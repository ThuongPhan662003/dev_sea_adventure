from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database import get_session
from models import Player
import json

from utils.utils import create_game_map

router = APIRouter()

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
    global players, player_ws_map, clients
    # print("player_ws_map:", player_ws_map)
    # print("players:", players)
    # print("clients:", clients)
    sender_name = None
    for name, ws in player_ws_map.items():
        # print(f"Checking player: {name}, WebSocket: {ws}")
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
    print("người nhận", next_player)

    if websocket_to:
        try:
            await websocket_to.send_text(json.dumps(message))
        except Exception as e:
            print("danh sách người chơi", players)
            print(f"Lỗi khi gửi tới người kế tiếp: {next_player} - {e}")
            if websocket_to in clients:
                clients.remove(websocket_to)
            if next_player in player_ws_map:
                del player_ws_map[next_player]
            if next_player in players:
                players.remove(next_player)


def get_player_name_by_ws(ws: WebSocket):
    global player_ws_map
    for name, sock in player_ws_map.items():
        if sock == ws:
            return name
    return None


async def broadcast_token_ring(websocket_from: WebSocket, message: dict):
    global players, player_ws_map, clients
    print("->>>>bắt đầu gửi theo vòng", message)

    # if not players or len(players) < 2:
    #     return

    sender_name = get_player_name_by_ws(websocket_from)
    if sender_name is None:
        print("Người gửi không xác định.")
        return

    current_name = sender_name
    current_ws = websocket_from
    print(f"Người gửi hiện tại: {current_name}, WebSocket: {current_ws}")
    for _ in range(len(players)):
        print(f"action-  Đang gửi từ: {current_name}")
        print("bí mat", message)
        # if message["current_turn"] != current_name:
        await send_to_next_player_from_to(current_ws, message)

        # Lấy người kế tiếp trong danh sách vòng
        next_index = (players.index(current_name) + 1) % len(players)
        current_name = players[next_index]
        current_ws = player_ws_map[current_name]
        # Nếu người nhận bị loại trong quá trình gửi, dừng vòng luôn
        print("người chơi và danh sách", current_name, players)
        if current_name not in players:
            print(f"[broadcast] {current_name} đã bị ngắt kết nối, dừng vòng.")
            return
        
    if len(clients) == 1:
        await send_to_next_player_from_to(current_ws, message)
        print(f"[broadcast] Chỉ còn {current_name} trong game, dừng vòng.")
    print("->>>>Kết thúc gửi theo vòng")


async def send_to(ws: WebSocket, message: dict):
    global clients
    try:
        await ws.send_text(json.dumps(message))
    except:
        if ws in clients:
            clients.remove(ws)


def current_turn():
    global current_turn_index, players
    if players:
        return players[current_turn_index]
    return None


def advance_turn():
    global current_turn_index
    if players:
        current_turn_index = (current_turn_index + 1) % len(players)


def remove_client(ws: WebSocket):
    global clients, players, player_ws_map, current_turn_index, map_data, player_ids

    if ws in clients:
        clients.remove(ws)

    for name, sock in list(player_ws_map.items()):
        if sock == ws:
            players.remove(name)
            del player_ws_map[name]
            if name in player_ids:
                del player_ids[name]
            break

    # ✅ Nếu không còn client nào → reset toàn bộ server state
    if not clients:
        print("⚠️ Không còn người chơi nào. Reset server state.")
        players.clear()
        player_ws_map.clear()
        player_ids.clear()
        current_turn_index = 0
        map_data = {}



async def handle_join(name: str, websocket: WebSocket):
    global players, player_ws_map, clients
    # Nếu người chơi chưa tồn tại, thêm vào danh sách
    if name not in players:
        players.append(name)
        player_ws_map[name] = websocket
        clients.append(websocket)

        # Lưu người chơi mới vào cơ sở dữ liệu
        with get_session() as session:
            session.add(Player(player_name=name))
            session.commit()
    # print(f"Player {name} joined. Current players: {players}")
    # Gửi phản hồi riêng cho client đã join
    await send_to(websocket, {"type": "join_accepted", "players": players})

    # Gửi cập nhật danh sách phòng chờ đến tất cả client khác
    await broadcast_token_ring(
        websocket, {"type": "waiting_room_update", "players": players}
    )


async def handle_start_game(websocket: WebSocket):
    global players, player_ws_map, current_turn_index, map_data
    if not players:
        print("Không có người chơi để bắt đầu game.")
        return

    map_data = create_game_map()  # nếu có bản đồ
    print("Bản đồ game đã được tạo:", map_data)
    # Lấy WebSocket của người đầu tiên (host)
    host_name = players[0]
    host_ws = player_ws_map.get(host_name)

    if not host_ws:
        print(f"Không tìm thấy WebSocket cho host: {host_name}")
        return
    
    # Gửi theo vòng bắt đầu từ người host
    await broadcast_token_ring(
        host_ws,
        {
            "type": "start",
            "players": players,
            "map": map_data,
            "current_turn": current_turn(),
        },
    )


async def handle_action(name: str, data: dict, websocket: WebSocket):
    global players, player_ws_map, current_turn_index, map_data
    # if name != current_turn():
    #     await send_to(
    #         websocket, {"type": "error", "message": "Không phải lượt của bạn!"}
    #     )
    #     return

    # Gửi thông tin cập nhật theo Token Ring
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
    global players, current_turn_index, player_ws_map

    # Tính người kế tiếp
    advance_turn()
    next_player = current_turn()
    next_ws = player_ws_map.get(next_player)

    if not next_ws:
        print(f"[handle_next_token] Không tìm thấy WebSocket cho {next_player}")
        return

    # Gửi thông tin cập nhật theo Token Ring
    await broadcast_token_ring(
        next_ws,
        {
            "type": "next_token_oke",
            "current_turn": next_player,
            "players": players,
        },
    )
    print(f"[handle_next_token] Đã gửi thông tin đến {next_player}.")


# ==== ENDPOINT WEBSOCKET ====


@router.websocket("/ws")
async def websocket_game(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"Received message: {message}")
            if message["type"] == "join":
                print(f"Player {message['name']} is trying to join.")
                await handle_join(message["name"], websocket)

            elif message["type"] == "start_game":
                await handle_start_game(websocket)
            elif message["type"] == "action":
                print(f"Player {message['sender']} is taking an action.")
                await handle_action(
                    message["sender"], message["token_data"]["position"], websocket
                )
            elif message["type"] == "role_dice":
                print("Handling dice roll...", message)
                # print(f"Player {message['type']} rolled dice: {message['total']}")
            elif message["type"] == "next_token":
                await handle_next_token(websocket, message)

    except WebSocketDisconnect:
        print("Client disconnected.")
        remove_client(websocket)
        await broadcast_token_ring(
            websocket, {"type": "player_disconnected", "players": players}
        )

