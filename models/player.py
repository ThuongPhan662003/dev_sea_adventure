# class Player:
#     def __init__(self, name, color, start_position):
#         self.name = name
#         self.color = color
#         self.position = start_position
#         self.score = 0

#     def roll_dice(self):
#         import random
#         return random.randint(1, 3), random.randint(1, 3)

#     def take_turn(self, screen):
#         dice1, dice2 = self.roll_dice()
#         move = dice1 + dice2
#         self.position = (self.position + move) % 10  # wrap lại map
#         # Kiểm tra source code tại vị trí mới => cộng điểm


class Player:
    def __init__(self, name, color, start_position=0):
        self.name = name
        self.color = color
        self.position = start_position
        self.score = 0

    def move(self, steps):
        self.position = (self.position + steps) % 10
