import pygame


def draw_button(screen, rect, text, font_size=24):
    pygame.draw.rect(screen, (0, 100, 200), rect)
    font = pygame.font.SysFont(None, font_size)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.x + 10, rect.y + 10))
