# client/scenes/game_board.py
import pygame


def draw_game_board(screen, websocket_client):
    font = pygame.font.SysFont(None, 30)
    screen.fill((173, 216, 230))

    # Vẽ bản đồ
    map_data = websocket_client.map_data
    if map_data:
        for item in map_data.get("source_codes", []):
            x = item.get("x", 0)
            y = item.get("y", 0)
            pygame.draw.circle(screen, (255, 215, 0), (x, y), 10)
            screen.blit(font.render("SC", True, (0, 0, 0)), (x - 10, y - 25))

        for idx, player in enumerate(websocket_client.players):
            pygame.draw.rect(screen, (0, 128, 0), (100 + idx * 100, 600, 40, 40))
            screen.blit(
                font.render(player, True, (255, 255, 255)), (100 + idx * 100, 650)
            )
