import pygame


class Button:
    def __init__(self, rect, text, font, bg_color=(0, 128, 0), text_color=(255, 255, 255), action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.action = action

        self._render_text()

    def _render_text(self):
        self.rendered_text = self.font.render(self.text, True, self.text_color)
        self.text_pos = (
            self.rect.centerx - self.rendered_text.get_width() // 2,
            self.rect.centery - self.rendered_text.get_height() // 2,
        )

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        screen.blit(self.rendered_text, self.text_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()
