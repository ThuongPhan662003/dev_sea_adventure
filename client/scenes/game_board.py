import pygame
import math


def draw_game_board(screen, websocket_client):
    font = pygame.font.SysFont(None, 30)
    screen.fill((173, 216, 230))  # Nền biển

    map_data = websocket_client.map_data
    # print("Map data:", map_data)
    wave_amplitude = 80  # biên độ sóng lên xuống
    step_x = 60  # khoảng cách giữa các ô theo chiều ngang

    if map_data:
        for item in map_data.get("source_codes", []):
            position = item.get("position", 0)
            score = item.get("score", None)
            collected = item.get("collected", False)

            # Bỏ qua nếu không phải Source Code (không có score)
            if score is None:
                continue

            # Tính vị trí lượn sóng theo chiều ngang
            offset_y = int(math.sin(position * math.pi / 5) * wave_amplitude)
            center_x = position * step_x + 100
            center_y = screen.get_height() // 2 + offset_y

            # Màu sắc và nhãn
            if collected:
                color = (160, 160, 160)  # Đã lấy - xám
                label = "✓"
            else:
                color = (255, 215, 0)  # Chưa lấy - vàng
                label = f"SC {score}"

            # Vẽ vòng tròn
            pygame.draw.circle(screen, color, (center_x, center_y), 15)
            screen.blit(
                font.render(label, True, (0, 0, 0)), (center_x - 15, center_y - 25)
            )
            

        # Vẽ tàu ngầm ở đầu bản đồ (bên trái)
        pygame.draw.rect(
            screen, (50, 50, 50), (50, screen.get_height() // 2 - 15, 40, 30)
        )
        screen.blit(
            font.render("Server", True, (255, 255, 255)),
            (30, screen.get_height() // 2 + 25),
        )

    # Vẽ người chơi ở dưới bản đồ
    for idx, player in enumerate(websocket_client.players):
        pygame.draw.rect(screen, (0, 128, 0), (100 + idx * 100, 650, 40, 40))
        screen.blit(
            font.render(player, True, (255, 255, 255)), (100 + idx * 100 - 10, 695)
        )
