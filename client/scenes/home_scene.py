import pygame

from settings import BUTTON_HEIGHT, BUTTON_WIDTH
from .base_scene import BaseScene


class HomeScene(BaseScene):
    def __init__(self, manager, websocket_client):
        super().__init__()  # Gọi BaseScene để lấy WIDTH, HEIGHT, background, music
        self.manager = manager
        self.client = websocket_client
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)

        self.join_button = pygame.Rect(
            (self.WIDTH - BUTTON_WIDTH) // 2,
            self.HEIGHT // 2 - 50 // 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

        self.create_button = pygame.Rect(
            (self.WIDTH - BUTTON_WIDTH) // 2,
            self.HEIGHT // 2 + 50 // 2 + BUTTON_HEIGHT,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

    def draw_button(self, screen, rect, text):
        pygame.draw.rect(screen, (70, 130, 180), rect, border_radius=12)
        label = self.button_font.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.join_button.collidepoint(event.pos):
                self.client.is_host = False
                self.manager.set_scene("main_scene")
            elif self.create_button.collidepoint(event.pos):
                self.client.is_host = True
                self.manager.set_scene("connect")

    def update(self):
        pass

    def draw(self, screen):
        # Vẽ background trước
        screen.blit(self.background, (0, 0))

        # Vẽ tiêu đề
        title = self.font.render("Dev Sea Adventure", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))

        # Vẽ các nút
        self.draw_button(screen, self.join_button, "Join Room")
        self.draw_button(screen, self.create_button, "Create Room")
