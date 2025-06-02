import queue
import threading
import asyncio
import websockets
import json

from settings import PORT
from utils.utils import get_local_ip


class WebSocketClient:

    def __init__(self):
        self.uri = f"ws://192.168.1.37:5000/ws"
        self.players = []
        self.player_name = None
        self.is_host = False
        self.token_holder = None
        self.map_data = None
        self.phase = "connect"

        # Callback khi có cập nhật player hoặc game start
        self.on_update_players = None
        self.on_game_started = None

        self.websocket = None
        self.loop = asyncio.new_event_loop()  # event loop riêng cho thread
        self.running = False

        self.message_queue = queue.Queue()  # Queue message nhận được từ server
        self.current_position_index = 0  # Vị trí hiện tại của người chơi trên bản đồ
        self.map_state = []
        self.player_states = {}
        self.current_turn_index = 0

    def start(self, name):
        """Bắt đầu kết nối websocket trên luồng phụ"""
        self.player_name = name
        self.running = True
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_and_listen())

    async def _connect_and_listen(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                # Gửi join tên người chơi
                await websocket.send(
                    json.dumps({"type": "join", "name": self.player_name})
                )
                self.phase = "waiting"

                while self.running:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # Đưa message vào queue để luồng chính xử lý
                    self.message_queue.put(data)

                    # Nếu có callback, gọi ngay
                    if data["type"] == "join_accepted":
                        self.players = data["players"]
                        self.is_host = self.players[0] == self.player_name
                        if self.on_update_players:
                            self.on_update_players(self.players)

                    elif data["type"] == "waiting_room_update":
                        self.players = data["players"]
                        if self.on_update_players:
                            self.on_update_players(self.players)

                    elif data["type"] == "start":
                        self.map_data = data["map"]
                        # self.token_holder = data["current_turn"]

                        self.phase = "playing"
                        self.players = data["players"]
                        self.current_turn_index = 0
                        for player in self.players:
                            if player not in self.player_states:
                                self.player_states[player] = {
                                    "position_index": 0,
                                    "score": 0,
                                }

                        self.map_state = data["map"]
                        self.message_queue.put(
                            {
                                "type": "start",
                                "map": self.map_data,
                                "players": self.players,
                                "current_turn": data["current_turn"],
                            }
                        )

                    elif data["type"] == "token":
                        self.map_data = data["data"]

                    elif data["type"] == "turn_update":
                        sender = data.get("sender")
                        new_index = data.get("current_turn_index", 0)
                        # token_data = data.get("token_data", {})
                        # action_data = data.get("data", {})
                        # # self.send({"type": "liuliu"})
                        # if sender != self.player_name:
                        #     # Nếu là người chơi khác, đẩy vào queue để scene xử lý
                        # Cập nhật vị trí cho người chơi
                        # if sender in self.player_states:
                        #     self.player_states[sender]["position_index"] = new_index
                        self.message_queue.put(
                            {
                                "type": "external_action",
                                "sender": sender,
                                # "token_data": token_data,
                                # "data": action_data,
                                "current_turn": data.get("current_turn"),
                                "current_turn_index": data.get("current_turn_index", 0),
                            }
                        )
                    elif data["type"] == "your_turn":
                        # Nếu là lượt của người chơi này, có thể thực hiện hành động

                        print("[WebSocketClient] It's your turn!")
                        # self.send_dice(1)  # Gửi giá trị dice mặc định là 0
                        # self.message_queue.put(
                        #     {"type": "your_turn", "player": data.get("players")}
                        # )

        except websockets.exceptions.ConnectionClosed as e:
            print(
                f"[WebSocketClient] ❌ Kết nối bị đóng. Code: {e.code}, reason: {e.reason}"
            )
            self.running = False
        except Exception as e:
            print("[WebSocketClient] ❌ Lỗi không xác định:", e)
            self.running = False

    def send(self, message_dict):
        """Gửi message lên server từ luồng chính"""
        if self.websocket and self.running:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(message_dict)), self.loop
            )
        else:
            print("[WebSocketClient] Not connected or stopped, cannot send message.")

    def get_message_nowait(self):
        """Lấy message mới nhất từ server, không chặn luồng"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        """Dừng kết nối và event loop"""
        self.running = False
        self.loop.call_soon_threadsafe(self.loop.stop)

    # Optional: Hàm gửi start game (có thể gọi từ luồng chính)
    def send_start_game(self):
        self.send({"type": "start_game"})

    def send_dice(self, dice_value):
        self.send(
            {"type": "role_dice", "total": dice_value, "sender": self.player_name}
        )

    # Optional: Gửi hành động game
    def send_action(self, token_data, action_data):
        self.send(
            {
                "type": "action",
                "sender": self.player_name,
                "token_data": token_data,
                "data": action_data,
            }
        )

    def get_player_position(self, name):
        return self.player_states.get(name, {}).get("position_index")

    def get_player_score(self, name):
        return self.player_states.get(name, {}).get("score")

    def get_map_tile(self, index):
        return self.map_state[index] if 0 <= index < len(self.map_state) else None
