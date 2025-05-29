import pygame
from .ui_elements import draw_button

# Màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 215)

# Button Rect
start_button = pygame.Rect(400, 550, 200, 50)


def draw_waiting_room(screen, players, is_host, start_callback):
    font = pygame.font.SysFont(None, 36)

    screen.fill(WHITE)

    # Tiêu đề
    title = font.render("Waiting Room", True, BLACK)
    screen.blit(title, (400, 50))

    # Danh sách người chơi
    for idx, name in enumerate(players):
        player_text = font.render(f"{idx + 1}. {name}", True, BLACK)
        screen.blit(player_text, (100, 150 + idx * 40))

    # Nếu là host thì hiện nút Start
    if is_host:
        draw_button(screen, start_button, "BẮT ĐẦU")

        # Kiểm tra nếu click vào nút
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        if start_button.collidepoint(mouse_pos) and mouse_click[0]:
            start_callback()
