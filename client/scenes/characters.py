import pygame
import os
import math
import sys


# ==== Lớp Nhân Vật (Character) ====
class Character:
    def __init__(self, name, folder_path, position, sound_path=None, channel_index=0):
        self.name = name
        self.position = list(position)
        self.frames = []
        self.load_frames(folder_path)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.speed = 150  # pixel/second

        self.sound = pygame.mixer.Sound(sound_path) if sound_path else None
        self.channel = pygame.mixer.Channel(channel_index) if sound_path else None
        self.has_moved = False

    def load_frames(self, folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                image = pygame.image.load(
                    os.path.join(folder_path, filename)
                ).convert_alpha()
                image = pygame.transform.scale(image, (48, 48))
                self.frames.append(image)

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen, font):
        frame = self.frames[self.current_frame]
        x, y = self.position
        screen.blit(frame, (x, y))
        label = font.render(self.name, True, (0, 0, 0))
        screen.blit(label, (x - 10, y - 25))

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


# ==== Hàm vẽ game board ====
def draw_game_board(screen, characters, source_codes):
    font = pygame.font.SysFont("Arial", 20)
    screen.fill((173, 216, 230))  # Nền

    wave_amplitude = 80
    step_x = 60

    for item in source_codes:
        pos = item.get("position", 0)
        score = item.get("score", None)
        offset_y = int(math.sin(pos * math.pi / 5) * wave_amplitude)
        center_x = pos * step_x + 100
        center_y = screen.get_height() // 2 + offset_y
        pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 15)
        screen.blit(
            font.render(f"SC {score}", True, (0, 0, 0)), (center_x - 15, center_y - 25)
        )

    pygame.draw.rect(screen, (50, 50, 50), (50, screen.get_height() // 2 - 15, 40, 30))
    screen.blit(
        font.render("Server", True, (255, 255, 255)),
        (30, screen.get_height() // 2 + 25),
    )

    for character in characters:
        character.update(1 / 60)
        character.draw(screen, font)


# ==== Tạo bản đồ mẫu ====
def generate_sample_map():
    return [{"position": i, "score": (i % 5 + 1)} for i in range(20)]


def draw_sine_map(
    screen,
    tile_color=(100, 200, 100),
    tile_size=40,
    amplitude=80,
    frequency=0.2,
    offset_x=0,
    offset_y=300,
    count=30,
    gap=10,
):
    """
    Vẽ các khối dạng sóng sin với khoảng cách giữa chúng.

    Args:
        screen: màn hình pygame để vẽ.
        tile_color: màu khối vuông (RGB).
        tile_size: kích thước mỗi khối vuông.
        amplitude: biên độ sóng.
        frequency: tần số sóng.
        offset_x: vị trí bắt đầu trục x.
        offset_y: trục giữa chiều cao (dọc).
        count: số khối.
        gap: khoảng cách giữa các khối (theo trục x).
    """
    step = tile_size + gap
    for i in range(count):
        x = offset_x + i * step
        y = offset_y + int(math.sin(i * frequency) * amplitude)
        pygame.draw.rect(
            screen, tile_color, (x, y, tile_size, tile_size), border_radius=5
        )


# ==== Hàm chính ====
def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(10)

    screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
    pygame.display.set_caption("Dev Sea Adventure")
    clock = pygame.time.Clock()

    # === Tạo các nhân vật ===
    characters = [
        Character(
            "Alice",
            "../assets/characters/bat",
            (150, 300),
            "../assets/sounds/impact.ogg",
            channel_index=0,
        ),
        Character(
            "Bob",
            "../assets/characters/blob",
            (150, 300),
            "../assets/sounds/music.wav",
            channel_index=1,
        ),
        Character(
            "Jame",
            "../assets/characters/skeleton",
            (150, 300),
            "../assets/sounds/shoot.wav",
            channel_index=2,
        ),
    ]

    active_character = characters[1]  # Nhân vật điều khiển

    # source_codes = generate_sample_map()
    draw_sine_map(
        screen,
        tile_color=(139, 69, 19),  # Màu nâu đất
        tile_size=40,
        amplitude=60,
        frequency=0.3,
        offset_x=50,
        offset_y=screen.get_height() // 2 + 100,
        count=25,
    )
    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            active_character.move("left", dt)
        elif keys[pygame.K_RIGHT]:
            active_character.move("right", dt)
        elif keys[pygame.K_UP]:
            active_character.move("up", dt)
        elif keys[pygame.K_DOWN]:
            active_character.move("down", dt)
        else:
            active_character.has_moved = False  # Reset khi không nhấn gì

        active_character.play_sound_if_moved()

        # draw_game_board(screen, characters, source_codes)
        draw_sine_map(
            screen,
            tile_color=(139, 69, 19),  # Màu nâu đất
            tile_size=40,
            amplitude=60,
            frequency=0.3,
            offset_x=50,
            offset_y=screen.get_height() // 2 + 100,
            count=25,
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
