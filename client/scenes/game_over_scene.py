import queue
import pygame
from .base_scene import BaseScene


class GameOverScene(BaseScene):
    def __init__(self, manager, websocket_client, winner_name=None):
        super().__init__()
        self.manager = manager
        self.client = websocket_client
        self.winner_name = winner_name
        self.font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 36)
        # self.screen_width = 1200
        # self.screen_height = 800

        # self.background = pygame.Surface((self.screen_width, self.screen_height))
        self.background.fill((0, 0, 50))

    def on_enter(self):
        print(f"Game Over! Winner: {self.winner_name}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:

                import os, sys

                os.execv(sys.executable, ["python"] + sys.argv)
                # self.manager.set_scene("home")

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Hiển thị thông báo game over
        text_surface = self.font.render("Game Over!", True, (255, 255, 0))
        screen.blit(
            text_surface,
            ((self.WIDTH - text_surface.get_width()) // 2, 200),
        )

        if self.winner_name:
            winner_text = f"Winner: {self.winner_name}"
            winner_surface = self.small_font.render(winner_text, True, (255, 255, 255))
            screen.blit(
                winner_surface,
                ((self.WIDTH - winner_surface.get_width()) // 2, 300),
            )

        info_text = "Press Enter to return to Home"
        info_surface = self.small_font.render(info_text, True, (180, 180, 180))
        screen.blit(
            info_surface,
            ((self.WIDTH - info_surface.get_width()) // 2, 400),
        )
