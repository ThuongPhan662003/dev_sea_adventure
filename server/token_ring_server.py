# Giả định bạn đang dùng FastAPI + WebSocket
# server/token_ring_server.py

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from .database import get_session
from .models import Player, Map, SourceCode
import json, random

router = APIRouter()

clients = []
players = []  # Danh sách người chơi (tên)
player_ws_map = {}  # ánh xạ tên -> websocket
current_turn_index = 0  # Token ring


async def broadcast(message: dict):
    disconnected = []
    for client in clients:
        try:
            await client.send_text(json.dumps(message))
        except:
            disconnected.append(client)
    for client in disconnected:
        clients.remove(client)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "join":
                name = message["name"]
                if name not in players:
                    players.append(name)
                    player_ws_map[name] = websocket
                    with get_session() as session:
                        player = Player(player_name=name)
                        session.add(player)
                        session.commit()
                await websocket.send_text(
                    json.dumps({"type": "join_accepted", "players": players})
                )
                await broadcast({"type": "waiting_room_update", "players": players})

            elif message["type"] == "start_game" and websocket == clients[0]:
                # Người đầu tiên là host -> bắt đầu game
                map_data = generate_random_map()
                await broadcast(
                    {
                        "type": "start",
                        "players": players,
                        "map": map_data,
                        "current_turn": players[0],  # Người đầu tiên đi
                    }
                )

            elif message["type"] == "action":
                # Nhận action từ player -> xử lý và gửi cho toàn bộ
                await broadcast({"type": "player_action", "data": message["data"]})
                advance_turn()
                await broadcast(
                    {"type": "turn_update", "current_turn": players[current_turn_index]}
                )

    except WebSocketDisconnect:
        clients.remove(websocket)


def generate_random_map():
    """Sinh bản đồ mẫu gồm source code ở random vị trí"""
    positions = [(x, y) for x in range(5) for y in range(5)]
    random.shuffle(positions)
    sources = [{"id": i, "pos": pos} for i, pos in enumerate(positions[:5])]
    return {"size": [5, 5], "sources": sources}


def advance_turn():
    global current_turn_index
    current_turn_index = (current_turn_index + 1) % len(players)
