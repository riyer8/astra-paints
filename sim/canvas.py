"""The canvas: a grid of pixels. Paint is faked analytically, not simulated."""
import numpy as np
import imageio  # pyright: ignore[reportMissingImports]


class Canvas:
    def __init__(self, size=256, x_range=(0.0, 0.5), y_range=(-0.25, 0.25)):
        self.size = size
        self.x_range = x_range
        self.y_range = y_range
        self.pixels = np.full((size, size, 3), 255, dtype=np.uint8)  # white

    def world_to_pixel(self, x, y):
        (x0, x1), (y0, y1) = self.x_range, self.y_range
        col = int((x - x0) / (x1 - x0) * (self.size - 1))
        row = int((1.0 - (y - y0) / (y1 - y0)) * (self.size - 1))
        return row, col

    def stamp(self, x, y, color, radius=3):
        row, col = self.world_to_pixel(x, y)
        rr, cc = np.ogrid[:self.size, :self.size]
        mask = (rr - row) ** 2 + (cc - col) ** 2 <= radius ** 2
        self.pixels[mask] = color

    def save(self, path):
        imageio.imwrite(path, self.pixels)
