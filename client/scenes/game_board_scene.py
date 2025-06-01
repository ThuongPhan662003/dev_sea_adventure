import math
import pygame

from settings import LEN_MAP, MAP_POSITIONS, TILE_SIZE
from utils.utils import create_zigzag_rock_map
from .base_scene import BaseScene
from .components.character import Character
from .components.dice import Dice
import asyncio


class GameBoardScene(BaseScene):
    def __init__(self, manager, websocket_client):
        super().__init__()
        self.manager = manager
        self.client = websocket_client
        self.font = pygame.font.SysFont(None, 36)

        # Load hình ảnh tile 1 lần
        tile_size = 50
        self.tile_images = [
            pygame.transform.scale(
                pygame.image.load(
                    f"./assets/background/output_tiles/tile_0_{i}.png"
                ).convert_alpha(),
                (tile_size, tile_size),
            )
            for i in range(3)
        ]

        # Load âm thanh tile 1 lần
        self.tile_sounds = [
            pygame.mixer.Sound(f"./assets/background/output_tiles/music_{i}.wav")
            for i in range(3)
        ]

        # Load sprite folders và âm thanh character 1 lần
        self.sprite_folders = [
            "./assets/characters/bat",
            "./assets/characters/blob",
            "./assets/characters/skeleton",
            "./assets/characters/dev",
        ]
        self.sound_paths = [
            "./assets/character_sounds/impact.ogg",
            "./assets/character_sounds/music.wav",
            "./assets/character_sounds/shoot.wav",
            "./assets/character_sounds/shoot.wav",
        ]

        # Load Dice assets
        self.dice_images_path = "./assets/background/dices"
        self.dice_sound_path = "./assets/background/dices/dice_sound.wav"

        # Các biến còn lại
        self.rock_tiles = []
        self.characters = []
        self.active_character = None
        self.dice = None
        self.map_positions = MAP_POSITIONS
        self.button_rect = pygame.Rect(800, 600, 150, 50)
        self.current_position_index = 0
        self.player_index = 0  # sẽ set sau khi biết danh sách player

    def on_enter(self):
        print("Game started!")
        self.init_board()

    def init_board(self):

        self.rock_tiles = create_zigzag_rock_map(
            self.tile_images,
            self.tile_sounds,
            TILE_SIZE,
            count=15,
            amplitude=100,
            frequency=0.4,
            base_y=500,
            gap=15,
            slope=25,
            left_margin=70,
        )

        self.characters = [
            Character(
                name=self.client.players[i],
                folder_path=self.sprite_folders[i % len(self.sprite_folders)],
                position=(150 + i * 100, 300),
                sound_path=self.sound_paths[i % len(self.sound_paths)],
                channel_index=i,
            )
            for i in range(len(self.client.players))
        ]
        self.player_index = self.client.players.index(self.client.player_name)
        # self.player_index = 1
        self.active_character = self.characters[
            self.player_index % len(self.characters)
        ]

        self.dice = Dice(
            "./assets/background/dices",
            "./assets/background/dices/dice_sound.wav",
            (1000, 90),
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.dice.rect.collidepoint(event.pos):
                self.dice.handle_click(event.pos)

            for tile in self.rock_tiles:
                tile.handle_click(event.pos)

        else:
            for tile in self.rock_tiles:
                tile.handle_event(event)

    def update(self):
        # Check queue for external actions (from server)
        message = self.client.get_message_nowait()
        while message:
            if message["type"] == "external_action":
                sender = message["sender"]
                action_data = message["data"]
                token_data = message["token_data"]

                step_count = action_data["steps"]
                target_character = next(
                    (c for c in self.characters if c.name == sender), None
                )

                if target_character:
                    start_index = 0
                    for i, pos in enumerate(MAP_POSITIONS):
                        if (pos["x"], pos["y"] - 50) == target_character.get_position():
                            start_index = i
                            break

                    end_index = min(start_index + step_count, len(MAP_POSITIONS))
                    steps = [
                        (pos["x"], pos["y"] - 50)
                        for pos in MAP_POSITIONS[start_index:end_index]
                    ]
                    target_character.set_steps(steps, delay=0.5)
                    print(f"[Client] {sender} moved {step_count} steps")
            elif message["type"] == "your_turn":
                # Nếu là lượt của người chơi này, có thể thực hiện hành động
                if message["player"] == self.client.player_name:
                    print(f"[Client] It's your turn, {self.client.player_name}!")
                    self.active_character = next(
                        (
                            c
                            for c in self.characters
                            if c.name == self.client.player_name
                        ),
                        None,
                    )
                    self.dice.is_rolling = False
            message = self.client.get_message_nowait()

        dt = pygame.time.Clock().tick(60) / 1000

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.active_character.move("left", dt)
        elif keys[pygame.K_RIGHT]:
            self.active_character.move("right", dt)
        elif keys[pygame.K_UP]:
            self.active_character.move("up", dt)
        elif keys[pygame.K_DOWN]:
            self.active_character.move("down", dt)
        else:
            self.active_character.has_moved = False
        self.dice.update(dt)
        if not self.dice.is_rolling and self.dice.final_value != 0:
            step_count = self.dice.get_value()
            print(f"Dice rolled: {step_count}")

            # self.client.send_dice(step_count)
            end_index = min(
                self.current_position_index + step_count, len(MAP_POSITIONS)
            )
            steps = [
                (pos["x"], pos["y"] - 50)
                for pos in MAP_POSITIONS[self.current_position_index : end_index]
            ]
            self.active_character.set_steps(steps, delay=0.5)
            self.current_position_index = end_index

            # 👉 Gửi dữ liệu tới server
            # if self.client:
            #     import threading, asyncio

            token_data = {
                "position": self.current_position_index
            }  # dữ liệu vị trí hoặc token tùy thiết kế server
            action_data = {
                "steps": step_count,
                "player": self.active_character.name,
            }
            # threading.Thread(
            #     target=lambda: asyncio.run(
            #         self.client.send_action(token_data, action_data)
            #     ),
            #     daemon=True,
            # ).start()
            self.client.send_action(token_data, action_data)

            self.dice.final_value = 0  # reset sau khi gửi

            self.active_character.play_sound_if_moved()
            # self.dice.update(dt)

        for char in self.characters:
            char.update(dt)

    def draw(self, screen):

        # Vẽ background trước
        screen.blit(self.background, (0, 0))

        for tile in self.rock_tiles:
            tile.draw(screen)

        for char in self.characters:
            char.draw(screen, self.font)

        pygame.draw.rect(screen, (0, 128, 0), self.button_rect)
        button_label = self.font.render("Start Walk", True, (255, 255, 255))
        screen.blit(button_label, (self.button_rect.x + 20, self.button_rect.y + 10))

        self.dice.draw(screen)
