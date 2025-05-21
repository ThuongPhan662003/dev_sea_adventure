import pygame

pygame.font.init()
font = pygame.font.Font("../assets/fonts/Roboto-Regular.ttf", 24)

MAP_POSITIONS = [
    (100, 300),
    (200, 250),
    (300, 200),
    (400, 200),
    (500, 250),
    (600, 300),
    (700, 350),
    (600, 400),
    (500, 450),
    (400, 400),
]


def draw_game(screen, state, message="", message_time=None):
    screen.fill((0, 105, 148))

    for i, pos in enumerate(MAP_POSITIONS):
        pygame.draw.circle(screen, (255, 255, 255), pos, 30)
        pygame.draw.circle(screen, (0, 0, 0), pos, 30, 2)
        text = font.render(str(i), True, (0, 0, 0))
        screen.blit(text, (pos[0] - 5, pos[1] - 10))

    for i, p in enumerate(state.players):
        pos = MAP_POSITIONS[p["position"]]
        pygame.draw.circle(screen, tuple(p["color"]), (pos[0], pos[1] - 40), 12)
        name_text = font.render(p["name"], True, tuple(p["color"]))
        screen.blit(name_text, (pos[0] - 30, pos[1] - 70))
        if i == state.token_index:
            pygame.draw.rect(screen, (255, 255, 0), (pos[0] - 15, pos[1] - 60, 30, 10))

    msg = (
        f"Lượt của: {state.players[state.token_index]['name']}"
        if state.players
        else "Đang chờ người chơi..."
    )
    info = font.render(msg, True, (0, 0, 0))
    screen.blit(info, (20, 520))

    # Thông báo lỗi nếu còn hiệu lực
    if message and message_time:
        if pygame.time.get_ticks() - message_time < 3000:
            notice = font.render(message, True, (255, 0, 0))
            screen.blit(notice, (20, 550))

    # Hiển thị bảng người chơi góc phải
    pygame.draw.rect(
        screen, (255, 255, 255), (800, 20, 180, 30 * len(state.players) + 10)
    )
    screen.blit(font.render("Người chơi:", True, (0, 0, 0)), (810, 25))
    for idx, player in enumerate(state.players):
        name = player["name"]
        color = tuple(player["color"])
        name_text = font.render(f"{name}", True, color)
        screen.blit(name_text, (810, 55 + idx * 25))


def draw_input_box(screen, box_rect, text, placeholder=""):
    color_active = pygame.Color("lightskyblue3")
    pygame.draw.rect(screen, color_active, box_rect, 2)
    txt_surface = font.render(text or placeholder, True, (0, 0, 0))
    screen.blit(txt_surface, (box_rect.x + 10, box_rect.y + 8))


def draw_button(screen, rect, text):
    pygame.draw.rect(screen, (100, 200, 100), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    txt_surface = font.render(text, True, (0, 0, 0))
    text_rect = txt_surface.get_rect(center=rect.center)
    screen.blit(txt_surface, text_rect)
