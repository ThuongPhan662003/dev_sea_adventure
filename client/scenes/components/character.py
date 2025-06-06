import pygame
import os


class Character:
    def __init__(self, name, folder_path, position, sound_path=None, channel_index=0, label_image_path=None):
        self.name = name
        self.position = list(position)
        self.frames = []
        self.load_frames(folder_path)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.speed = 150  # pixel/second

        # Load label image nếu có đường dẫn truyền vào
        if label_image_path:
            self.label_image = pygame.image.load(label_image_path).convert_alpha()
            self.label_image = pygame.transform.scale(self.label_image, (48, 48))
        else:
            self.label_image = None

        self.sound = pygame.mixer.Sound(sound_path) if sound_path else None
        self.channel = pygame.mixer.Channel(channel_index) if sound_path else None
        self.has_moved = False

        self.step_index = 0
        self.step_path = []
        self.step_delay = 0.5  # giây giữa các bước
        self.step_timer = 0

    def load_frames(self, folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                image = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                image = pygame.transform.scale(image, (48, 48))
                self.frames.append(image)

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        if self.step_path:
            self.step_timer += dt
            if self.step_timer >= self.step_delay:
                target_pos = self.step_path[self.step_index]
                self.position = list(target_pos)
                self.step_index += 1
                self.step_timer = 0
                if self.step_index >= len(self.step_path):
                    self.step_path = []
                    self.step_index = 0

    def draw(self, screen, font):
        # Vẽ sprite hiện tại
        screen.blit(self.frames[self.current_frame], self.position)

        # Vẽ tên hoặc hình label (ngôi sao)
        name_x = self.position[0]
        name_y = self.position[1] - 50  # vị trí dưới chân nhân vật

        if self.label_image:
            label_rect = self.label_image.get_rect(center=(name_x + 24, name_y + 24))
            screen.blit(self.label_image, label_rect)
        else:
            name_surface = font.render(self.name, True, (255, 255, 255))
            screen.blit(name_surface, (name_x, name_y))

    def move(self, direction, dt):
        old_pos = self.position[:]
        if direction == "left":
            self.position[0] -= self.speed * dt
        elif direction == "right":
            self.position[0] += self.speed * dt
        elif direction == "up":
            self.position[1] -= self.speed * dt
        elif direction == "down":
            self.position[1] += self.speed * dt

        self.has_moved = self.position != old_pos

    def play_sound_if_moved(self):
        if self.sound and self.channel:
            if self.has_moved:
                if not self.channel.get_busy():
                    self.channel.play(self.sound, loops=-1)
            else:
                self.channel.stop()

    def set_steps(self, positions, delay=0.5):
        """
        Thiết lập các bước đi qua với độ trễ giữa mỗi bước.
        """
        self.step_path = positions
        self.step_index = 0
        self.step_delay = delay
        self.step_timer = 0
