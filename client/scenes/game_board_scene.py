from datetime import datetime
import math
import pygame
import random
from settings import LEN_MAP, MAP_POSITIONS, TILE_SIZE
from utils.utils import create_zigzag_rock_map
from .base_scene import BaseScene
from .components.character import Character
from .components.dice import Dice
from .components.button import Button
from .game_over_scene import GameOverScene
import asyncio


class GameBoardScene(BaseScene):
    def __init__(self, manager, websocket_client):
        super().__init__()
        self.manager = manager
        self.client = websocket_client
        self.font = pygame.font.SysFont(None, 36)
        self.countdown_font = pygame.font.SysFont(None, 48)

        # Screen size cố định
        self.screen_width = 1200
        self.screen_height = 800

        tile_size = 50
        base_image = pygame.image.load(
            "./assets/background/output_tiles/balloon.png"
        ).convert_alpha()

        # Danh sách scale với trọng số tương ứng (50%, 30%, 20%)
        scales = [1.0] * 5 + [1.3] * 3 + [1.6] * 2

        self.tile_images = [
            pygame.transform.scale(
                base_image, (int(tile_size * scale), int(tile_size * scale))
            )
            for scale in random.choices(scales, k=15)  # hoặc số tile bạn muốn
        ]

        self.tile_sounds = [
            pygame.mixer.Sound(f"./assets/background/output_tiles/music_{i}.wav")
            for i in range(3)
        ]

        # Load sprite folders và âm thanh character
        self.sprite_folders = [
            # "./assets/characters/bat",
            # "./assets/characters/blob",
            # "./assets/characters/skeleton",
            "./assets/characters/c1",
            "./assets/characters/c2",
            "./assets/characters/c3",
            "./assets/characters/c4",
            "./assets/characters/c5",
            "./assets/characters/c6",
        ]

        self.sound_paths = [
            "./assets/character_sounds/impact.ogg",
            "./assets/character_sounds/music.wav",
            "./assets/character_sounds/shoot.wav",
            "./assets/character_sounds/shoot.wav",
            "./assets/character_sounds/shoot.wav",
            "./assets/character_sounds/shoot.wav",
        ]

        # Dice assets
        self.dice_images_path = "./assets/background/dices"
        self.dice_sound_path = "./assets/background/dices/dice_sound.wav"
        self.rock_tiles = []
        self.characters = []
        self.active_character = None
        self.dice = None
        self.map_positions = MAP_POSITIONS
        self.character_positions = {}

        self.buttons = []

        # Đồng hồ đếm ngược
        self.countdown_total = 6.0  # Tổng thời gian đếm ngược (giây)
        self.countdown_time_left = self.countdown_total
        self.countdown_active = False

    def on_enter(self):
        print("Game started!")
        self.init_board()
        self.start_countdown()

    def init_board(self):
        self.move_status = "Go on"
        self.go_on_enabled = True

        # Tạo nút ở góc dưới bên phải
        button_width = 180
        button_height = 50
        padding = 8

        panel_x = self.screen_width - button_width - 20
        panel_y_start = self.screen_height - (button_height + padding) * 5 - 20

        button_texts = [
            ("Go back", (128, 0, 0), self.go_back_action),
            ("Drop down", (0, 0, 128), self.drop_down_action),
        ]

        self.buttons = []
        for i, (text, color, action) in enumerate(button_texts):
            rect = (
                panel_x,
                panel_y_start + i * (button_height + padding),
                button_width,
                button_height,
            )
            self.buttons.append(
                Button(
                    rect=rect, text=text, font=self.font, bg_color=color, action=action
                )
            )

        # Tạo bản đồ đá
        self.rock_tiles = create_zigzag_rock_map(
            self.tile_images,
            self.tile_sounds,
            TILE_SIZE,
            count=15,
            amplitude=100,
            frequency=0.4,
            base_y=500,
            gap=20,
            slope=20,
            left_margin=70,
        )

        # Tạo nhân vật cho từng người chơi
        self.characters = [
            Character(
                name=self.client.players[i],
                folder_path=self.sprite_folders[i % len(self.sprite_folders)],
                position=(150 + i * 100, 300),
                sound_path=self.sound_paths[i % len(self.sound_paths)],
                channel_index=i,
                label_image_path=(
                    "./assets/background/star.png"
                    if self.client.players[i] == self.client.player_name
                    else None
                ),
            )
            for i in range(len(self.client.players))
        ]
        self.player_index = self.client.players.index(self.client.player_name)
        self.active_character = self.characters[
            self.player_index % len(self.characters)
        ]

        # Khởi tạo xúc xắc
        self.dice = Dice(
            self.dice_images_path,
            self.dice_sound_path,
            (600, 600),
        )

        # Vị trí ban đầu mỗi người chơi
        # self.character_positions = {char.name: 0 for char in self.characters}
        # Cập nhật vị trí nhân vật theo player_states
        for char in self.characters:
            player_state = self.client.player_states.get(char.name)
            print(f"[Client] Player state for {char.name}: {player_state}")
            if player_state:
                index = player_state.get("position_index", 0)
                if 0 <= index < len(MAP_POSITIONS):
                    pos = MAP_POSITIONS[index]
                    char.position = [pos["x"], pos["y"] - 50]
                    self.character_positions[char.name] = index

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.dice.rect.collidepoint(event.pos):
                # self.dice.handle_click(event.pos)
                # ✅ Chặn nếu không phải lượt của người chơi này

                if self.client.token_holder != self.client.player_name:
                    print("[Client] Không phải lượt của bạn.")
                else:
                    self.dice.handle_click(event.pos)

            for tile in self.rock_tiles:
                tile.handle_click(event.pos)

            for button in self.buttons:
                button.handle_event(event)
        else:
            for tile in self.rock_tiles:
                tile.handle_event(event)

    def go_back_action(self):
        print("[Client] Go Back button pressed")
        self.move_status = "Go Back"

    def drop_down_action(self):
        print("[Client] Drop Down button pressed")
        # TODO: Thêm logic khi bấm Drop Down

    def start_countdown(self):
        self.countdown_time_left = self.countdown_total
        self.countdown_active = True

    def update(self):
        dt = pygame.time.Clock().tick(60) / 1000  # delta time (giây)

        # Cập nhật đồng hồ đếm ngược
        if (
            self.client.token_holder == self.client.player_name
            and self.countdown_active
        ):
            self.countdown_time_left -= dt
            if self.countdown_time_left <= 0:
                self.countdown_time_left = self.countdown_total
                # self.countdown_active = False
                print("[Timer] Time's up!")
                # TODO: Hành động khi hết thời gian, ví dụ kết thúc lượt

        # Xử lý message từ server (client)
        message = self.client.get_message_nowait()
        while message:
            if message["type"] == "external_action":
                sender = message["current_turn"]
                target_character = next(
                    (c for c in self.characters if c.name == sender), None
                )
                if target_character:
                    current_index = message.get("current_turn_index", 0)
                    start_index = self.character_positions.get(sender, 0)
                    end_index = min(
                        message.get("current_turn_index", 0), len(MAP_POSITIONS)
                    )

                    if start_index <= end_index:
                        step_range = range(start_index, end_index + 1)
                    else:
                        step_range = range(start_index, end_index - 1, -1)

                    steps = [
                        (MAP_POSITIONS[i]["x"], MAP_POSITIONS[i]["y"] - 50)
                        for i in step_range
                    ]

                    # steps = [
                    #     (pos["x"], pos["y"] - 50) for pos in MAP_POSITIONS[0:end_index]
                    # ]
                    target_character.set_steps(steps, delay=0.5)
                    self.character_positions[sender] = current_index
                    print(f"[Client] {sender} moved to index {current_index}")

            elif message["type"] == "your_turn":
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
                    # self.start_countdown()

            elif message["type"] == "next_token_holder":
                # if message["current_turn"] != self.client.player_name:
                print("[Client] It's your turn", message["current_turn"])
                self.client.token_holder = message["current_turn"]
                self.active_character = next(
                    (c for c in self.characters if c.name == message["current_turn"]),
                    None,
                )
                # Đặt lại đồng hồ đếm ngược dựa trên start_time từ server
                try:
                    from dateutil.parser import isoparse

                    server_time = isoparse(message.get("start_time"))
                    now = datetime.utcnow()
                    delay = (now - server_time).total_seconds()
                    self.countdown_time_left = max(6.0 - delay, 6.0)
                except Exception as e:
                    print("[Warning] Không đồng bộ được thời gian:", e)
                    self.countdown_time_left = 10.0

            elif message["type"] == "end_game":
                winner = message.get("winner")
                print(f"[Client] Game Over! Winner: {winner}")
                self.manager.set_scene("game_over")
                self.manager.active_scene.winner_name = winner
                return

            message = self.client.get_message_nowait()

        # Di chuyển nhân vật bằng phím
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     self.active_character.move("left", dt)
        # elif keys[pygame.K_RIGHT]:
        #     self.active_character.move("right", dt)
        # elif keys[pygame.K_UP]:
        #     self.active_character.move("up", dt)
        # elif keys[pygame.K_DOWN]:
        #     self.active_character.move("down", dt)
        # else:
        #     self.active_character.has_moved = False

        # Cập nhật xúc xắc
        self.dice.update(dt)
        flag = 0

        if not self.dice.is_rolling and self.dice.final_value != 0:
            step_count = self.dice.get_value()
            print(f"Dice rolled: {step_count}")

            player_name = self.active_character.name
            # start_index = self.character_positions.get(player_name, -1)
            start_index = self.client.player_states.get(player_name)["position_index"]
            step_range = [
                i
                for i in range(start_index + 1, len(MAP_POSITIONS))
                if i - start_index <= step_count
            ]

            if step_range:
                steps = [
                    (MAP_POSITIONS[i]["x"], MAP_POSITIONS[i]["y"] - 50)
                    for i in step_range
                ]
                self.active_character.set_steps(steps, delay=0.5)
                print("[Client] Moving character:", self.client.player_states)
                self.client.player_states.get(player_name)["position_index"] = (
                    self.client.player_states.get(player_name)["position_index"]
                ) + step_count
                end_index = step_range[-1]
                # ✅ Cập nhật lại vị trí
                print(
                    f"[Client] {player_name} moved to index {end_index} (start: {start_index}, steps: {step_count})"
                )
                print(self.character_positions[player_name])
                self.character_positions[player_name] = end_index
                self.client.player_states[player_name]["position_index"] = end_index

                # Khi nhân vật đi đến cuối bản đồ
                if end_index >= len(MAP_POSITIONS) - 1:
                    winner = self.active_character.name
                    print(f"[Game] {winner} reached the end!")

                    # Chuyển sang màn hình Game Over, truyền tên người thắng
                    self.client.send_game_over(winner)
                    # return

                token_data = {"position": end_index, "start_index": start_index}
                action_data = self.client.player_states
                map_data = self.client.map_data
                print("map_data", map_data)
                self.client.send_action(token_data, action_data, map_data)
                self.active_character.play_sound_if_moved()

            self.dice.final_value = 0
            self.active_character.play_sound_if_moved()
            # self.start_countdown()
            self.dice.final_value = 0
            self.active_character.play_sound_if_moved()
            flag = 1  # Đánh dấu đã gửi hành động

        # Update các nhân vật
        for char in self.characters:
            char.update(dt)
        if flag == 1:
            self.client.send_turn_update(
                current_turn=self.client.token_holder,
            )
            flag = 0  # Reset flag sau khi gửi
            # Kiểm tra và thêm nhân vật nếu có người mới
        existing_names = {char.name for char in self.characters}
        for i, player_name in enumerate(self.client.players):
            if player_name not in existing_names:
                print(
                    f"[GameBoardScene] Phát hiện người mới: {player_name}, đang tạo nhân vật..."
                )

                char = Character(
                    name=player_name,
                    folder_path=self.sprite_folders[i % len(self.sprite_folders)],
                    position=(
                        150 + i * 100,
                        300,
                    ),  # vị trí tạm thời, sẽ cập nhật bên dưới
                    sound_path=self.sound_paths[i % len(self.sound_paths)],
                    channel_index=i,
                    label_image_path=(
                        "./assets/background/star.png"
                        if player_name == self.client.player_name
                        else None
                    ),
                )

                # Nếu đã có vị trí trong player_states, gán luôn đúng vị trí
                player_state = self.client.player_states.get(player_name)
                if player_state:
                    index = player_state.get("position_index", 0)
                    if 0 <= index < len(MAP_POSITIONS):
                        pos = MAP_POSITIONS[index]
                        char.position = [pos["x"], pos["y"] - 50]
                        self.character_positions[player_name] = index

                self.characters.append(char)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        # Góc trái trên cùng - trạng thái di chuyển
        move_text_surface = self.font.render(
            f"Status: {self.move_status}", True, (255, 255, 255)
        )
        screen.blit(move_text_surface, (20, 20))
        button_label = self.font.render("It's not your turn", True, (255, 255, 255))
        #     screen.blit(button_label, (100, 500))
        # Vẽ các tile đá
        for tile in self.rock_tiles:
            tile.draw(screen)

        # Vẽ nhân vật
        for char in self.characters:
            char.draw(screen, self.font)

        # Vẽ xúc xắc
        self.dice.draw(screen)

        # --- Vẽ chữ "Your turn" trên cùng ---
        if self.client.token_holder:
            # Tạo hiệu ứng scale cho chữ "Your turn"
            time = pygame.time.get_ticks() / 500  # Thời gian theo ms chia nhỏ
            scale = 1 + 0.1 * math.sin(time * 2 * math.pi)  # Scale dao động 0.9 - 1.1
            your_name = self.client.player_name
            token = self.client.token_holder
            if token == your_name:
                your_turn_text = "Your's turn"
                text_color = (0, 255, 0)  # Màu xanh lá cây cho lượt của bạn
            else:
                your_turn_text = f"{token}'s turn"
                text_color = (255, 255, 0)  # Màu vàng cho lượt của người khác

            base_font_size = 48
            font_scaled = pygame.font.SysFont(None, int(base_font_size * scale))
            your_turn_surface = font_scaled.render(your_turn_text, True, text_color)

            x = (self.screen_width - your_turn_surface.get_width()) // 2
            y = 30  # Cách mép trên 30px
            screen.blit(your_turn_surface, (x, y))

        # --- Vẽ đồng hồ đếm ngược ---
        if self.client.token_holder == self.client.player_name:
            time_left = max(self.countdown_time_left, 0)
            # Hiển thị với 1 chữ số thập phân cho mượt hơn
            time_str = f"Time: {time_left:.1f}s"

            # Chuyển màu mượt từ xanh sang đỏ khi còn dưới 5 giây
            if time_left > 5:
                time_color = (0, 255, 0)
            else:
                # Lerp màu xanh->đỏ theo thời gian còn lại
                ratio = time_left / 5
                r = int(255 * (1 - ratio))
                g = int(255 * ratio)
                time_color = (r, g, 0)

            text_surface = self.countdown_font.render(time_str, True, time_color)
            screen.blit(
                text_surface, (self.screen_width - text_surface.get_width() - 20, 20)
            )
        # else:
        #     # Hết thời gian

        #     times_up_text = "Time's up!"
        #     times_up_surface = self.countdown_font.render(
        #         times_up_text, True, (255, 0, 0)
        #     )
        #     x = (self.screen_width - times_up_surface.get_width()) // 2
        #     y = 30  # Cách mép trên 30px
        #     screen.blit(times_up_surface, (x, y))

        # Vẽ panel UI (nền panel phía dưới bên phải)
        button_width = 180
        button_height = 50
        padding = 8

        panel_x = self.screen_width - button_width - 20
        panel_y_start = self.screen_height - (button_height + padding) * 5 - 20
        panel_rect = pygame.Rect(
            panel_x - 20,
            panel_y_start - 20,
            button_width + 40,
            (button_height + padding) * 2 + 40,
        )
        pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=15)

        # Vẽ nút
        for button in self.buttons:
            button.draw(screen)

        # pygame.draw.rect(screen, (0, 128, 0), self.button_rect)
        # button_label = self.font.render("Start Walk", True, (255, 255, 255))
        # screen.blit(button_label, (self.button_rect.x + 20, self.button_rect.y + 10))

        self.dice.draw(screen)
        # if self.client.token_holder != self.client.player_name:
        #     button_label = self.font.render("It's not your turn", True, (255, 255, 255))
        #     screen.blit(button_label, (100, 500))
