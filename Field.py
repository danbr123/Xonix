import numpy as np
from skimage.morphology import flood_fill
import pygame

from GameDefs import *


class Field:

    def __init__(self, window):
        self.window = window
        self.field_bmp = np.zeros(shape=(FIELD_HEIGHT, FIELD_WIDTH))
        self.blue_count = 0

        # color the border
        for i in range(FIELD_HEIGHT):
            for j in range(FIELD_WIDTH):
                if i < BORDER - 1 or j < BORDER - 1 or i >= FIELD_HEIGHT - BORDER or j >= FIELD_WIDTH - BORDER:
                    self.field_bmp[i][j] = BLUE
                else:
                    self.field_bmp[i][j] = BLACK

    def draw(self):
        surf = pygame.surfarray.make_surface(np.swapaxes(self.field_bmp, 0, 1))
        pix_array = pygame.PixelArray(surf)
        pix_array.replace(BLUE, AQUA)
        pix_array.replace(RED, PURPLE)
        del pix_array
        self.window.blit(surf, (0, 0))

    def flood_fill(self, white_dots, orange_lines):
        # clear purple pixels
        self.field_bmp[self.field_bmp == RED] = BLUE
        start_points = [dot for dot in white_dots]
        for line in orange_lines:
            start_points.append(line.end_one)
            start_points.append(line.end_two)
        # apply flood fill algorithm from every enemy in the black area
        for point in start_points:
            if self.field_bmp[point.y][point.x] == BLACK:  # fix obscure bug where the the algorithm fills with black
                self.field_bmp = flood_fill(self.field_bmp, (point.y, point.x), CHECKED)
        # update colors
        self.field_bmp[self.field_bmp == BLACK] = BLUE
        self.field_bmp[self.field_bmp == CHECKED] = BLACK

    def check_interference(self, white_dots):
        # check if a white dot hit the purple line
        for dot in white_dots:
            if np.array_equal(self.field_bmp[dot.y, dot.x], RED):
                return True
        return False

    def clean_red(self):
        self.field_bmp[self.field_bmp == RED] = BLACK

    def update_blue_count(self):
        self.blue_count = np.count_nonzero(self.field_bmp == BLUE)
