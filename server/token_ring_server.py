from asyncio import create_task, sleep
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database import get_session
from models import Player
import json
from datetime import datetime
from utils.utils import create_game_map

router = APIRouter()

# ==== TRẠNG THÁI GAME ====
clients: list[WebSocket] = []
players: list[str] = []
player_ws_map: dict[str, WebSocket] = {}
current_turn_index: int = 0
map_data: dict = {}
current_game_id: int = 1
player_ids: dict[str, int] = {}

current_turn_name: str | None = None
token_start_time: datetime | None = None
current_turn_ws: WebSocket | None = None
token_timeout_task = None


# ==== RESET GAME STATE ====
def reset_game_state():
    global players, player_ws_map, player_ids, current_turn_index
    global map_data, current_turn_name, token_start_time, current_turn_ws
    global token_timeout_task, clients

    print("✅ Đang reset toàn bộ trạng thái server...")
    players.clear()
    player_ws_map.clear()
    player_ids.clear()
    current_turn_index = 0
    map_data = {}
    current_turn_name = None
    token_start_time = None
    current_turn_ws = None
    if token_timeout_task and not token_timeout_task.done():
        token_timeout_task.cancel()
    token_timeout_task = None
    clients.clear()


# ==== HÀM XỬ LÝ ====
async def send_to_next_player_from_to(websocket_from: WebSocket, message: dict):
    sender_name = get_player_name_by_ws(websocket_from)
    if sender_name is None or sender_name not in players:
        print("Người gửi không xác định hoặc đã rời game.")
        return

    current_index = players.index(sender_name)
    next_index = (current_index + 1) % len(players)
    next_player = players[next_index]
    websocket_to = player_ws_map.get(next_player)
    print("Người nhận:", next_player)

    if websocket_to:
        try:
            await websocket_to.send_text(json.dumps(message))
        except Exception as e:
            print(f"Lỗi khi gửi tới {next_player}: {e}")
            if websocket_to in clients:
                clients.remove(websocket_to)
            player_ws_map.pop(next_player, None)
            players.remove(next_player)


def get_player_name_by_ws(ws: WebSocket):
    for name, sock in player_ws_map.items():
        if sock == ws:
            return name
    return None


async def broadcast_token_ring(websocket_from: WebSocket, message: dict):
    sender_name = get_player_name_by_ws(websocket_from)
    if sender_name is None:
        return

    current_name = sender_name
    current_ws = websocket_from

    for _ in range(len(players)):
        await send_to_next_player_from_to(current_ws, message)
        next_index = (players.index(current_name) + 1) % len(players)
        current_name = players[next_index]
        current_ws = player_ws_map[current_name]
        if current_name not in players:
            print(f"{current_name} đã bị ngắt kết nối, dừng vòng.")
            return

    if len(clients) == 1:
        await send_to_next_player_from_to(current_ws, message)
    print("Kết thúc gửi vòng token")


async def send_to(ws: WebSocket, message: dict):
    try:
        await ws.send_text(json.dumps(message))
    except:
        if ws in clients:
            clients.remove(ws)


def current_turn():
    if players:
        return players[current_turn_index]
    return None


def advance_turn():
    global current_turn_index
    if players:
        current_turn_index = (current_turn_index + 1) % len(players)


def remove_client(ws: WebSocket):
    if ws in clients:
        clients.remove(ws)
    for name, sock in list(player_ws_map.items()):
        if sock == ws:
            players.remove(name)
            player_ws_map.pop(name, None)
            player_ids.pop(name, None)
            break

    if not clients:
        print("⚠️ Không còn người chơi nào. Reset server state.")
        reset_game_state()


async def handle_join(name: str, websocket: WebSocket):
    if name not in players:
        players.append(name)
        player_ws_map[name] = websocket
        clients.append(websocket)

        with get_session() as session:
            session.add(Player(player_name=name))
            session.commit()

    await send_to(websocket, {"type": "join_accepted", "players": players})
    await broadcast_token_ring(websocket, {"type": "waiting_room_update", "players": players})


