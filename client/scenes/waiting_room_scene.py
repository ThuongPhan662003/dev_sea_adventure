import asyncio
import threading
import pygame

from settings import BUTTON_HEIGHT, BUTTON_WIDTH, COLORS
from .base_scene import BaseScene


class WaitingRoomScene(BaseScene):
    def __init__(self, manager, websocket_client):
        super().__init__()  # Gọi BaseScene để lấy WIDTH, HEIGHT, background, music
        self.manager = manager
        self.client = websocket_client
        self.on_game_started = self.on_game_started
        # self.font = pygame.font.SysFont(None, 36)
        self.button_font = pygame.font.SysFont("./assets/fonts/Roboto-Regular.ttf", 28)
        self.start_button = pygame.Rect(
            (self.WIDTH - BUTTON_WIDTH) // 2,
            self.HEIGHT // 2 - 50 // 2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

    def on_enter(self):
        print("Entered waiting room.")
        print("WebSocket client:", self.client.websocket)

    def on_game_started(self):
        self.manager.set_scene("main_scene")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.client.is_host:
            if self.start_button.collidepoint(event.pos):
                # threading.Thread(
                #     target=lambda: asyncio.run(self.client.send_start_game()),
                #     daemon=True,
                # ).start()
                self.client.send_start_game()
                self.manager.set_scene("main_scene")

    def update(self):
        # Kiểm tra xem có tin nhắn nào mới từ server không
        message = self.client.get_message_nowait()
        while message:
            # while True:
            print(f"[WaitingRoomScene] Received message: {message}")
            if message["type"] == "start":
                # while True:
                #     print("message", message)
                self.client.map_state = message.get("map")
                self.client.token_holder = message.get("current_turn")

                self.client.phase = "playing"
                self.client.players = message["players"]

                self.client.current_turn_index = 0
                self.on_game_started()
            message = self.client.get_message_nowait()

    def draw(self, screen):
        # Vẽ background trước
        screen.blit(self.background, (0, 0))

        # Tiêu đề
        title_font = pygame.font.SysFont(None, 72)  # font lớn hơn
        title = title_font.render("Waiting Room", True, COLORS["white"])
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))

        # Danh sách người chơi
        for idx, name in enumerate(self.client.players):
            player_text = self.font.render(f"{idx + 1}. {name}", True, COLORS["black"])
            screen.blit(player_text, (100, 150 + idx * 40))

        # Nút Start nếu là host, canh giữa màn hình
        if self.client.is_host:
            # Cập nhật vị trí nút ở giữa màn hình
            self.start_button.centerx = screen.get_width() // 2
            self.start_button.y = screen.get_height() - 100

            # Hiệu ứng hover đổi màu
            mouse_pos = pygame.mouse.get_pos()
            if self.start_button.collidepoint(mouse_pos):
                color = COLORS["blue"]  # xanh dương khi hover
            else:
                color = COLORS["dark_blue"]  # màu nút mặc định

            pygame.draw.rect(screen, color, self.start_button, border_radius=12)
            label = self.button_font.render("Start", True, COLORS["white"])
            label_rect = label.get_rect(center=self.start_button.center)
            screen.blit(label, label_rect)
