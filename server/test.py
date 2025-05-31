from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database import get_session
from models import Player
import json

game_router = APIRouter()

# ==== TRẠNG THÁI GAME ====
clients: list[WebSocket] = []
players: list[str] = []  # Tên người chơi
player_ws_map: dict[str, WebSocket] = {}
current_turn_index: int = 0
map_data: dict = {}
current_game_id: int = 1  # giả sử bạn đã tạo game trong DB và lấy id
player_ids: dict[str, int] = {}  # ánh xạ name -> player_id


# ==== HÀM XỬ LÝ ====
async def send_to_next_player_from_to(websocket_from: WebSocket, message: dict):
    sender_name = None
    for name, ws in player_ws_map.items():
        if ws == websocket_from:
            sender_name = name
            break

    if sender_name is None or sender_name not in players:
        print("Người gửi không xác định hoặc đã rời game.")
        return

    current_index = players.index(sender_name)
    next_index = (current_index + 1) % len(players)
    next_player = players[next_index]
    websocket_to = player_ws_map.get(next_player)

    if websocket_to:
        try:
            await websocket_to.send_text(json.dumps(message))
        except:
            print(f"Lỗi khi gửi tới người kế tiếp: {next_player}")
            if websocket_to in clients:
                clients.remove(websocket_to)


def get_player_name_by_ws(ws: WebSocket):
    for name, sock in player_ws_map.items():
        if sock == ws:
            return name
    return None


async def broadcast_token_ring(websocket_from: WebSocket, message: dict):
    if not players or len(players) < 2:
        return

    sender_name = get_player_name_by_ws(websocket_from)
    if sender_name is None:
        print("Người gửi không xác định.")
        return

    current_ws = websocket_from
    for _ in range(len(players)):
        await send_to_next_player_from_to(current_ws, message)
        current_name = get_player_name_by_ws(current_ws)
        next_index = (players.index(current_name) + 1) % len(players)
        current_ws = player_ws_map[players[next_index]]


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
            del player_ws_map[name]
            break


async def handle_join(name: str, websocket: WebSocket):
    # Nếu người chơi chưa tồn tại, thêm vào danh sách
    if name not in players:
        players.append(name)
        player_ws_map[name] = websocket
        clients.append(websocket)

        # Lưu người chơi mới vào cơ sở dữ liệu
        with get_session() as session:
            session.add(Player(player_name=name))
            session.commit()

    # Gửi phản hồi riêng cho client đã join
    await send_to(websocket, {"type": "join_accepted", "players": players})

    # Gửi cập nhật danh sách phòng chờ đến tất cả client khác
    await broadcast_token_ring(
        websocket, {"type": "waiting_room_update", "players": players}
    )


async def handle_start_game(websocket: WebSocket):
    global map_data
    # map_data = generate_random_map()

    # Gửi theo vòng bắt đầu từ người host
    await broadcast_token_ring(
        websocket,
        {
            "type": "start",
            "players": players,
            "map": map_data,
            "current_turn": current_turn(),
        },
    )


async def handle_action(name: str, data: dict, websocket: WebSocket):
    if name != current_turn():
        await send_to(
            websocket, {"type": "error", "message": "Không phải lượt của bạn!"}
        )
        return

    # Cập nhật vị trí mới nếu có
    new_position = data.get("new_position")
    if new_position is not None:
        player_positions[name] = new_position

    # Lưu lại người vừa thực hiện (websocket hiện tại) để truyền theo vòng
    current_player_position = player_positions.get(name)

    # Chuyển lượt
    advance_turn()
    next_player = current_turn()
    next_player_id = player_ids.get(next_player)

    # Gửi thông tin cập nhật theo Token Ring
    await broadcast_token_ring(
        websocket,
        {
            "type": "turn_update",
            "map": map_data,
            "player_positions": player_positions,
            "updated_player": {"name": name, "new_position": current_player_position},
            "next_player": {"name": next_player, "id": next_player_id},
        },
    )


# ==== ENDPOINT WEBSOCKET ====


@game_router.websocket("/ws")
async def websocket_game(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "join":
                await handle_join(message["name"], websocket)

            elif message["type"] == "start_game":
                await handle_start_game()

            elif message["type"] == "action":
                await handle_action(message["name"], message["data"], websocket)

    except WebSocketDisconnect:
        remove_client(websocket)
        await broadcast({"type": "player_disconnected", "players": players})
