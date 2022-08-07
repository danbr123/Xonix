import pygame
import os
import time

from GameDefs import *
from Dot import BlackDot, WhiteDot, OrangeLine
from Field import Field
from Player import Player


pygame.init()
pygame.display.set_caption("Xonix32 ripoff by Dan")
pygame.font.init()

# fonts
courer_regular = pygame.font.match_font("Courier", bold=False)
courer_bold = pygame.font.match_font("Courier", bold=True)
font = pygame.font.Font(courer_regular, 11)
font_b = pygame.font.Font(courer_bold, 11)
font_b2 = pygame.font.Font(courer_bold, 22)


class Game:

    def __init__(self):
        # init pygame stuff
        self._running = True
        self.size = self.width, self.height = WIDTH, HEIGHT
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.size)

        self.player = Player(self.window)
        self.status_bar = StatusBar(self.window)
        self.level = 0

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

        self.is_paused = False
        self.pause_time = 0
        self.pause_start = 0

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                if self.is_paused:
                    self.is_paused = False
                    self.pause_time += time.time() - self.pause_start
                else:
                    self.is_paused = True
                    self.pause_start = time.time()



    def on_loop(self):
        if not self.show_score and not self.is_paused:
            if self.show_ready:
                self.show_ready = False
                time.sleep(2)
                self.start_time = time.time()
            else:
                self.time_remaining = int(self.time_limit - (time.time() - self.start_time) + self.pause_time)
            self.field.update_blue_count()
            self.percent_complete = 100 * (self.field.blue_count / TOTAL_SQUARES)
            if self.player.update(self.field.field_bmp):
                self.field.flood_fill(self.white_dots, self.orange_lines)
                self.field.update_blue_count()
                self.percent_complete = 100 * (self.field.blue_count / TOTAL_SQUARES)
                if self.percent_complete > MIN_PERCENT_FOR_WIN:
                    self.player.update_score(self.time_remaining, self.time_limit)
                    if self.level == MAX_LEVEL:
                        self.congrats = True
                    else:
                        self.init_next_level()
            for dot in self.white_dots:
                dot.update(self.field.field_bmp)
            for dot in self.black_dots:
                dot.update(self.field.field_bmp)
            for line in self.orange_lines:
                line.update(self.field.field_bmp)

            if self.player.interference(self.white_dots, self.black_dots) or self.field.check_interference(self.white_dots) or self.time_remaining <= 0:
                time.sleep(2)
                for dot in self.black_dots:
                    dot.reset_position()
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
            if keys_pressed[pygame.K_ESCAPE] or keys_pressed[pygame.K_RETURN]:
                self._running = False

    def on_render(self):
        self.window.fill((0, 0, 0))
        score_msg = "Your Score is: {score}".format(score=self.player.score)
        if self.congrats:
            msg = font_b2.render("YOU WIN! " + score_msg + score_msg, True, (204, 204, 0))
            msg_rect = msg.get_rect(center=(FIELD_WIDTH // 2, FIELD_HEIGHT // 2))
            self.window.blit(msg, msg_rect)
        elif self.show_score:
            msg = font_b2.render("You Lose. " + score_msg, True, (204, 204, 0))
            msg_rect = msg.get_rect(center=(FIELD_WIDTH // 2, FIELD_HEIGHT // 2))
            self.window.blit(msg, msg_rect)
        else:
            self.field.draw()
            if self.show_ready:
                msg = font_b2.render("Ready...", True, (204, 204, 0))
                msg_rect = msg.get_rect(center=(FIELD_WIDTH // 2, FIELD_HEIGHT // 2))
                self.window.blit(msg, msg_rect)
            elif self.is_paused:
                msg = font_b2.render("Paused", True, (204, 204, 0))
                msg_rect = msg.get_rect(center=(FIELD_WIDTH // 2, FIELD_HEIGHT // 2))
                self.window.blit(msg, msg_rect)
            self.status_bar.draw(self.level, self.player.xonii, self.player.score, self.percent_complete,
                                 self.time_remaining)
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
        self.pause_time = 0
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

        self.status_msg = "Level: {level}   Xonii: {xonii}   Filled: {fill_p}%   Score: {score}   "
        self.time_msg = "Time: {min}:{sec}"
        self.time_msg_low = "Time:{min}:{sec} <<< Low Time!"

    def draw(self, level, xonii, score, filled, time):
        mins = time//60
        secs = time - mins * 60
        msg = font.render(self.status_msg.format(level=level, xonii=xonii, fill_p=round(filled), score=score), True, (255,255,255))
        if mins == 0 and secs < 30:
            msg_time = font_b.render(self.time_msg_low.format(min=mins, sec=secs), True, (255,255,255))
        else:
            msg_time = font.render(self.time_msg.format(min=mins, sec=secs), True, (255,255,255))
        self.window.blit(msg, (10, FIELD_HEIGHT + 5))
        self.window.blit(msg_time, (10 + msg.get_width(), FIELD_HEIGHT + 5))


Game()