import pygame
import os
import numpy as np
from GameDefs import *


class Player:

    player_image = None

    OFFSET = 3
    SPEED = 4

    def __init__(self, window):
        self.window = window
        if not Player.player_image:
            Player.player_image = pygame.image.load(os.path.join('Assets', "player.bmp")).convert_alpha()
        self.image = Player.player_image
        self.score = 0
        self.xonii = 2  # lives
        self.died_on_this_level = False
        self.x = FIELD_WIDTH // 2
        self.y = 3
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed_x = self.speed_y = 0

    def reset_position(self):
        self.x = FIELD_WIDTH // 2
        self.y = 3
        self.speed_x = self.speed_y = 0
        self.rect.center = (self.x, self.y)

    def update(self, field_bmp):
        self.direction()
        return self.move(field_bmp)

    def move(self, field_bmp):
        # check edges
        if (self.speed_x < 0 and self.x - self.OFFSET <= 1) or (self.speed_x > 0 and self.x + self.OFFSET >=
                                                                FIELD_WIDTH - 3):
            self.speed_x = 0

        if (self.speed_y < 0 and self.y - self.OFFSET <= 1) or (self.speed_y > 0 and self.y + self.OFFSET >=
                                                                FIELD_HEIGHT - 3):
            self.speed_y = 0

        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.center = (self.x, self.y)

        # color trajectory in the black area
        if np.array_equal(field_bmp[self.y][self.x], BLACK):
            for j in range(self.x - self.OFFSET, self.x + self.OFFSET):
                for i in range(self.y - self.OFFSET, self.y + self.OFFSET):
                    if np.array_equal(field_bmp[i][j], BLACK):
                        field_bmp[i][j] = RED

        # if the player moved from black to blue, return True and reset speed
        if np.array_equal(field_bmp[self.y][self.x], BLUE) and np.array_equal(
                field_bmp[self.y - self.speed_y][self.x - self.speed_x], RED):
            self.speed_x = 0
            self.speed_y = 0
            return True
        return

    def direction(self):
        # get moving direction
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:  # LEFT
            self.speed_x = -self.SPEED
            self.speed_y = 0
        elif keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:  # RIGHT
            self.speed_x = self.SPEED
            self.speed_y = 0
        elif keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:  # UP
            self.speed_x = 0
            self.speed_y = -self.SPEED
        elif keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:  # DOWN
            self.speed_x = 0
            self.speed_y = self.SPEED
        else:
            self.speed_x = 0
            self.speed_y = 0

    def update_score(self, time_remaining, time_limit):
        self.score += 500
        self.score += get_bonus_points(time_remaining, time_limit, self.died_on_this_level)

    def interference(self, white_dots, black_dots, field_bmp):
        # check if a black/white dot hit the player
        for dot in white_dots:
            if field_bmp[self.y][self.x] != BLUE:  # only check for collisions if the player is not in the "safe" area
                if self.rect.colliderect(dot.rect):
                    return True
        for dot in black_dots:
            if self.rect.colliderect(dot.rect):
                return True

    def draw(self):
        self.window.blit(self.image, self.rect)
