import pygame
from network import GameClient
from scene import draw_game, draw_input_box, draw_button


def start_client():
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font("../assets/fonts/Roboto-Regular.ttf", 24)

    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Dev Sea - Connect")
    clock = pygame.time.Clock()

    input_boxes = {
        "name": pygame.Rect(350, 200, 300, 40),
        "ip": pygame.Rect(350, 260, 300, 40),
    }
    connect_button = pygame.Rect(420, 320, 160, 40)
    text_data = {"name": "", "ip": ""}
    active_box = None

    connecting = False

    while not connecting:
        screen.fill((200, 230, 255))
        title = font.render(
            "Nhập tên người chơi và địa chỉ IP server:", True, (0, 0, 0)
        )
        screen.blit(title, (300, 150))

        draw_input_box(screen, input_boxes["name"], text_data["name"], "Tên của bạn")
        draw_input_box(
            screen, input_boxes["ip"], text_data["ip"], "IP phòng (vd: 192.168.1.100)"
        )
        draw_button(screen, connect_button, "KẾT NỐI")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, box in input_boxes.items():
                    if box.collidepoint(event.pos):
                        active_box = key
                if connect_button.collidepoint(event.pos):
                    if text_data["name"] and text_data["ip"]:
                        print(f"[CLIENT] Kết nối tới IP: {text_data['ip']}")
                        connecting = True
            elif event.type == pygame.KEYDOWN and active_box:
                if event.key == pygame.K_BACKSPACE:
                    text_data[active_box] = text_data[active_box][:-1]
                else:
                    text_data[active_box] += event.unicode

        pygame.display.flip()
        clock.tick(30)

    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Dev Sea - Playing")
    client = GameClient(server_host=text_data["ip"], server_port=5000)
    client.connect(text_data["name"])

    message = ""
    message_time = 0
    last_token_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if client.state.players and client.state.token_index < len(
                    client.state.players
                ):
                    current = client.state.players[client.state.token_index]
                    if current["name"] == client.state.name:
                        client.send_roll()
                        message = ""
                        last_token_time = now
                    else:
                        message = "Không phải lượt của bạn!"
                        message_time = now

        # Nếu giữ token quá 5 giây mà không hành động → tự động chuyển lượt
        if client.state.players and client.state.token_index < len(
            client.state.players
        ):
            current = client.state.players[client.state.token_index]
            if current["name"] == client.state.name:
                if now - last_token_time > 5000:
                    print("[CLIENT] Token hết thời gian - chuyển lượt")
                    client.send_roll()
                    message = "Tự động chuyển lượt (quá 5 giây)"
                    message_time = now
                    last_token_time = now

        draw_game(screen, client.state, message, message_time)
        pygame.display.flip()
        clock.tick(60)
