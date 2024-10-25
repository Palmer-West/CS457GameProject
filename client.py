import socket
import threading
import queue
import logging

logging.basicConfig(
    filename="client.log",
    filemode="w",
    level=logging.DEBUG,
    format="| %(asctime)s | %(levelname)s | %(message)s |"
)

# Define the server host and port to connect to
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

# Queue for communication between the listener and display threads
message_queue = queue.Queue()

# Handle receiving messages from the server and pass them to the display thread
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                logging.info("Connection closed by server.")
                break
            message_queue.put(message)
        except ConnectionResetError:
            logging.exception("Connection closed by server.")
            break

# Game display thread that prints game information from the queue
def display_game():
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            logging.info(f"Game Update: {message}")

# Main function to start the client
if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Start a thread to listen for incoming messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Start a thread to display game information from the queue
    display_thread = threading.Thread(target=display_game)
    display_thread.start()

    try:
        while True:
            message = input("You: ")
            if message.lower() == 'quit':
                print("Sending disconnect message and closing connection.")
                client_socket.send(message.encode('utf-8'))
                client_socket.close()
                break
            client_socket.send(message.encode('utf-8'))

    except KeyboardInterrupt:
        logging.exception("Client exiting...")

    finally:
        # Ensure both threads exit cleanly
        receive_thread.join()
        display_thread.join()
        client_socket.close()
