# -------------------- client/scenes/game_board.py --------------------
import asyncio
import json

import pygame
import math
import random
from tile import RockTile
from character import Character
from dice import Dice
from .setup import *

# Biến toàn cục để lưu đối tượng
MAP_POSITIONS = []
rock_tiles = []
characters = []
active_character = None
dice = None
button_rect = pygame.Rect(1000, 30, 150, 40)
current_position_index = 0


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
        score = 5 + i
        collected = False
        img = tile_images[i % len(tile_images)]
        snd = tile_sounds[i % len(tile_sounds)]

        # Lưu cả thông tin chi tiết vào MAP_POSITIONS
        MAP_POSITIONS.append({"x": x, "y": y, "score": score, "collected": collected})

        # Tạo đối tượng RockTile bình thường
        tiles.append(RockTile(img, x, y, tile_size, score, snd))
    return tiles


def draw_game_board(screen, websocket_client, player_index, event=None):
    global rock_tiles, characters, active_character, dice, current_position_index

    if not rock_tiles:
        tile_size = 50
        tile_images = [
            pygame.transform.scale(
                pygame.image.load(
                    f"./assets/background/output_tiles/tile_0_{i}.png"
                ).convert_alpha(),
                (tile_size, tile_size),
            )
            for i in range(3)
        ]
        tile_sounds = [
            pygame.mixer.Sound(f"./assets/background/output_tiles/music_{i}.wav")
            for i in range(3)
        ]

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

        sprite_folders = [
            "./assets/characters/bat",
            "./assets/characters/blob",
            "./assets/characters/skeleton",
            "./assets/characters/dev",
        ]

        sound_paths = [
            "./assets/character_sounds/impact.ogg",
            "./assets/character_sounds/music.wav",
            "./assets/character_sounds/shoot.wav",
            "./assets/character_sounds/shoot.wav",
        ]

        characters = [
            Character(
                name=websocket_client.players[i],
                folder_path=sprite_folders[i % len(sprite_folders)],
                position=(150 + i * 100, 300),
                sound_path=sound_paths[i % len(sound_paths)],
                channel_index=i,
            )
            for i in range(len(websocket_client.players))
        ]

        # active_character = characters[1]
        active_character = characters[player_index % len(characters)]

        dice = Dice(
            "./assets/background/dices",
            "./assets/background/dices/dice_sound.wav",
            (1000, 90),
        )

    dt = pygame.time.Clock().tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # ⚠️ Chỉ người đang giữ token mới được thao tác
            # if websocket_client.player_name != websocket_client.current_turn:
            #     print("⚠️ Not your turn")
            #     return

            if button_rect.collidepoint(event.pos):
                step_count = dice.get_value()
                end_index = min(current_position_index + step_count, len(MAP_POSITIONS))
                steps = [
                    (x, y - 50)
                    for (x, y) in MAP_POSITIONS[current_position_index:end_index]
                ]
                active_character.set_steps(steps, delay=0.5)
                current_position_index = end_index
                # ✅ Gửi hành động và token sau khi bước xong
                token_data = {
                    "map_positions": [
                        {
                            "x": pos[0],
                            "y": pos[1],
                            "collected": rock_tiles[i].collected,
                            "score": rock_tiles[i].score,
                        }
                        for i, pos in enumerate(MAP_POSITIONS)
                    ]
                }

                action_data = {
                    "player": websocket_client.player_name,
                    "step_count": step_count,
                    "end_index": end_index,
                }
                asyncio.run(websocket_client.send_action(token_data, action_data))
                print("haha")
            elif dice.rect.collidepoint(event.pos):
                dice.handle_click(event.pos)
            for tile in rock_tiles:
                tile.handle_click(event.pos)
        else:
            for tile in rock_tiles:
                tile.handle_event(event)

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

    if not dice.is_rolling and dice.final_value != 0:
        step_count = dice.get_value()
        end_index = min(current_position_index + step_count, len(MAP_POSITIONS))
        steps = [
            (pos["x"], pos["y"] - 10)
            for pos in MAP_POSITIONS[current_position_index:end_index]
        ]

        active_character.set_steps(steps, delay=0.5)
        current_position_index = end_index
        dice.final_value = 0

    active_character.play_sound_if_moved()
    dice.update(dt)

    screen.fill((135, 206, 235))

    for tile in rock_tiles:
        tile.draw(screen)

    for char in characters:
        char.update(dt)
        char.draw(screen, font)

    pygame.draw.rect(screen, (0, 128, 0), button_rect)
    button_label = font.render("Start Walk", True, (255, 255, 255))
    screen.blit(button_label, (button_rect.x + 20, button_rect.y + 10))

    dice.draw(screen)
