import socket
import threading
import json
from state import GameState


class GameClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.state = GameState()

    def connect(self, player_name):
        self.sock.connect((self.server_host, self.server_port))
        self.state.name = player_name
        self.sock.sendall(player_name.encode())
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def send_roll(self):
        self.sock.sendall(b"roll")

    def listen_to_server(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                message = json.loads(data.decode())
                if message["type"] == "state":
                    self.state.players = message["players"]
                    self.state.token_index = message["token_index"]
                elif message["type"] == "error":
                    print("[SERVER]:", message["message"])
            except:
                break
