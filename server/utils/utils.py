import socket
import random


def get_local_ip():
    """Lấy địa chỉ IP nội bộ (IPv4) đang hoạt động."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Kết nối ảo ra ngoài để buộc hệ thống chọn interface phù hợp
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def create_game_map(length=15):
    """
    Tạo bản đồ game với các ô có thuộc tính index, score, is_collected.

    Parameters:
        length (int): Số lượng ô trong map.

    Returns:
        List[Dict]: Danh sách ô trong map.
    """
    game_map = []
    for index in range(length):
        tile = {
            "index": index,
            "x": 0,
            "y": 0,  # Vị trí có thể được tính toán sau
            "score": random.choice([0, 5, 10, 20]),  # hoặc theo luật game
            "is_collected": False,
        }
        game_map.append(tile)

    return game_map
