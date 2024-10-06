import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WarGameClient:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            logging.info(f"Connected to server at {self.host}:{self.port}")
            thread = threading.Thread(target=self.recieve_messages)
            thread.start()
            self.send_messages()
        except socket.error as e:
            logging.error(f"Failed to connect to server: {e}")

    def send_messages(self):
        try:
            while True:
                message = input("Message: ")
                self.client_socket.send(message.encode('utf-8'))
        except socket.error as e: 
            logging.error(f"Error sending message: {e}")
        finally:
            self.client_socket.close()

    def recieve_messages(self):
        try: 
            while True:
                message = self.client_socket.reciv(1024).decode('utf-8')
                if not message:
                    break
                logging.info(f"Received message: {message}")
        except socket.error as e:
            logging.error(f"Error receving message: {e}")
        finally: 
            self.client_socet.close()

if __name__ == "__main__":
    client = WarGameClient()
    client.connect_to_server()