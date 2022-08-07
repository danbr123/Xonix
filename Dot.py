import random
import os
import pygame
from GameDefs import *


class Dot:

    OFFSET = 3
    Z_ORDER = 4
    GAP = 50
    SPEED_MIN = 1
    SPEED_MAX = 4

    def __init__(self, window, x=None, y=None):
        self.window = window
        if x:
            self.x = x
        else:
            self.x = self.GAP + random.randint(0, FIELD_WIDTH - 2 * self.GAP - 1)
        if y:
            self.y = y
        else:
            self.y = self.GAP + random.randint(0, FIELD_HEIGHT - 2 * self.GAP - 1)

        self.speed_x = random.randint(self.SPEED_MIN, self.SPEED_MAX)
        self.speed_y = random.randint(self.SPEED_MIN, self.SPEED_MAX)
        if random.getrandbits(1):
            self.speed_x = - self.speed_x
        if random.getrandbits(1):
            self.speed_y = - self.speed_y
        self.bounce_pix = BLUE
        self.bounce_pix_2 = None
        self.image = None
        self.rect = None

    def bounce(self, field_bmp):
        if self.y_border() or np.array_equal(self.next_pix_y(field_bmp), self.bounce_pix) or np.array_equal(
                self.next_pix_y(field_bmp), self.bounce_pix_2):
            self.speed_y = -self.speed_y
        if self.x_border() or np.array_equal(self.next_pix_x(field_bmp), self.bounce_pix) or np.array_equal(
                self.next_pix_x(field_bmp), self.bounce_pix_2):
            self.speed_x = -self.speed_x

    def update(self, field_bmp):
        self.bounce(field_bmp)
        self.x += self.speed_x
        self.y += self.speed_y
        if self.rect:
            self.rect.center = (self.x, self.y)

    def draw(self):
        # pygame.draw.rect(self.window, (0, 0, 0), pygame.Rect(self.x, self.y, 3,3))
        self.window.blit(self.image, self.rect)

    def y_border(self):
        if self.speed_y > 0:
            return self.y + self.OFFSET > FIELD_HEIGHT
        else:
            return self.y - self.OFFSET < 0

    def x_border(self):
        if self.speed_x > 0:
            return self.x + self.OFFSET > FIELD_WIDTH
        else:
            return self.x - self.OFFSET < 0

    def next_pix_x(self, field_bmp):
        try:
            if self.speed_x > 0:
                pix = field_bmp[self.y][self.x + self.speed_x + self.OFFSET]
            else:
                pix = field_bmp[self.y][self.x + self.speed_x - self.OFFSET]
            return pix
        except:
            return self.bounce_pix

    def next_pix_y(self, field_bmp):
        try:
            if self.speed_y > 0:
                pix = field_bmp[self.y + self.speed_y + self.OFFSET][self.x]
            else:
                pix = field_bmp[self.y + self.speed_y - self.OFFSET][self.x]
            return pix
        except:
            return self.bounce_pix


class WhiteDot(Dot):

    white_dot_img = None

    SPEED_MIN = 1
    SPEED_MAX = 3

    def __init__(self, window):
        super().__init__(window)
        self.bounce_pix = BLUE
        if not WhiteDot.white_dot_img:
            WhiteDot.white_dot_img = pygame.image.load(os.path.join('Assets', "wdot.bmp")).convert_alpha()
        self.image = WhiteDot.white_dot_img
        self.rect = self.image.get_rect(center=(self.x, self.y))


class BlackDot(Dot):

    black_dot_img = None

    SPEED_MIN = SPEED_MAX = 2

    def __init__(self, window):
        self.y = random.randint(0, 3) + (FIELD_HEIGHT - BORDER + 10)
        self.x = BORDER + random.randint(0, FIELD_WIDTH - BORDER - 1)
        super().__init__(window, self.x, self.y)
        self.bounce_pix = BLACK
        self.bounce_pix_2 = RED
        if not BlackDot.black_dot_img:
            BlackDot.black_dot_img = pygame.image.load(os.path.join('Assets', "bdot.png")).convert_alpha()
        self.image = BlackDot.black_dot_img
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def reset_position(self):
        self.y = random.randint(0, 3) + (FIELD_HEIGHT - BORDER + 10)
        self.x = BORDER + random.randint(0, FIELD_WIDTH - BORDER - 1)
        self.rect.center = (self.x, self.y)



class LineDot(Dot):

    SPEED_MIN = 1
    SPEED_MAX = 1

    def __init__(self, window):
        super().__init__(window)
        self.bounce_pix = BLUE
        self.image = None

    def draw(self):
        pass


class OrangeLine:

    Z_ORDER = 3

    def __init__(self, window):
        self.window = window
        self.end_one = LineDot(window)
        self.end_two = LineDot(window)

    def update(self, field_bmp):
        self.end_one.update(field_bmp)
        self.end_two.update(field_bmp)
        self.cover_field(field_bmp)

    def draw(self):
        pygame.draw.line(self.window, ORANGE, (self.end_one.x, self.end_one.y), (self.end_two.x, self.end_two.y))

    def cover_field(self, field_bmp):
        x1, y1 = self.end_one.x, self.end_one.y
        x2, y2 = self.end_two.x, self.end_two.y

        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        delta_x = x2 - x1
        delta_y = abs(y2 - y1)
        error = delta_x // 2
        is_up = 1 if y1 < y2 else -1

        y = y1
        for x in range(x1, x2):
            pixel = [y, x] if steep else [x, y]
            field_bmp[pixel[1], pixel[0]] = BLACK
            for i in range(4):

                field_bmp[pixel[1] + i, pixel[0]] = BLACK
                field_bmp[pixel[1] - i, pixel[0]] = BLACK
                field_bmp[pixel[1], pixel[0] + i] = BLACK
                field_bmp[pixel[1], pixel[0] - i] = BLACK


            error -= delta_y
            if error < 0:
                y += is_up
                error += delta_x
