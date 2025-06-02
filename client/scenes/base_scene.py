import pygame

from settings import WINDOW_HEIGHT, WINDOW_WIDTH


class BaseScene:
    def __init__(self):
        self.WIDTH = WINDOW_WIDTH
        self.HEIGHT = WINDOW_HEIGHT

        # Background mặc định (nếu cần)
        self.raw_background = pygame.image.load("./assets/background/bg2.png").convert()
        self.background = pygame.transform.scale(
            self.raw_background, (self.WIDTH, self.HEIGHT)
        )
        self.font = pygame.font.SysFont("./assets/fonts/Roboto-Regular.ttf", 24)

        # Âm thanh nền mặc định (tuỳ bạn)
        # self.background_music = pygame.mixer.Sound(
        #     "./assets/character_sounds/menu_music.wav"
        # )
        # self.background_music.set_volume(0.5)  # Tuỳ chỉnh âm lượng
        # self.background_music.play(-1)  # Lặp vô hạn

    def on_enter(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))  # Dùng nền mặc định
