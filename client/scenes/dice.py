import random

import pygame


class Dice:
    def __init__(self, image_folder, sound_path, position):
        self.images = [
            pygame.transform.scale(
                pygame.image.load(f"{image_folder}/dice{i}.png").convert_alpha(),
                (60, 60),
            )
            for i in range(1, 7)
        ]
        self.sound = pygame.mixer.Sound(sound_path)
        self.position = position
        self.rect = pygame.Rect(position[0], position[1], 60, 60)
        self.value = 1  # giá trị đang hiển thị (trong khi quay)
        self.final_value = 1  # kết quả cuối cùng sau khi quay
        self.is_rolling = False
        self.roll_timer = 0
        self.roll_duration = 0.6
        self.roll_interval = 0.1

    def update(self, dt):
        if self.is_rolling:
            self.roll_timer += dt
            if self.roll_timer < self.roll_duration:
                if int(self.roll_timer / self.roll_interval) != int(
                    (self.roll_timer - dt) / self.roll_interval
                ):
                    self.value = random.randint(1, 6)
            else:
                self.is_rolling = False
                self.final_value = random.randint(1, 6)
                self.value = self.final_value  # chuyển sang hiển thị giá trị thật

    def draw(self, screen):
        image = self.images[self.value - 1]
        screen.blit(image, self.position)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.is_rolling = True
            self.roll_timer = 0
            self.sound.play()

    def get_value(self):
        return self.final_value
