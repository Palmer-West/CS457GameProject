import socket
import pydealer
import logging
import select
import random

logging.basicConfig(
    filename="server.log",
    filemode="w",
    level=logging.DEBUG,
    format="| %(asctime)s | %(levelname)s | %(message)s |"
)

HOST = '127.0.0.1'
PORT = 5555

deck = pydealer.Deck()
player_hands = {}
clients = []
pile = []
turn = None

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
server_socket.setblocking(False)
logging.info(f"Server listening on {HOST}:{PORT}")
print("Waiting for clients to connect...")

def broadcast_message(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
            logging.info(f"Broadcasted: {message}")
        except (BrokenPipeError, OSError):
            logging.error("Failed to send message to a client.")

def handle_client_disconnect(client):
    if client in clients:
        clients.remove(client)
        client.close()
    logging.info(f"Client {client.getpeername()} disconnected.")

def game_setup():
    global turn
    deck.shuffle()
    hand_size = 52 // len(clients)
    for i, client in enumerate(clients):
        player_hands[client] = deck.deal(hand_size)
        client.send(f"You are Player {i + 1}. Game is starting...".encode('utf-8'))
    logging.info("Hands dealt to all players.")
    turn = random.choice(clients)
    turn.send("Game starting. You go first. Your turn".encode('utf-8'))
    for client in clients:
        if client != turn:
            client.send("Game starting. Wait for your turn.".encode('utf-8'))
    logging.info("Game has started.")

try:
    while True:
        readable, _, _ = select.select([server_socket] + clients, [], [], 1)
        for s in readable:
            if s is server_socket:
                # Accept new connection
                client_socket, client_address = server_socket.accept()
                clients.append(client_socket)
                client_socket.setblocking(False)
                logging.info(f"Client {client_address} connected.")
                if len(clients) == 2:
                    game_setup()
            else:
                try:
                    message = s.recv(1024).decode('utf-8')
                    if not message:
                        handle_client_disconnect(s)
                        continue
                    logging.info(f"Received from {s.getpeername()}: {message}")
                    if message.lower() == "turn taken":
                        card = player_hands[s].deal(1)
                        pile.extend(card)
                        logging.info(f"Card {card} added to the pile from Player {clients.index(s) + 1}.")
                        broadcast_message(f"Pile: {[str(c) for c in pile]}")
                        # Switch turn
                        turn = clients[(clients.index(s) + 1) % len(clients)]
                        turn.send("Your turn.".encode('utf-8'))
                        for client in clients:
                            if client != turn:
                                client.send("Wait for your turn.".encode('utf-8'))
                    elif message.lower() == "shutdown":
                        logging.info(f"Shutdown requested by {s.getpeername()}.")
                        broadcast_message("shutdown")
                        raise KeyboardInterrupt
                except (ConnectionResetError, OSError):
                    handle_client_disconnect(s)
except KeyboardInterrupt:
    logging.info("Server shutting down.")
    for client in clients:
        client.close()
    server_socket.close()
    logging.info("Server socket closed.")
