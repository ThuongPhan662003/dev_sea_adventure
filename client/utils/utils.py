import math
import pygame
from scenes.components.tile import RockTile
from settings import COLORS, MAP_POSITIONS, PORT
import socket


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
    return f"{ip}:{PORT}"


def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, COLORS["gray"], rect)
    label = font.render(text, True, COLORS["white"])
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def create_zigzag_rock_map(
    tile_images,
    tile_sounds,
    tile_size,
    count,
    amplitude=100,
    frequency=0.4,
    base_y=500,
    gap=15,
    slope=25,
    left_margin=70,
):
    MAP_POSITIONS.clear()
    tiles = []

    step = tile_size + gap
    for i in range(count):
        x = i * step + left_margin  # Dịch sang phải
        y = base_y - i * slope + int(math.sin(i * frequency) * amplitude)

        score = 5 + i
        collected = False
        img = tile_images[i % len(tile_images)]
        snd = tile_sounds[i % len(tile_sounds)]

        MAP_POSITIONS.append({"x": x, "y": y, "score": score, "collected": collected})
        tiles.append(RockTile(img, x, y, tile_size, score, snd))

    return tiles
