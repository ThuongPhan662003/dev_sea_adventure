import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from models.game import Game
from scenes.game_scene import draw_board, draw_players


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dev Sea Adventure")

    clock = pygame.time.Clock()
    game = Game(screen)
    game.load_data()

    font = pygame.font.SysFont(None, 28)

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Chỉ người giữ token được ấn SPACE
                    game.take_turn()

        draw_board(screen)

        draw_players(screen, game.players)

        # Hiển thị tên người chơi có lượt (token)
        current = game.current_player()
        msg = f"Lượt của: {current.name}"
        text = font.render(msg, True, (0, 0, 0))
        screen.blit(text, (800, 520))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
