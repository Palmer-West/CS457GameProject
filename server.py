import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WarGameServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server started on {self.host}:{self.port}, waiting for connections...")

        # main running loop
        while True:
            client_socket, client_address = self.server_socet.accept()
            logging.info(f"Client connected from {client_address}")
            self.clients.append(client_socket)

            thread = threading.Thread(target=self.handle_client, args=(client_socket,))

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                logging.info(f"Received message: {message}", client_socket)
                self.broadcast_message(f"Message from client {client_address}: {message}, client_socket")
        except ConnectionResetError:
            logging.error(f"Client: {client_address} disconnected unexpectedly")
        finally:
            logging.info(f"Client: {client_address} disconnected")
            self.clients.remove(client_socket)
            client_socket.close()

    def broadcast_message(self, message, source_client):
        for client in self.clients:
            if client != source_client:
                try:
                    client.send(message.encode('utf-8'))
                except socket.error as e:
                    logging.error(f"Failed to send message to client: {client_address}: {e}")

    def stop_server(self):
        for client in self.clients:
            client.close()
        self.server_socket.close()
        logging.info("Server stopped")   


if __name__ == "__main__":
    server = WarGameServer()
    server.start_server()     