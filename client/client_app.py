# client/client_app.py
import pygame
import asyncio
import threading
from network import WebSocketClient
from scenes.waiting_room import draw_waiting_room
from scenes.game_board import draw_game_board

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dev Sea Adventure")
clock = pygame.time.Clock()

phase = "connect"  # connect -> waiting -> playing
player_name = ""
is_host = False
websocket_client = WebSocketClient()


def run_websocket(name):
    asyncio.run(websocket_client.connect(name))


def start_game_callback():
    asyncio.run(websocket_client.send_start_game())


def main():
    global phase, player_name, is_host
    pygame.init()
    font = pygame.font.SysFont(None, 36)
    input_box = pygame.Rect(350, 300, 300, 40)
    input_active = False
    input_text = ""

    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if phase == "connect":
                    if input_box.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
                elif phase == "waiting" and is_host:
                    if 800 <= event.pos[0] <= 900 and 600 <= event.pos[1] <= 650:
                        asyncio.run(websocket_client.send_start_game())
            elif event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    player_name = input_text
                    threading.Thread(
                        target=run_websocket, args=(player_name,), daemon=True
                    ).start()
                    input_text = ""
                    phase = "waiting"
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        is_host = websocket_client.is_host

        if phase == "connect":
            txt_surface = font.render("Enter your name:", True, (0, 0, 0))
            screen.blit(txt_surface, (350, 250))
            pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
            name_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
        elif phase == "waiting":
            if phase == "playing":
                phase = "playing"
            draw_waiting_room(
                screen,
                websocket_client.players,
                websocket_client.is_host,
                start_game_callback,
            )

        elif phase == "playing":
            draw_game_board(
                screen, websocket_client.map_data, websocket_client.current_turn
            )

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
