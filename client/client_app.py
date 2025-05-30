# -------------------- client/client_app.py --------------------
import pygame
import asyncio
import threading
from network import WebSocketClient
from scenes.waiting_room import draw_waiting_room
from scenes.game_board import draw_game_board
from scenes.setup import *

clock = pygame.time.Clock()

websocket_client = WebSocketClient()
phase = "connect"  # connect -> waiting -> playing
player_name = ""


def on_players_update(players):
    pass  # sẽ xử lý ở phần vẽ UI nếu cần hiển thị thêm thông tin


def on_game_started():
    global phase
    phase = "playing"


def run_websocket(name):
    websocket_client.on_update_players = on_players_update
    websocket_client.on_game_started = on_game_started
    asyncio.run(websocket_client.connect(name))


def main():
    global phase, player_name
    pygame.init()
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
                elif phase == "waiting" and websocket_client.is_host:
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

        # Phase đồng bộ từ WebSocketClient
        if websocket_client.phase != phase:
            phase = websocket_client.phase

        if phase == "connect":
            txt_surface = font.render("Enter your name:", True, (0, 0, 0))
            screen.blit(txt_surface, (350, 250))
            pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
            name_surface = font.render(input_text, True, (0, 0, 0))
            screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))

        elif phase == "waiting":
            draw_waiting_room(
                screen,
                websocket_client.players,
                websocket_client.is_host,
                lambda: asyncio.run(websocket_client.send_start_game()),
            )

        elif phase == "playing":
            player_index = websocket_client.players.index(player_name)
            draw_game_board(screen, websocket_client, player_index, event)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
