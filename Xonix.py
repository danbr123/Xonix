import pygame
import os
import random
from GameDefs import *
import numpy as np
import time


pygame.init()
pygame.display.set_caption("Xonix ripoff by Dan")
pygame.font.init()

# fonts
courer_regular = pygame.font.match_font("Courier", bold=False)
courer_bold = pygame.font.match_font("Courier", bold=True)
font = pygame.font.Font(courer_regular, 12)
font_b = pygame.font.Font(courer_bold, 12)



class Game:

    def __init__(self):
        # init pygame stuff
        self._running = True
        self.size = self.width, self.height = WIDTH, HEIGHT
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.size)

        self.player = Player(self.window)
        self.status_bar = StatusBar(self.window)
        self.level = 2

        # level params
        self.white_dots = None
        self.black_dots = None
        self.orange_lines = None
        self.field = None
        self.time_limit = None
        self.start_time = None
        self.time_remaining = None
        self.percent_complete = None
        self.show_ready = False

        self.init_next_level()

        self.congrats = False
        self.show_score = False

        # run game
        self.on_execute()


    def on_execute(self):
        while (self._running):
            self.clock.tick(FPS)  # sync time to match FPS
            for event in pygame.event.get():  # handle events if they exist
                self.on_event(event)
            self.on_loop()  # perform loop logic
            self.on_render()  # draw the current state
        self.on_cleanup()  # close app

    def on_event(self, event):
        # this function runs in each iteration of the main loop where a pygame event happened
        if event.type == pygame.QUIT:  # click the exit button
            self._running = False

    def on_loop(self):
        if not self.show_score:
            if self.show_ready:
                self.show_ready = False
                time.sleep(2)
                self.start_time = time.time()
            else:
                self.time_remaining = int(self.time_limit - (time.time() - self.start_time))

        if self.player.update(self.field.field_bmp):
            self.field.flood_fill(self.white_dots, self.orange_lines)
            self.percent_complete = 100 * (self.field.blue_count / TOTAL_SQUARES)
            if self.percent_complete > 75:
                self.init_next_level()
        for dot in self.white_dots:
            dot.update(self.field.field_bmp)
        for dot in self.black_dots:
            dot.update(self.field.field_bmp)
        for line in self.orange_lines:
            line.update(self.field.field_bmp)

        if self.player.interference(self.white_dots, self.black_dots) or self.field.check_interference(self.white_dots) or self.time_remaining <= 0:
            time.sleep(2)
            self.player.xonii -= 1
            if self.player.xonii == 0:
                self.show_score = True
            else:
                self.player.died_on_this_level = True
                self.player.reset_position()
                self.field.clean_red()
                self.time_limit = get_time_limit(self.level, self.player.died_on_this_level)
                self.time_remaining = self.time_limit
                self.show_ready = True

        if self.show_score:
            keys_pressed = pygame.key.get_pressed()
            if pygame.K_ESCAPE in keys_pressed or pygame.K_RETURN in keys_pressed:
                self._running = False

    def on_render(self):
        if self.congrats:
            msg = font.render("you win.", True, WHITE)
            self.window.blit(msg, (10, FIELD_HEIGHT + 5))
        elif self.show_score:
            msg = font.render("you lose.", True, WHITE)
            self.window.blit(msg, (10, FIELD_HEIGHT + 5))

        elif self.show_ready:
            msg = font.render("Ready...", True, WHITE)
            self.window.blit(msg, (10, FIELD_HEIGHT + 5))

        self.field.draw()
        self.status_bar.draw(self.level, self.player.xonii, self.player.score, self.percent_complete, self.time_remaining)
        self.player.draw()
        for dot in self.white_dots:
            dot.draw()
        for dot in self.black_dots:
            dot.draw()
        for line in self.orange_lines:
            line.draw()
        pygame.display.update()



    def on_cleanup(self):
        pygame.quit()

    def init_next_level(self):
        self.level += 1
        self.player.xonii += 1
        self.player.reset_position()
        self.time_limit = get_time_limit(self.level, self.player.died_on_this_level)
        self.time_remaining = self.time_limit
        self.percent_complete = 18
        self.field = Field(self.window)
        counts = get_object_count(self.level)
        self.white_dots = [WhiteDot(self.window) for _ in range(counts["white_dots"])]
        self.black_dots = [BlackDot(self.window) for _ in range(counts["black_dots"])]
        self.orange_lines = [OrangeLine(self.window) for _ in range(counts["orange_lines"])]
        self.show_ready = True

