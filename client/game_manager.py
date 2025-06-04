import pygame
from settings import GAP, TILE_SIZE, WINDOW_HEIGHT, WINDOW_WIDTH
from websocketclient import WebSocketClient
from scene_manager import SceneManager

from scenes.home_scene import HomeScene
from scenes.connect_scene import ConnectScene
from scenes.waiting_room_scene import WaitingRoomScene
from scenes.game_board_scene import GameBoardScene
from scenes.game_over_scene import GameOverScene

class Game:
    def __init__(self, width=1000, height=700):
        pygame.init()
        self.WIDTH, self.HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Dev Sea Adventure")
        self.clock = pygame.time.Clock()
        self.map_positions = [
            (50 + i * (TILE_SIZE + GAP), self.HEIGHT - 100 - i * (TILE_SIZE + GAP))
            for i in range(min(self.WIDTH, self.HEIGHT) // (TILE_SIZE + GAP))
        ]
        # Core components
        self.websocket_client = WebSocketClient()
        self.scene_manager = SceneManager()

        # Register scenes
        self.register_scenes()

        # Start at home screen
        self.scene_manager.set_scene("home")

        self.running = True

    def register_scenes(self):
        print("Registering scenes...")
        print("WebSocket client:", self.websocket_client)
        self.scene_manager.add_scene(
            "home", HomeScene(self.scene_manager, self.websocket_client)
        )
        self.scene_manager.add_scene(
            "connect", ConnectScene(self.scene_manager, self.websocket_client)
        )
        self.scene_manager.add_scene(
            "waiting", WaitingRoomScene(self.scene_manager, self.websocket_client)
        )
        self.scene_manager.add_scene(
            "main_scene", GameBoardScene(self.scene_manager, self.websocket_client)
        )
        self.scene_manager.add_scene(
            "game_over", GameOverScene(self.scene_manager, self.websocket_client)
        )

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.handle_event(event)

            self.scene_manager.update()
            self.scene_manager.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
