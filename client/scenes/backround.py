import pygame
import math
import sys


def draw_sine_map_with_image(
    screen,
    tile_image,
    tile_size=40,
    amplitude=80,
    frequency=0.3,
    offset_x=0,
    offset_y=300,
    count=30,
    gap=10,
    alpha=255,
):
    step = tile_size + gap
    tile_image.set_alpha(alpha)  # đặt độ trong suốt
    for i in range(count):
        x = offset_x + i * step
        y = offset_y + int(math.sin(i * frequency) * amplitude)
        screen.blit(tile_image, (x, y))


def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Sine Wave Map with Parallax")

    clock = pygame.time.Clock()

    tile_size = 40
    tile_image = pygame.image.load("output_tiles/tile_0_6.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))

    # Tạo thêm 2 lớp tile khác (có thể là cùng tile nhưng chỉnh alpha hoặc scale)
    tile_image_far = pygame.transform.scale(
        tile_image, (int(tile_size * 0.6), int(tile_size * 0.6))
    )
    tile_image_near = pygame.transform.scale(
        tile_image, (int(tile_size * 1.2), int(tile_size * 1.2))
    )

    offset_far = 0
    offset_near = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((135, 206, 235))  # nền trời

       
        # Lớp chính đứng yên (offset_x=0)
        draw_sine_map_with_image(
            screen,
            tile_image,
            tile_size=tile_size,
            amplitude=80,
            frequency=0.3,
            offset_x=0,
            offset_y=screen_height // 2,
            count=30,
            gap=30,
            alpha=255,
        )
        

        # Di chuyển các lớp xa gần tạo hiệu ứng parallax
        offset_far -= 0.5  # chạy chậm nhất
        offset_near -= 3  # chạy nhanh hơn

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
