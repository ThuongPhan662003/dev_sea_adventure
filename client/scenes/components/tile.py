import os
import pygame


class RockTile:
    def __init__(self, source_image, x, y, tile_size, score=10, click_sound=None):
        self.source_image = source_image
        self.image = source_image.copy()
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.collected = False
        self.tile_size = tile_size
        self.score = score
        self.click_sound = click_sound
        self.stop_sound_event = pygame.USEREVENT + x  # Mỗi tile có event riêng

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


        icon_path = (
            "./assets/background/treasure/open.png"
            if self.collected
            else "./assets/background/treasure/close.png"
        )

        treasure_icon = pygame.image.load(icon_path).convert_alpha()
        treasure_icon = pygame.transform.scale(treasure_icon, (30, 30))
        screen.blit(treasure_icon, (self.rect.right - 40, self.rect.top + 60))

        if self.collected:
            temp_img = self.image.copy()
            temp_img.set_alpha(100)
            screen.blit(temp_img, self.rect.topleft)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos) and not self.collected:
            self.collected = True
            if self.click_sound:
                self.click_sound.play()
                pygame.time.set_timer(self.stop_sound_event, 1000, loops=1)
            print(
                f"\u0110\u00e3 l\u1ea5y kho b\u00e1u, \u0111i\u1ec3m c\u1ed9ng: {self.score}"
            )
            return True
        return False

    def handle_event(self, event):
        if event.type == self.stop_sound_event and self.click_sound:
            self.click_sound.stop()
