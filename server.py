import socket
import pydealer
from pydealer.const import BOTTOM
import logging
import select
import random
import argparse

logging.basicConfig(
    filename="server.log",
    filemode="w",
    level=logging.DEBUG,
    format="| %(asctime)s | %(levelname)s | %(message)s |"
)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, required=True, help='Port number for the server')
args = parser.parse_args()

HOST = '127.0.0.1'
PORT = args.port

war_ranks = {
    "Ace": 13,
    "King": 12,
    "Queen": 11,
    "Jack": 10,
    "10": 9,
    "9": 8,
    "8": 7,
    "7": 6,
    "6": 5,
    "5": 4,
    "4": 3,
    "3": 2,
    "2": 1
}

deck = pydealer.Deck(ranks=war_ranks)
player_hands = {}
clients = []
pile = []
turn = None
rules = ['double', 'sandwitch']

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(2)
server_socket.setblocking(False)
logging.info(f"Server listening on {HOST}:{PORT}")
print("Waiting for clients to connect...")

def is_valid_slap():
    if pile.count == 0:
        return False
    if 'double' in rules and len(pile) >= 2:
        temp_pile = list(pile)
        first_card = temp_pile.pop()
        second_card = temp_pile.pop()
        if first_card.eq(second_card, war_ranks):
            return True
    if 'sandwitch' in rules and len(pile) >= 3:
        temp_pile = list(pile)
        first_card = temp_pile.pop()
        temp_pile.pop()
        third_card = temp_pile.pop()
        if first_card.eq(third_card, war_ranks):
            return True
    else:
        return False

def is_face_card(card):
    return card.value in ['Jack', "Queen", "King", "Ace"]

def face_card_count(card):
    if card.value == "Jack":
        return 1
    if card.value == "Queen":
        return 2
    if card.value == "King":
        return 3
    if card.value == "Ace":
        return 4
    return 0

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
    current_face_card = None
    cards_to_play = 0

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
                        #check if player hand is empty
                        if len(player_hands[s]) == 0:
                            winning_player = [c for c in clients if c != s][0]
                            losing_player = s

                            winning_player.send("Congradulations! You have won the game!".encode('utf-8'))
                            losing_player.send("You have lost the game. Better luck next time!".encode('utf-8'))

                            logging.info(f"Player {clients.index(winning_player) + 1} has won the game.")

                            for client in clients:
                                client.close()
                            server_socket.close()
                            logging.info("Server socket closed after game over.")
                            exit()

                        card = player_hands[s].deal(1)
                        pile.extend(card)
                        logging.info(f"Card {card} added to the pile from Player {clients.index(s) + 1}.")
                        broadcast_message(f"Pile: {[str(c) for c in pile]}")

                        if is_face_card(card[0]):
                            current_face_card = card[0]
                            cards_to_play = face_card_count(current_face_card)
                            logging.info(f"Face card {current_face_card} played. Next player must play {cards_to_play} card(s).")

                            turn = clients[(clients.index(s) + 1) % len(clients)]
                            turn.send("Your turn to play a card due to face card rule. Click 'Take Turn' to play each card.".encode('utf-8'))
                            broadcast_message(f"Player {clients.index(turn) + 1} must play {cards_to_play} card(s) due to face card rule.")
                        
                        else:
                            turn = clients[(clients.index(s) + 1) % len(clients)]
                            turn.send("Your turn.".encode('utf-8'))
                            for client in clients:
                                if client != turn:
                                    client.send("Wait for your turn.".encode('utf-8'))
                    

                    elif message.lower() == "face card turn taken":
                        if cards_to_play > 0:
                            card = player_hands[s].deal(1)
                            pile.extend(card)
                            cards_to_play -= 1
                            logging.info(f"Card {card} added to pile from Player {clients.index(s) + 1} during face card round.")
                            broadcast_message(f"Pile: {[str(c) for c in pile]} | {cards_to_play} card(s) left to play.")

                            if len(player_hands[s]) == 0:
                                #winning condition
                                winning_player = [c for c in clients if c != s][0]
                                losing_player = s

                                winning_player.send("Congradulations! You have won the game!".encode('utf-8'))
                                losing_player.send("You have lost the game. Better luck next time!".encode('utf-8'))

                                logging.info(f"Player {clients.index(winning_player) + 1} has won the game.")

                                for client in clients:
                                    client.close()
                                server_socket.close()
                                logging.info("Server socket closed after game over.")
                                exit()

                            if cards_to_play > 0:
                                s.send(f"Your turn to play a card due to face card rule. You have {cards_to_play} card(s) left.".encode('utf-8'))
                            else:
                                initiating_player = clients[(clients.index(s) - 1) % len(clients)]
                                player_hands[initiating_player].add(pile, end=BOTTOM)
                                pile.clear()
                                broadcast_message(f"Player {clients.index(initiating_player) + 1} takes the pile after face card round.")
                                current_face_card = None
                                turn = clients[(clients.index(initiating_player) + 1) % len(clients)]
                                turn.send("Your turn.".encode('utf-8'))
                                for client in clients:
                                    if client != turn:
                                        client.send("Wait for your turn".encode('utf-8'))
                            
                    elif message.lower() == "slap deck":
                        if is_valid_slap():
                            player_hands[s].add(pile, end=BOTTOM)
                            pile.clear()

                            broadcast_message(f"Player {clients.index(s) + 1} made a valid slap. The pile is now empty.")
                            s.send(f"Your hand has been updated. You now have {len(player_hands[s])} cards.".encode('utf-8'))

                            for client in clients:
                                if client != s:
                                    client.send(f"Player {clients.index(s) + 1} made a valid slap and took the pile.".encode('utf-8'))

                            logging.info(f"Player {clients.index(s) + 1} made a valid slap and took the pile.")
                            current_face_card = None
                            cards_to_play = 0

                        else:
                            s.send("Invalid slap.".encode("utf-8"))
                            logging.info(f"Player {clients.index(s) + 1} attempted an invalid slap.")

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
