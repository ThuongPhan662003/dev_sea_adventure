import pygame
import sys
import math
import random
from tile import RockTile
from character import Character
from dice import Dice

# Biến toàn cục chứa tất cả vị trí bước
MAP_POSITIONS = []


def create_sine_rock_map(
    tile_images, tile_sounds, tile_size, count, amplitude, frequency, offset_y, gap
):
    global MAP_POSITIONS
    tiles = []
    step = tile_size + gap
    MAP_POSITIONS = []
    for i in range(count):
        x = i * step
        y = offset_y + int(math.sin(i * frequency) * amplitude)
        MAP_POSITIONS.append((x, y))
        score = 5 + i
        img = tile_images[i % len(tile_images)]
        snd = tile_sounds[i % len(tile_sounds)]
        tiles.append(RockTile(img, x, y, tile_size, score, snd))
    return tiles


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(10)

    screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
    pygame.display.set_caption("Dev Sea Adventure")
    clock = pygame.time.Clock()

    tile_size = 50

    tile_images = [
        pygame.transform.scale(
            pygame.image.load(f"output_tiles/tile_0_{i}.png").convert_alpha(),
            (tile_size, tile_size),
        )
        for i in range(3)
    ]

    tile_sounds = [pygame.mixer.Sound(f"output_tiles/music_{i}.wav") for i in range(3)]

    rock_tiles = create_sine_rock_map(
        tile_images,
        tile_sounds,
        tile_size,
        count=20,
        amplitude=80,
        frequency=0.5,
        offset_y=screen.get_height() // 2,
        gap=20,
    )

    characters = [
        Character(
            "Alice", "assets/characters/bat", (150, 300), "assets/sounds/impact.ogg", 0
        ),
        Character(
            "Bob", "assets/characters/blob", (150, 300), "assets/sounds/music.wav", 1
        ),
        Character(
            "Jame",
            "assets/characters/skeleton",
            (150, 300),
            "assets/sounds/shoot.wav",
            2,
        ),
    ]
    active_character = characters[1]
    current_position_index = 0  # vị trí hiện tại trong MAP_POSITIONS

    dice = Dice("dices", "dices/dice_sound.wav", (1000, 90))

    font = pygame.font.SysFont("Arial", 20)
    button_rect = pygame.Rect(1000, 30, 150, 40)

    running = True
    # Trong game loop:
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    step_count = dice.get_value()
                    end_index = min(
                        current_position_index + step_count, len(MAP_POSITIONS)
                    )
                    steps = [
                        (x, y - 50)
                        for (x, y) in MAP_POSITIONS[current_position_index:end_index]
                    ]
                    active_character.set_steps(steps, delay=0.5)
                    current_position_index = end_index
                elif dice.rect.collidepoint(event.pos):
                    dice.handle_click(event.pos)
                for tile in rock_tiles:
                    tile.handle_click(event.pos)
            else:
                for tile in rock_tiles:
                    tile.handle_event(event)

        # Di chuyển theo xúc xắc khi vừa quay xong
        dice.update(dt)
        if not dice.is_rolling and dice.final_value != 0:
            step_count = dice.get_value()
            end_index = min(current_position_index + step_count, len(MAP_POSITIONS))
            steps = [
                (x, y - 50)
                for (x, y) in MAP_POSITIONS[current_position_index:end_index]
            ]
            active_character.set_steps(steps, delay=0.5)
            current_position_index = end_index
            dice.final_value = 0  # Để tránh lặp lại

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
            active_character.has_moved = False

        active_character.play_sound_if_moved()
        dice.update(dt)

        screen.fill((135, 206, 235))

        for tile in rock_tiles:
            tile.draw(screen)

        for char in characters:
            char.update(dt)
            char.draw(screen, font)

        # Draw button
        pygame.draw.rect(screen, (0, 128, 0), button_rect)
        button_label = font.render("Start Walk", True, (255, 255, 255))
        screen.blit(button_label, (button_rect.x + 20, button_rect.y + 10))

        # Draw dice
        dice.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
