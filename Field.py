import numpy as np
from skimage.morphology import flood_fill
import pygame

from GameDefs import *

class Field:

    def __init__(self, window):
        self.window = window
        self.field_bmp = np.zeros(shape=(FIELD_HEIGHT, FIELD_WIDTH))
        self.blue_count = 0
        # self.base_rect = pygame.Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT)

        for i in range(FIELD_HEIGHT):
            for j in range(FIELD_WIDTH):
                if i < BORDER - 1 or j < BORDER - 1 or i >= FIELD_HEIGHT - BORDER or j >= FIELD_WIDTH - BORDER:
                    self.field_bmp[i][j] = BLUE
                    # self.blue_count += 1
                else:
                    self.field_bmp[i][j] = BLACK
        self.modified = True

    def draw(self):
        # pygame.draw.rect(self.window, AQUA, self.base_rect)
        surf = pygame.surfarray.make_surface(np.swapaxes(self.field_bmp, 0, 1))
        pix_array = pygame.PixelArray(surf)
        pix_array.replace(BLUE, AQUA)
        pix_array.replace(RED, PURPLE)
        del pix_array
        self.window.blit(surf, (0, 0))

    def flood_fill(self, white_dots, orange_lines):
        # def check_criteria(x, y, queue):
        #     if self.field_bmp[y][x] == BLACK:
        #         self.ops += 1
        #         self.field_bmp[y][x] = CHECKED
        #         queue.extend([[x+1, y], [x, y+1], [x-1, y], [x, y-1]])

        # replace reds with blue
        # self.blue_count += np.count_nonzero(self.field_bmp == RED)
        self.field_bmp[self.field_bmp == RED] = BLUE
        start_points = [dot for dot in white_dots]
        for line in orange_lines:
            start_points.append(line.end_one)
            start_points.append(line.end_two)
        for point in start_points:
            if self.field_bmp[point.y][point.x] == BLACK:
                self.field_bmp = flood_fill(self.field_bmp, (point.y, point.x), CHECKED)
        # for point in start_points:
        #     if self.field_bmp[point.y, point.x] == CHECKED:
        #         continue
        #     queue = [[point.x, point.y]]
        #     while queue:
        #         new_point = queue.pop()
        #         check_criteria(new_point[0], new_point[1], queue)

        # for point in start_points:
        #     if self.field_bmp[point.y, point.x] == CHECKED:
        #         continue
        #     queue = [[point.x, point.y]]
        #     while queue:
        #         x_start, y = queue.pop()
        #         x = x_start
        #
        #         while self.field_bmp[y][x] == BLACK:
        #             self.field_bmp[y][x] = CHECKED
        #             if self.field_bmp[y + 1, x] != CHECKED:
        #                 queue.append([x, y + 1])
        #             if self.field_bmp[y-1, x] != CHECKED:
        #                 queue.append([x, y - 1])
        #             x = x + 1
        #         x = x_start - 1
        #         while self.field_bmp[y][x] == BLACK:
        #             self.field_bmp[y][x] = CHECKED
        #             if self.field_bmp[y+1, x] != CHECKED:
        #                 queue.append([x, y+1])
        #             if self.field_bmp[y-1, x] != CHECKED:
        #                 queue.append([x, y - 1])
        #             x = x - 1


        # replace black->blue and checked->black
        # self.blue_count += np.count_nonzero(self.field_bmp == BLACK)
        self.field_bmp[self.field_bmp == BLACK] = BLUE
        self.field_bmp[self.field_bmp == CHECKED] = BLACK

    def check_interference(self, white_dots):
        for dot in white_dots:
            if np.array_equal(self.field_bmp[dot.y, dot.x], RED):
                return True
        return False

    def clean_red(self):
        self.field_bmp[self.field_bmp == RED] = BLACK

    def update_blue_count(self):
        self.blue_count = np.count_nonzero(self.field_bmp == BLUE)
