import pygame
from websocketclient import WebSocketClient
from scene_manager import SceneManager

from scenes.connect_scene import ConnectScene
from scenes.waiting_room_scene import WaitingRoomScene
from scenes.game_board_scene import GameBoardScene
from scenes.home_scene import HomeScene

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dev Sea Adventure")
clock = pygame.time.Clock()


def main():
    pygame.init()

    websocket_client = WebSocketClient()
    manager = SceneManager()

    # Đăng ký scene
    manager.add_scene("connect", ConnectScene(manager, websocket_client))
    manager.add_scene("waiting", WaitingRoomScene(manager, websocket_client))
    manager.add_scene("playing", GameBoardScene(manager, websocket_client))
    # Đăng ký thêm HomeScene
    manager.add_scene("home", HomeScene(manager, websocket_client))
    # Bắt đầu ở màn connect
    # manager.set_scene("connect")
    manager.set_scene("home")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update()
        manager.draw(screen)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
