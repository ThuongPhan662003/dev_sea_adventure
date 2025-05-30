from PIL import Image
import os

# Mở ảnh và chuyển sang RGBA để xử lý alpha
image = Image.open("image.png").convert("RGBA")
tile_size = 48
cols = image.width // tile_size
rows = image.height // tile_size

# Màu nền tối cần loại bỏ (bạn có thể tinh chỉnh nếu cần)
background_color = image.getpixel((0, 0))

os.makedirs("treasure_icons", exist_ok=True)

for y in range(rows):
    for x in range(cols):
        box = (x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size)
        tile = image.crop(box)
        tile = tile.convert("RGBA")

        # Tách nền
        pixels = tile.getdata()
        new_pixels = []
        for pixel in pixels:
            # Nếu pixel gần giống nền (chênh lệch nhỏ), đặt alpha = 0
            if all(abs(pixel[i] - background_color[i]) < 15 for i in range(3)):
                new_pixels.append((0, 0, 0, 0))
            else:
                new_pixels.append(pixel)
        tile.putdata(new_pixels)

        tile.save(f"treasure_icons/treasure_{y}_{x}.png")
