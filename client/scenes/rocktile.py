import math
import sys
import pygame


class RockTile:
    def __init__(self, source_image, x, y, tile_size, score=10, click_sound=None):
        self.source_image = source_image
        self.image = source_image.copy()
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.collected = False
        self.tile_size = tile_size
        self.score = score
        self.click_sound = click_sound
        self.stop_sound_event = pygame.USEREVENT + x  # Mỗi tile có event riêng

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        icon_path = "treasure/open.png" if self.collected else "treasure/close.png"
        treasure_icon = pygame.image.load(icon_path).convert_alpha()
        treasure_icon = pygame.transform.scale(treasure_icon, (30, 30))
        screen.blit(treasure_icon, (self.rect.right - 20, self.rect.top - 30))

        if self.collected:
            temp_img = self.image.copy()
            temp_img.set_alpha(100)
            screen.blit(temp_img, self.rect.topleft)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos) and not self.collected:
            self.collected = True
            if self.click_sound:
                self.click_sound.play()
                # Đặt hẹn giờ để dừng sau 1 giây (1000ms)
                pygame.time.set_timer(self.stop_sound_event, 1000, loops=1)
            print(f"Đã lấy kho báu, điểm cộng: {self.score}")
            return True
        return False

    def handle_event(self, event):
        if event.type == self.stop_sound_event and self.click_sound:
            self.click_sound.stop()


def create_sine_rock_map(
    tile_images, tile_sounds, tile_size, count, amplitude, frequency, offset_y, gap
):
    tiles = []
    step = tile_size + gap
    for i in range(count):
        x = i * step
        y = offset_y + int(math.sin(i * frequency) * amplitude)
        score = 5 + i

        # Lấy image và sound theo index (mod để tránh lỗi)
        img = tile_images[i % len(tile_images)]
        snd = tile_sounds[i % len(tile_sounds)]

        tiles.append(RockTile(img, x, y, tile_size, score, snd))
    return tiles


def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    pygame.display.set_caption("Sine Wave Rock Tile Map with Sounds")

    clock = pygame.time.Clock()

    tile_size = 50

    # Load nhiều ảnh tile khác nhau (ví dụ 3 tile)
    tile_images = [
        pygame.transform.scale(
            pygame.image.load(f"output_tiles/tile_0_{i}.png").convert_alpha(),
            (tile_size, tile_size),
        )
        for i in range(3)
    ]

    # Load nhiều âm thanh khác nhau (ví dụ 3 sound)
    tile_sounds = [pygame.mixer.Sound(f"output_tiles/music_{i}.wav") for i in range(3)]

    rock_tiles = create_sine_rock_map(
        tile_images,
        tile_sounds,
        tile_size,
        count=20,
        amplitude=80,
        frequency=0.5,
        offset_y=screen_height // 2,
        gap=20,
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for tile in rock_tiles:
                    if tile.handle_click(pos):
                        break
            else:
                for tile in rock_tiles:
                    tile.handle_event(event)

        screen.fill((135, 206, 235))

        for tile in rock_tiles:
            tile.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
