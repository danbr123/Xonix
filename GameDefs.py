import numpy as np

# BLACK = np.array((0, 0, 0))
# RED = np.array((255, 102, 102))
# WHITE = np.array((255, 255, 255))
# AQUA = np.array((0, 132, 132))
BLACK = 0
RED = 64
WHITE = 255
AQUA = 130
ORANGE = (132, 132, 0)
FPS = 30
FIELD_WIDTH, FIELD_HEIGHT = 510, 322
TOTAL_SQUARES = FIELD_WIDTH * FIELD_HEIGHT
WIDTH, HEIGHT = FIELD_WIDTH, FIELD_HEIGHT + 25 # 25 is for status bar

CHECKED = 1
BORDER = 20

MAX_LEVEL = 15


def get_time_limit(level, died_on_this_level=False):
    limit = 60 * min(5, level)
    if died_on_this_level:
        limit = limit // 2
    return limit


def get_bonus_points(time_remaining, time_limit, died_on_this_level):
    half_time_limit = time_limit // 2
    if not died_on_this_level and time_remaining > half_time_limit:
        return 10 * (time_remaining - half_time_limit)
    return 0


def get_object_count(level):
    return {
        "white_dots": min(8, 3 + level//3),
        "black_dots": min(4, (1 + (level - 1))//3),
        "orange_lines": min(4, (level + 1)//3)
    }
