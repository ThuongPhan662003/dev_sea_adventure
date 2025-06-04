import asyncio
import pygame
import threading

from settings import BUTTON_HEIGHT, BUTTON_WIDTH, COLORS
from .base_scene import BaseScene


class ConnectScene(BaseScene):
    def __init__(self, manager, websocket_client):
        super().__init__()  # Gọi BaseScene để lấy WIDTH, HEIGHT, background, music
        self.manager = manager
        self.client = websocket_client
        self.font = pygame.font.SysFont(None, 36)
        # self.input_box = pygame.Rect(350, 300, 300, 40)
        # Background mặc định (nếu cần)
        self.raw_background = pygame.image.load(
            "./assets/background/connect_room.png"
        ).convert()
        self.background = pygame.transform.scale(
            self.raw_background, (self.WIDTH, self.HEIGHT)
        )
        self.input_box = pygame.Rect(
            (self.WIDTH - BUTTON_WIDTH) // 2,
            self.HEIGHT // 2 - 50 // 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )
        self.input_box_color = COLORS["white"]
        self.input_active = False
        self.input_text = ""

    def on_enter(self):
        print("Entered connect scene.")
        print("WebSocket client:", self.client.websocket)
        self.input_text = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.input_active = self.input_box.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                name = self.input_text.strip()
                if name:
                    print(f"Connecting with name: {name}")

                    print(
                        f"[ConnectScene] Starting client with name: {name},{self.client.players}"
                    )
                    self.client.start(name)
                    self.manager.set_scene("waiting")
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    def update(self):
        pass
        # # Kiểm tra xem có tin nhắn nào mới từ server không
        # message = self.client.get_message_nowait()
        # while message:
        #     # while True:
        #     print(f"[WaitingRoomScene] Received message: {message}")
        #     if message["type"] == "game_resync":
        #         self.manager.set_scene("main_scene")
        #     message = self.client.get_message_nowait()

    def draw(self, screen):
        # Vẽ background trước
        screen.blit(self.background, (0, 0))

        # Vẽ tiêu đề
        title = self.font.render("Enter your name:", True, (0, 0, 0))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))
        # Tô nền input box
        pygame.draw.rect(screen, self.input_box_color, self.input_box)

        if self.input_active:
            bg_color = COLORS["gray"]  # Màu nền khi active, ví dụ "light_gray"
            border_color = COLORS["blue"]  # Màu viền khi active
        else:
            bg_color = COLORS["white"]  # Màu nền khi không active
            border_color = COLORS["gray"]  # Màu viền bình thường

        # Tô nền input box
        pygame.draw.rect(screen, bg_color, self.input_box)

        # Vẽ viền input box
        pygame.draw.rect(screen, border_color, self.input_box, 2)

        # Vẽ text bên trong input box
        screen.blit(
            self.font.render(self.input_text, True, (0, 0, 0)),
            (self.input_box.x + 5, self.input_box.y + 5),
        )
