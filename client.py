import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import logging
import argparse
import re

logging.basicConfig(
    filename="client.log",
    filemode="w",
    level=logging.DEBUG,
    format="| %(asctime)s | %(levelname)s | %(message)s |"
)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ip', required=True, help='Server IP address')
parser.add_argument('-p', '--port', type=int, required=True, help='Port number of the server')
args = parser.parse_args()

SERVER_HOST = args.ip
SERVER_PORT = args.port

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
logging.info("Connected to the server.")

gui = tk.Tk()
gui.title("Game Updates")

text_area = scrolledtext.ScrolledText(gui, wrap=tk.WORD, width=50, height=20)
text_area.pack(padx=10, pady=10)
text_area.config(state=tk.DISABLED)

turn_button = tk.Button(gui, text="Take Turn", command=lambda: announce_turn())
turn_button.pack(pady=5)

slap_button = tk.Button(gui, text="Slap Deck", command=lambda: slap_deck())
slap_button.pack(pady=5)
slap_button.config(state=tk.NORMAL)

shutdown_event = threading.Event()
player_turn = False
face_card_turn = False
cards_left_to_play = 0

def receive_messages():
    global player_turn, face_card_turn, cards_left_to_play
    while not shutdown_event.is_set():
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                logging.info("Connection closed by server.")
                break
            logging.info(f"Received: {message}")
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, message + '\n')
            text_area.config(state=tk.DISABLED)
            text_area.yview(tk.END)

            if "Your turn" in message and "face card rule" not in message:
                player_turn = True
                turn_button.config(state=tk.NORMAL) 
                logging.info("Player turn set to True")
            elif "Your turn to play a card due to face card rule" in message:
                face_card_turn = True
                turn_button.config(state=tk.NORMAL)
                logging.info("Face card turn set to True")
                if "card(s) left" in message:
                    match = re.search(r'You have (\d+) card\(s\) left', message)
                    if match:
                        cards_left_to_play = int(match.group(1)) - 1
            elif "Wait for your turn" in message:
                player_turn = False
                face_card_turn = False
                turn_button.config(state=tk.DISABLED) 
                logging.info("Player turn set to False")
            elif "Player" in message and "made a valid slap" in message:
                text_area.config(state=tk.NORMAL)
                text_area.insert(tk.END, message + '\n')
                text_area.config(state=tk.DISABLED)
                text_area.yview(tk.END)
            elif "shutdown" in message:
                shutdown_event.set()
                gui.quit()
        except (ConnectionResetError, OSError):
            logging.error("Connection lost.")
            break

def slap_deck():
    client_socket.send("slap deck".encode('utf-8'))
    logging.info("Deck slapped message sent to server.")

def announce_turn():
    global player_turn, face_card_turn, cards_left_to_play
    if player_turn:
        client_socket.send("turn taken".encode('utf-8'))
        player_turn = False
        turn_button.config(state=tk.DISABLED)  
        logging.info("Turn taken message sent to server.")
    elif face_card_turn:
        client_socket.send("face card turn taken".encode('utf-8'))
        logging.info("Face card turn taken message sent to server.")
        cards_left_to_play -= 1
        if cards_left_to_play > 0:
            turn_button.config(state=tk.NORMAL)
        else:
            face_card_turn = False
            turn_button.config(state=tk.DISABLED)
    else:
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, "It's not your turn. Please wait for your turn.\n")
        text_area.config(state=tk.DISABLED)
        text_area.yview(tk.END)
        logging.info("Player attempted to take turn out of sequence.")


def on_close():
    shutdown_event.set()
    client_socket.send("shutdown".encode('utf-8'))
    logging.info("Shutdown message sent to server.")
    client_socket.close()
    gui.quit()

gui.protocol("WM_DELETE_WINDOW", on_close)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

gui.mainloop()

client_socket.close()
logging.info("Client socket closed.")
