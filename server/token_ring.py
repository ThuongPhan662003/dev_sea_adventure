import socket
import threading
import json


class TokenRingServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.players = []
        self.token_index = 0
        self.lock = threading.Lock()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"[SERVER] Listening on {self.host}:{self.port}...")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def broadcast_game_state(self):
        state = {
            "type": "state",
            "players": self.players,
            "token_index": self.token_index,
        }
        data = json.dumps(state).encode()
        for client in self.clients:
            try:
                client.sendall(data)
            except:
                continue

    def handle_client(self, conn, addr):
        with conn:
            print(f"[CONNECTED] {addr}")
            self.clients.append(conn)
            name = conn.recv(1024).decode()
            color = (
                [255, 0, 0]
                if len(self.players) == 0
                else [0, 255, 0] if len(self.players) == 1 else [0, 0, 255]
            )
            with self.lock:
                self.players.append({"name": name, "position": 0, "color": color})
                self.broadcast_game_state()

            while True:
                try:
                    data = conn.recv(1024).decode()
                    if not data:
                        break

                    if data == "roll":
                        with self.lock:
                            if self.clients[self.token_index] == conn:
                                import random

                                dice = random.randint(1, 3) + random.randint(1, 3)
                                self.players[self.token_index]["position"] = (
                                    self.players[self.token_index]["position"] + dice
                                ) % 10
                                self.token_index = (self.token_index + 1) % len(
                                    self.players
                                )
                                self.broadcast_game_state()
                            else:
                                conn.sendall(
                                    json.dumps(
                                        {"type": "error", "message": "Not your turn"}
                                    ).encode()
                                )
                except:
                    break

            print(f"[DISCONNECTED] {addr}")
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
