import random
from models.player import Player
from db.game_data_loader import GameDataLoader


class Game:
    def __init__(self, screen, game_id=1):
        self.screen = screen
        self.players = []
        self.token_index = 0  # Vị trí người chơi có "token"
        self.game_id = game_id
        self.running = True
        self.turn_in_progress = False  # Kiểm soát không cho ấn SPACE liên tục

    def load_data(self):
        loader = GameDataLoader()
        player_data = loader.get_players_in_game(self.game_id)
        self.players = [
            Player(p["player_name"], self.hex_to_rgb(p["color"]), 0)
            for p in player_data
        ]
        loader.close()

    def current_player(self):
        return self.players[self.token_index]

    def roll_dice(self):
        return random.randint(1, 3), random.randint(1, 3)

    def take_turn(self):
        dice1, dice2 = self.roll_dice()
        steps = dice1 + dice2
        player = self.current_player()
        player.move(steps)
        print(f"{player.name} moved {steps} steps to position {player.position}")
        self.next_turn()

    def next_turn(self):
        self.token_index = (self.token_index + 1) % len(self.players)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
