import math
import pygame
import random
from tile import RockTile
from character import Character
from dice import Dice

MAP_POSITIONS = []
current_position_index = 0

# Tạo bản đồ hình sin


def create_sine_rock_map(
    tile_images, tile_sounds, tile_size, count, amplitude, frequency, offset_y, gap
):
    global MAP_POSITIONS
    tiles = []
    step = tile_size + gap
    MAP_POSITIONS = []
    for i in range(count):
        x = i * step
        y = offset_y + int(
            random.uniform(0.8, 1.2) * amplitude * math.sin(i * frequency)
        )
        MAP_POSITIONS.append((x, y))
        score = 5 + i
        img = tile_images[i % len(tile_images)]
        snd = tile_sounds[i % len(tile_sounds)]
        tiles.append(RockTile(img, x, y, tile_size, score, snd))
    return tiles


# Khởi tạo resources một lần để reuse
initialized = False
tile_images, tile_sounds, rock_tiles, characters, dice = [], [], [], [], None
active_character = None
font = None
button_rect = pygame.Rect(1000, 30, 150, 40)


def init_game_board():
    global initialized, tile_images, tile_sounds, rock_tiles, characters, dice, active_character, font
    if initialized:
        return
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
        offset_y=350,
        gap=20,
    )
    characters.extend(
        [
            Character(
                "Alice",
                "assets/characters/bat",
                (150, 300),
                "assets/sounds/impact.ogg",
                0,
            ),
            Character(
                "Bob",
                "assets/characters/blob",
                (150, 300),
                "assets/sounds/music.wav",
                1,
            ),
            Character(
                "Jame",
                "assets/characters/skeleton",
                (150, 300),
                "assets/sounds/shoot.wav",
                2,
            ),
        ]
    )
    active_character = characters[1]
    dice = Dice("dices", "dices/dice_sound.wav", (1000, 90))
    font = pygame.font.SysFont("Arial", 20)
    initialized = True


def draw_game_board(screen, websocket_client):
    global current_position_index
    init_game_board()
    dt = pygame.time.get_ticks() / 1000.0

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

    dice.update(dt)
    dice.draw(screen)

    pygame.display.flip()


def handle_game_event(event):
    global current_position_index
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if button_rect.collidepoint(event.pos):
            step_count = dice.get_value()
            end_index = min(current_position_index + step_count, len(MAP_POSITIONS))
            steps = [
                (x, y - 50)
                for (x, y) in MAP_POSITIONS[current_position_index:end_index]
            ]
            characters[1].set_steps(steps, delay=0.5)
            current_position_index = end_index
        elif dice.rect.collidepoint(event.pos):
            dice.handle_click(event.pos)
            if not dice.is_rolling:
                dice.final_value = dice.get_value()
        for tile in rock_tiles:
            tile.handle_click(event.pos)
    else:
        for tile in rock_tiles:
            tile.handle_event(event)
