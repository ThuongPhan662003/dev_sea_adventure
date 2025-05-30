# -------------------- client/network.py --------------------
import websockets
import asyncio
import json


class WebSocketClient:
    def __init__(self):
        self.uri = "ws://192.168.1.27:5000/ws"
        self.players = []
        self.is_host = False
        self.token_holder = None
        self.map_data = None
        self.on_update_players = None
        self.on_game_started = None
        self.phase = "connect"
        self.websocket = None

    async def connect(self, name):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            await websocket.send(json.dumps({"type": "join", "name": name}))
            self.phase = "waiting"

            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data["type"] == "join_accepted":
                    self.players = data["players"]
                    self.is_host = self.players[0] == name
                    if self.on_update_players:
                        self.on_update_players(self.players)

                elif data["type"] == "waiting_room_update":
                    self.players = data["players"]
                    if self.on_update_players:
                        self.on_update_players(self.players)

                elif data["type"] == "start":
                    self.map_data = data["map"]
                    self.token_holder = data["current_turn"]
                    self.phase = "playing"
                    if self.on_game_started:
                        self.on_game_started()

    async def send_start_game(self):
        async with websockets.connect(self.uri) as websocket:
            await websocket.send(json.dumps({"type": "start_game"}))
            print("Start game request sent.")
            response = await websocket.recv()
            data = json.loads(response)
            print("Game started:", data)
            if data["type"] == "start":
                self.map_data = data["map"]  # Lưu map để vẽ sau
                self.token_holder = data["current_turn"]
                self.phase = "playing"
                self.current_turn = data["current_turn"]
                self.players = data["players"]