async def handle_start_game(websocket: WebSocket):
    global current_turn_name, token_start_time, current_turn_ws, map_data

    if not players:
        return

    current_turn_name = players[0]
    token_start_time = datetime.utcnow()
    current_turn_ws = player_ws_map[current_turn_name]
    map_data = create_game_map()

    await broadcast_token_ring(
        current_turn_ws,
        {
            "type": "start",
            "players": players,
            "map": map_data,
            "current_turn": current_turn(),
        },
    )

    await start_token_timeout(current_turn_ws, current_turn_name)


async def handle_action(name: str, data: dict, websocket: WebSocket):
    await broadcast_token_ring(
        websocket,
        {
            "type": "turn_update",
            "sender": name,
            "current_turn": name,
            "current_turn_index": data,
        },
    )


async def handle_next_token(websocket: WebSocket, message: dict):
    advance_turn()
    next_player = current_turn()
    next_ws = player_ws_map.get(next_player)

    if not next_ws:
        print(f"Không tìm thấy WebSocket cho {next_player}")
        return

    await broadcast_token_ring(
        next_ws,
        {
            "type": "next_token_oke",
            "current_turn": next_player,
            "players": players,
            "start_time": datetime.utcnow().isoformat(),
        },
    )
    global current_turn_name, token_start_time, current_turn_ws
    current_turn_name = next_player
    token_start_time = datetime.utcnow()
    current_turn_ws = next_ws
    await start_token_timeout(current_turn_ws, current_turn_name)

async def handle_game_over(websocket: WebSocket, message: dict):
    global token_timeout_task

    winner = message.get("winner")
    if not winner:
        print("Không có người chiến thắng.")
        return

    # Gửi thông báo kết thúc đến tất cả clients
    await broadcast_token_ring(
        websocket,
        {
            "type": "end_game",
            "winner": winner,
            "players": players,
        },
    )

    # Cho client thời gian nhận message
    await asyncio.sleep(1)

    # Xóa từng client bằng remove_client
    for ws in list(clients):  # copy để tránh thay đổi trong khi lặp
        remove_client(ws)
        # try:
        #     await ws.close()
        # except:
        #     pass  # trong trường hợp client đã tự ngắt

    # Hủy task timeout nếu còn
    if token_timeout_task and not token_timeout_task.done():
        token_timeout_task.cancel()

    # # Reset tất cả state
    # reset_game_state()
    # print("✅ Trò chơi kết thúc. Server đã reset.")



def get_token_elapsed_seconds():
    if token_start_time:
        return int((datetime.utcnow() - token_start_time).total_seconds())
    return 0


async def start_token_timeout(ws: WebSocket, player_name: str):
    global current_turn_name, token_start_time, current_turn_ws, token_timeout_task

    current_turn_name = player_name
    token_start_time = datetime.utcnow()
    current_turn_ws = ws

    if token_timeout_task and not token_timeout_task.done():
        token_timeout_task.cancel()

    async def timeout_handler():
        await sleep(10)
        print(f"[TIMEOUT] {player_name} đã giữ token quá 10s.")
        await handle_next_token(ws, {"type": "auto_next_due_to_timeout"})

    token_timeout_task = create_task(timeout_handler())


# ==== ENDPOINT WEBSOCKET ====

@router.websocket("/ws")
async def websocket_game(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        print("Client connected:", websocket.client)
        print("Current players:", players)
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"Received message: {message}")

            if message["type"] == "join":
                await handle_join(message["name"], websocket)

            elif message["type"] == "start_game":
                await handle_start_game(websocket)

            elif message["type"] == "action":
                await handle_action(
                    message["sender"], message["token_data"]["position"], websocket
                )

            elif message["type"] == "next_token":
                await handle_next_token(websocket, message)

            elif message["type"] == "game_over":
                await handle_game_over(websocket, message)

    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        print("Client disconnected.")
        remove_client(websocket)
        await broadcast_token_ring(
            websocket, {"type": "player_disconnected", "players": players}
        )
