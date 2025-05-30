# Biến toàn cục chứa tất cả vị trí bước
import pygame

pygame.font.init()
MAP_POSITIONS = []
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dev Sea Adventure")
font = pygame.font.SysFont("../assets/fonts/Roboto-Regular.ttf", 36)
