import socket
import threading
import queue
import pydealer

# Define the host and port to listen on
HOST = '127.0.0.1'
PORT = 5555

# Game state variables
deck = None
playerHands = []
numClients = 0
clients = []

# Queue to handle communication between the game thread and the server
messageIn_queue = queue.Queue()
messageOut_queue = queue.Queue()

def game_setup():
    deck = pydealer.Deck()
    # TODO: handle uneven hand sizes, say for 3 clients
    if 52 % len(clients) == 0:
        handSize = int(52 / len(clients))
        print(f"Hand size: {handSize}")
    for i in range(len(clients)):
        playerHands.append(deck.deal(handSize))
        messageOut_queue.put(f"Hand: {clients[i]}:{playerHands[i]}")
        print(f"Hands of size {handSize} delt to {len(clients)} players")
    

# Placeholder game logic (can be replaced with a card game implementation)
def game_thread():
    print("Game thread started.")
    while True:
        if not messageIn_queue.empty():
            message = messageIn_queue.get()
            if message == "shutdown":
                print("Game thread shutting down.")
                break
            elif "New client:" in message:
                #numClients += 1
                clients.append(message[11:])
                
            elif message == "start":
                print("Game setup started...")
                game_setup()
                

            print(f"Game processing message: {message}")
            response = f"Processed: {message}"
            messageOut_queue.put(response)

# Handle individual client connections
def handle_client(client_socket, client_address):
    print(f"Client {client_address} connected.")
    messageIn_queue.put(f"New client: {client_address}")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message or message.lower() == 'quit':
                print(f"Client {client_address} disconnected.")
                break
            print(f"Received from {client_address}: {message}")
            messageIn_queue.put(message)

            # Get the game response and send it back to the client
            if not messageOut_queue.empty():    
                response = messageOut_queue.get()
                client_socket.send(response.encode('utf-8'))

    except ConnectionResetError:
        print(f"Connection with {client_address} was lost.")
    finally:
        client_socket.close()

# TCP server logic to manage multiple connections
def server_thread():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Allow up to 5 connections
    print(f"Server listening on {HOST}:{PORT}")

    client_threads = []

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_threads.append(client_handler)
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        # Shut down all client connections gracefully
        for client_thread in client_threads:
            client_thread.join()
        server_socket.close()

# Main server start function
if __name__ == "__main__":
    server = threading.Thread(target=server_thread)
    server.start()

    game = threading.Thread(target=game_thread)
    game.start()

    try:
        server.join()
        game.join()
    except KeyboardInterrupt:
        print("Server and game threads shutting down.")
        messageIn_queue.put("shutdown")