class GameDefs:

    def __init__(self):
        self.white_dots = None
        self.black_dots = None
        self.orange_lines = None
        self.limit = 0


class StatusBar:

    STRETCH = 0.8

    def __init__(self, window):
        self.window = window

        self.status_msg = "Level: {level}    Xonii: {xonii}    Filled: {fill_p}%    Score: {score}    "
        self.time_msg = "Time: {min}:{sec}"
        self.time_msg_low = "Time:{min}:{sec}   <<< Low Time!"

    def draw(self, level, xonii, score, filled, time):
        mins = time//60
        secs = time - mins * 60
        msg = font.render(self.status_msg.format(level=level, xonii=xonii, fill_p=round(filled), score=score), True, (255,255,255))
        if mins < 0 and secs < 30:
            msg_time = font_b.render(self.time_msg_low.format(min=mins, sec=secs), True, (255,255,255))
        else:
            msg_time = font.render(self.time_msg_low.format(min=mins, sec=secs), True, (255,255,255))
        self.window.blit(msg, (10, FIELD_HEIGHT + 5))
        self.window.blit(msg_time, (10 + msg.get_width(), FIELD_HEIGHT + 5))


class Player:

    COLLISION = 4
    OFFSET = 3
    SPEED = 4
    SIZE = 10

    def __init__(self, window):
        self.window = window
        self.image = None # TODO
        self.score = 0
        self.xonii = 2
        self.died_on_this_level = False
        self.x = FIELD_WIDTH // 2
        self.y = 3
        self.speed_x = self.speed_y = 0

        self.min_x = self.min_y = self.max_x = self.max_y = None

    def reset_position(self):
        self.x = FIELD_WIDTH // 2
        self.y = 3
        self.speed_x = self.speed_y = 0

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
        self.update_trajectory_extremes(field_bmp)


        if np.array_equal(field_bmp[self.y][self.x], BLACK):
            for j in range(self.x - self.OFFSET, self.x + self.OFFSET):
                for i in range(self.y - self.OFFSET, self.y + self.OFFSET):
                    if np.array_equal(field_bmp[i][j], BLACK):
                        field_bmp[i][j] = RED

        if np.array_equal(field_bmp[self.y][self.x], AQUA) and np.array_equal(
                field_bmp[self.y - self.speed_y][self.x - self.speed_x], RED):
            self.speed_x = 0
            self.speed_y = 0
            return True
        return

    def update_trajectory_extremes(self, field_bmp):
        if np.array_equal(field_bmp[self.y][self.x], AQUA):
            self.reset_trajectory_extremes()
            return
        if not self.min_x or self.x < self.min_x:
            self.min_x = self.x
        if not self.min_y or self.y < self.min_y:
            self.min_y = self.y
        if not self.max_x or self.x > self.max_x:
            self.max_x = self.x
        if not self.max_y or self.y > self.max_y:
            self.max_y = self.y

    def reset_trajectory_extremes(self):
        self.min_x = self.min_y = self.max_x = self.max_y = None

    def direction(self):
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

    def interference(self, white_dots, black_dots):
        for dot in white_dots:
            if abs(dot.x - self.x) + abs(dot.y - self.y) <= self.COLLISION:
                return True
        for dot in black_dots:
            if abs(dot.x - self.x) + abs(dot.y - self.y) <= self.COLLISION:
                return True
        return False

    def draw(self):
        pygame.draw.rect(self.window, (255,255,255), pygame.Rect(self.x - 3, self.y - 3, 5,5))


