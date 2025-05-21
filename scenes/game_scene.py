import pygame
from config import MAP_POSITIONS, SCREEN_WIDTH


def draw_board(screen):
    screen.fill((0, 105, 148))
    font = pygame.font.SysFont(None, 24)
    for i, pos in enumerate(MAP_POSITIONS):
        pygame.draw.circle(screen, (255, 255, 255), pos, 30)
        pygame.draw.circle(screen, (0, 0, 0), pos, 30, 2)
        text = font.render(f"{i}", True, (0, 0, 0))
        screen.blit(text, (pos[0] - 5, pos[1] - 10))
    pygame.draw.rect(screen, (255, 255, 255), (0, 500, SCREEN_WIDTH, 100))
    info_font = pygame.font.SysFont(None, 28)
    info_text = info_font.render(
        "Press SPACE to roll dice and start turn", True, (0, 0, 0)
    )
    screen.blit(info_text, (20, 520))


def draw_players(screen, players):
    for p in players:
        pos = MAP_POSITIONS[p.position]
        pygame.draw.circle(screen, p.color, (pos[0], pos[1] - 40), 12)