class Field:

    def __init__(self, window):
        self.window = window
        self.field_bmp = np.zeros(shape=(FIELD_HEIGHT, FIELD_WIDTH))
        self.blue_count = 0
        # self.base_rect = pygame.Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT)

        for i in range(FIELD_HEIGHT):
            for j in range(FIELD_WIDTH):
                if i < BORDER - 1 or j < BORDER - 1 or i >= FIELD_HEIGHT - BORDER or j >= FIELD_WIDTH - BORDER:
                    self.field_bmp[i][j] = AQUA
                    self.blue_count += 1
                else:
                    self.field_bmp[i][j] = BLACK
        self.modified = True

    def draw(self):
        # pygame.draw.rect(self.window, AQUA, self.base_rect)
        surf = pygame.surfarray.make_surface(np.swapaxes(self.field_bmp, 0, 1))
        self.window.blit(surf, (0, 0))

    def flood_fill(self, white_dots, orange_lines):
        # replace reds with blue
        self.blue_count += np.count_nonzero(self.field_bmp == RED)
        self.field_bmp[self.field_bmp == RED] = AQUA
        start_points = [dot for dot in white_dots]
        for line in orange_lines:
            start_points.append(line.end_one)
            start_points.append(line.end_two)

        for point in start_points:
            if self.field_bmp[point.y, point.x] == CHECKED:
                continue
            queue = [[point.x, point.y]]
            while queue:
                x_start, y = queue.pop()
                x = x_start

                while self.field_bmp[y][x] == BLACK:
                    self.field_bmp[y][x] = CHECKED
                    if self.field_bmp[y+1, x] != CHECKED:
                        queue.append([x, y+1])
                    if self.field_bmp[y-1, x] != CHECKED:
                        queue.append([x, y - 1])
                    x = x + 1
                x = x_start - 1
                while self.field_bmp[y][x] == BLACK:
                    self.field_bmp[y][x] = CHECKED
                    if self.field_bmp[y+1, x] != CHECKED:
                        queue.append([x, y+1])
                    if self.field_bmp[y-1, x] != CHECKED:
                        queue.append([x, y - 1])
                    x = x - 1


        # replace black->blue and checked->black
        self.blue_count += np.count_nonzero(self.field_bmp == BLACK)
        self.field_bmp[self.field_bmp == BLACK] = AQUA
        self.field_bmp[self.field_bmp == CHECKED] = BLACK

    def check_interference(self, white_dots):
        for dot in white_dots:
            if np.array_equal(self.field_bmp[dot.y, dot.x], RED):
                return True
        return False

    def clean_red(self):
        self.field_bmp[self.field_bmp == RED] = BLACK


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
        self.bounce_pix = AQUA
        self.bounce_pix_2 = None
        self.image = None

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

    def draw(self):
        pygame.draw.rect(self.window, (255,255,255), pygame.Rect(self.x, self.y, 3,3))

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

    SPEED_MIN = 1
    SPEED_MAX = 3

    def __init__(self, window):
        super().__init__(window)
        self.bounce_pix = AQUA
        self.image = None


class BlackDot(Dot):

    SPEED_MIN = SPEED_MAX = 2

    def __init__(self, window, x=None, y=None):
        self.y = random.randint(0, 3) + (FIELD_HEIGHT - BORDER + 10)
        self.x = BORDER + random.randint(0, FIELD_WIDTH - BORDER - 1)
        super().__init__(window, self.x, self.y)
        self.bounce_pix = BLACK
        self.bounce_pix_2 = RED
        self.image = None

    def draw(self):
        pygame.draw.rect(self.window, (0, 0, 0), pygame.Rect(self.x, self.y, 3,3))


class LineDot(Dot):

    SPEED_MIN = 1
    SPEED_MAX = 1

    def __init__(self, window):
        super().__init__(window)
        self.bounce_pix = AQUA
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

Game()