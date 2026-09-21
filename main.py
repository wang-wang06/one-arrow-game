import pygame
import sys
import math
import os
import time
import copy
import json

pygame.init()

# ============================================================
# 基本设置
# ============================================================

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()


# ============================================================
# 颜色
# ============================================================

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)

GRAY = (120, 120, 120)
LIGHT_GRAY = (235, 238, 242)
DARK_GRAY = (70, 75, 80)

BLUE = (75, 120, 180)
LIGHT_BLUE = (220, 235, 250)

GREEN = (80, 170, 110)

RED = (220, 80, 80)
LIGHT_RED = (255, 225, 225)

YELLOW = (240, 190, 70)

LOCK_GRAY = (180, 180, 180)


# ============================================================
# 中文字体
# ============================================================

FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc"
]

FONT_PATH = None

for path in FONT_PATHS:
    if os.path.exists(path):
        FONT_PATH = path
        break

if FONT_PATH:
    font_title = pygame.font.Font(FONT_PATH, 58)
    font_big = pygame.font.Font(FONT_PATH, 42)
    font_medium = pygame.font.Font(FONT_PATH, 32)
    font_normal = pygame.font.Font(FONT_PATH, 25)
    font_small = pygame.font.Font(FONT_PATH, 20)
    font_score = pygame.font.Font(FONT_PATH, 23)
else:
    font_title = pygame.font.SysFont("simhei", 58)
    font_big = pygame.font.SysFont("simhei", 42)
    font_medium = pygame.font.SysFont("simhei", 32)
    font_normal = pygame.font.SysFont("simhei", 25)
    font_small = pygame.font.SysFont("simhei", 20)
    font_score = pygame.font.SysFont("simhei", 23)


# ============================================================
# 飞镖图片
# ============================================================

DART_IMAGE_PATH = "assets/dart.png"

if not os.path.exists(DART_IMAGE_PATH):
    print("错误：找不到 assets/dart.png")
    pygame.quit()
    sys.exit()

dart_original = pygame.image.load(
    DART_IMAGE_PATH
).convert_alpha()

DART_SIZE = 52

dart_original = pygame.transform.smoothscale(
    dart_original,
    (DART_SIZE, DART_SIZE)
)


# ============================================================
# 棋盘设置
# ============================================================

ROWS = 7
COLS = 7

CELL_SIZE = 70

BOARD_X = 255
BOARD_Y = 110


# ============================================================
# 关卡数据
# ============================================================

LEVEL_DATA = {

    1: [
        (0, 0, "up"),
        (3, 0, "up"),
        (3, 4, "left"),
        (6, 4, "up"),
        (6, 1, "right"),
        (2, 1, "down"),
        (2, 6, "left"),
        (5, 6, "up"),
    ],

    2: [
        (0, 6, "up"),
        (3, 6, "up"),
        (3, 2, "right"),
        (6, 2, "up"),
        (6, 5, "left"),
        (2, 5, "down"),
        (2, 1, "right"),
        (5, 1, "up"),
    ],

    3: [
        (6, 0, "down"),
        (3, 0, "down"),
        (3, 5, "left"),
        (0, 5, "down"),
        (0, 2, "right"),
        (4, 2, "up"),
        (4, 6, "left"),
        (1, 6, "down"),
    ]
}


# ============================================================
# 每个关卡允许的失误次数
# ============================================================

LEVEL_MISTAKES = {
    1: 3,
    2: 4,
    3: 5
}


# ============================================================
# 计分设置
# ============================================================

SCORE_PER_ARROW = 100

MISTAKE_PENALTY = 50

MIN_SCORE = 0


# ============================================================
# 存档设置
# ============================================================

SAVE_FILE = "save.json"


# ============================================================
# 星级评价
# ============================================================

def calculate_stars(elapsed_time, mistakes_used):

    if elapsed_time <= 20 and mistakes_used <= 1:
        return 3

    if elapsed_time <= 35 and mistakes_used <= 3:
        return 2

    return 1


# ============================================================
# 游戏状态
# ============================================================

game_started = False

level_selecting = False

level_finished = False

game_failed = False

all_levels_finished = False


current_level = 1

unlocked_level = 1


# ============================================================
# 游戏对象
# ============================================================

arrows = []

moving_arrows = []


# ============================================================
# 撤销功能
# ============================================================

undo_history = []

MAX_UNDO = 10


# ============================================================
# 提示功能
# ============================================================

hint_arrow = None

HINT_DURATION = 120

hint_timer = 0

hint_message = ""

hint_message_timer = 0


# ============================================================
# 当前剩余失误次数
# ============================================================

mistakes = LEVEL_MISTAKES[current_level]


# ============================================================
# 得分
# ============================================================

score = 0

level_start_time = None

final_time = 0

final_mistakes_used = 0

current_stars = 0


# ============================================================
# 碰撞反馈
# ============================================================

collision_effect = None

COLLISION_DURATION = 30


# ============================================================
# 按钮位置
# ============================================================

# 开始按钮
start_button_rect = pygame.Rect(
    350,
    430,
    300,
    70
)

# 继续游戏按钮
continue_button_rect = pygame.Rect(
    350,
    515,
    300,
    60
)


# 关卡按钮
level_button_rects = [

    pygame.Rect(
        120,
        250,
        210,
        90
    ),

    pygame.Rect(
        395,
        250,
        210,
        90
    ),

    pygame.Rect(
        670,
        250,
        210,
        90
    )
]


# 游戏中重新开始
restart_game_button_rect = pygame.Rect(
    770,
    105,
    170,
    55
)


# 提示按钮
hint_button_rect = pygame.Rect(
    40,
    500,
    165,
    55
)


# 撤销按钮
undo_button_rect = pygame.Rect(
    40,
    570,
    165,
    55
)


# 通关后进入下一关
next_level_button_rect = pygame.Rect(
    350,
    415,
    300,
    65
)


# 返回关卡选择
back_select_button_rect = pygame.Rect(
    350,
    500,
    300,
    60
)


# 失败后重新挑战
restart_button_rect = pygame.Rect(
    350,
    390,
    300,
    65
)


# ============================================================
# 工具函数
# ============================================================

def draw_text(text, font, color, center):

    surface = font.render(
        str(text),
        True,
        color
    )

    rect = surface.get_rect(
        center=center
    )

    screen.blit(
        surface,
        rect
    )


def draw_button(
    rect,
    text,
    font,
    bg_color,
    text_color=WHITE
):

    pygame.draw.rect(
        screen,
        bg_color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (60, 65, 70),
        rect,
        width=2,
        border_radius=12
    )

    draw_text(
        text,
        font,
        text_color,
        rect.center
    )


# ============================================================
# 格式化时间
# ============================================================

def format_time(seconds):

    seconds = max(
        0,
        int(seconds)
    )

    minutes = seconds // 60

    remain_seconds = seconds % 60

    return f"{minutes:02d}:{remain_seconds:02d}"


# ============================================================
# 获取当前计时
# ============================================================

def get_current_elapsed_time():

    if level_start_time is None:
        return 0

    if level_finished or game_failed:
        return final_time

    return time.time() - level_start_time


# ============================================================
# 箭头角度
# ============================================================

def get_arrow_angle(direction):

    angle_map = {

        "right": 135,

        "up": -135,

        "left": -45,

        "down": 45
    }

    return angle_map[direction]


# ============================================================
# 箭头颜色
# ============================================================

ARROW_COLORS = [

    (75, 120, 180),

    (90, 160, 120),

    (210, 140, 70),

    (160, 100, 170),

    (70, 150, 160),

    (190, 100, 100)
]


def get_arrow_color(index):

    return ARROW_COLORS[
        index % len(ARROW_COLORS)
    ]


# ============================================================
# 绘制箭头
# ============================================================

def draw_arrow(
    row,
    col,
    direction,
    index,
    shake_x=0
):

    center_x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
        + shake_x
    )

    center_y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    angle = get_arrow_angle(
        direction
    )

    image = pygame.transform.rotate(
        dart_original,
        angle
    )

    color = get_arrow_color(
        index
    )

    color_surface = pygame.Surface(
        image.get_size(),
        pygame.SRCALPHA
    )

    color_surface.fill(
        (*color, 255)
    )

    image = image.copy()

    image.blit(
        color_surface,
        (0, 0),
        special_flags=pygame.BLEND_RGBA_MULT
    )

    rect = image.get_rect(
        center=(
            center_x,
            center_y
        )
    )

    screen.blit(
        image,
        rect
    )


# ============================================================
# 判断箭头路径
# ============================================================

def is_path_clear(
    row,
    col,
    direction
):

    dr = 0
    dc = 0

    if direction == "up":
        dr = -1

    elif direction == "down":
        dr = 1

    elif direction == "left":
        dc = -1

    elif direction == "right":
        dc = 1

    check_row = row + dr
    check_col = col + dc

    while (
        0 <= check_row < ROWS
        and
        0 <= check_col < COLS
    ):

        for arrow in arrows:

            if (
                arrow["row"] == check_row
                and
                arrow["col"] == check_col
            ):

                return False

        check_row += dr
        check_col += dc

    return True


# ============================================================
# 碰撞处理
# ============================================================

def trigger_collision(
    row,
    col
):

    global mistakes
    global collision_effect
    global score

    mistakes -= 1

    score = max(
        MIN_SCORE,
        score - MISTAKE_PENALTY
    )

    collision_effect = {

        "row": row,

        "col": col,

        "timer": COLLISION_DURATION
    }


def update_collision_effect():

    global collision_effect

    if collision_effect is None:
        return

    collision_effect["timer"] -= 1

    if collision_effect["timer"] <= 0:

        collision_effect = None


def get_collision_shake(
    row,
    col
):

    if collision_effect is None:
        return 0

    if (
        collision_effect["row"] != row
        or
        collision_effect["col"] != col
    ):

        return 0

    timer = collision_effect["timer"]

    return int(
        math.sin(timer * 1.8) * 7
    )


def draw_collision_effect():

    if collision_effect is None:
        return

    row = collision_effect["row"]

    col = collision_effect["col"]

    timer = collision_effect["timer"]

    x = (
        BOARD_X
        + col * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        RED,
        (
            x + 3,
            y + 3,
            CELL_SIZE - 6,
            CELL_SIZE - 6
        ),
        width=4,
        border_radius=8
    )

    alpha = int(
        80
        * timer
        / COLLISION_DURATION
    )

    overlay = pygame.Surface(
        (
            CELL_SIZE,
            CELL_SIZE
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            255,
            60,
            60,
            alpha
        )
    )

    screen.blit(
        overlay,
        (x, y)
    )


# ============================================================
# 飞出动画
# ============================================================

def create_flying_arrow(
    row,
    col,
    direction,
    index
):

    center_x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    center_y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    moving_arrows.append({

        "x": center_x,

        "y": center_y,

        "direction": direction,

        "index": index,

        "speed": 15
    })


def update_flying_arrows():

    for arrow in moving_arrows[:]:

        direction = arrow["direction"]

        if direction == "up":
            arrow["y"] -= arrow["speed"]

        elif direction == "down":
            arrow["y"] += arrow["speed"]

        elif direction == "left":
            arrow["x"] -= arrow["speed"]

        elif direction == "right":
            arrow["x"] += arrow["speed"]

        if (
            arrow["x"] < -100
            or
            arrow["x"] > WIDTH + 100
            or
            arrow["y"] < -100
            or
            arrow["y"] > HEIGHT + 100
        ):

            moving_arrows.remove(
                arrow
            )


def draw_flying_arrows():

    for arrow in moving_arrows:

        angle = get_arrow_angle(
            arrow["direction"]
        )

        image = pygame.transform.rotate(
            dart_original,
            angle
        )

        color = get_arrow_color(
            arrow["index"]
        )

        color_surface = pygame.Surface(
            image.get_size(),
            pygame.SRCALPHA
        )

        color_surface.fill(
            (*color, 255)
        )

        image = image.copy()

        image.blit(
            color_surface,
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        rect = image.get_rect(
            center=(
                arrow["x"],
                arrow["y"]
            )
        )

        screen.blit(
            image,
            rect
        )


# ============================================================
# 保存游戏进度
# ============================================================

def save_game_progress():

    global level_start_time

    if not game_started:
        return

    if level_selecting:
        return

    if all_levels_finished:
        return

    elapsed = get_current_elapsed_time()

    data = {

        "current_level": current_level,

        "unlocked_level": unlocked_level,

        "mistakes": mistakes,

        "score": score,

        "elapsed_time": elapsed,

        "final_time": final_time,

        "final_mistakes_used": final_mistakes_used,

        "current_stars": current_stars,

        "level_finished": level_finished,

        "game_failed": game_failed,

        "arrows": copy.deepcopy(arrows)
    }

    try:

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "保存游戏进度失败：",
            e
        )


# ============================================================
# 读取游戏进度
# ============================================================

def load_game_progress():

    global game_started
    global level_selecting
    global level_finished
    global game_failed
    global all_levels_finished

    global current_level
    global unlocked_level

    global arrows
    global moving_arrows

    global mistakes
    global score

    global level_start_time
    global final_time
    global final_mistakes_used
    global current_stars

    global undo_history
    global collision_effect

    if not os.path.exists(SAVE_FILE):

        return False

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        current_level = int(
            data["current_level"]
        )

        unlocked_level = int(
            data.get(
                "unlocked_level",
                current_level
            )
        )

        mistakes = int(
            data["mistakes"]
        )

        score = int(
            data["score"]
        )

        elapsed = float(
            data.get(
                "elapsed_time",
                0
            )
        )

        final_time = float(
            data.get(
                "final_time",
                0
            )
        )

        final_mistakes_used = int(
            data.get(
                "final_mistakes_used",
                0
            )
        )

        current_stars = int(
            data.get(
                "current_stars",
                0
            )
        )

        arrows = copy.deepcopy(
            data.get(
                "arrows",
                []
            )
        )

        moving_arrows = []

        undo_history = []

        collision_effect = None

        level_finished = bool(
            data.get(
                "level_finished",
                False
            )
        )

        game_failed = bool(
            data.get(
                "game_failed",
                False
            )
        )

        all_levels_finished = False

        game_started = True

        level_selecting = False

        # 根据已经进行的时间恢复计时
        if level_finished or game_failed:

            level_start_time = (
                time.time()
                - final_time
            )

        else:

            level_start_time = (
                time.time()
                - elapsed
            )

        return True

    except Exception as e:

        print(
            "读取游戏进度失败：",
            e
        )

        return False


# ============================================================
# 删除游戏进度
# ============================================================

def delete_game_progress():

    if os.path.exists(SAVE_FILE):

        try:

            os.remove(
                SAVE_FILE
            )

        except Exception as e:

            print(
                "删除存档失败：",
                e
            )


# ============================================================
# 加载关卡
# ============================================================

def load_level(level_number):

    global arrows
    global moving_arrows
    global current_level
    global mistakes
    global level_finished
    global game_failed
    global all_levels_finished
    global collision_effect

    global score
    global level_start_time
    global final_time
    global final_mistakes_used
    global current_stars

    global undo_history

    global hint_arrow
    global hint_timer
    global hint_message
    global hint_message_timer

    current_level = level_number

    arrows = []

    moving_arrows = []

    undo_history = []

    level_finished = False

    game_failed = False

    all_levels_finished = False

    collision_effect = None

    hint_arrow = None

    hint_timer = 0

    hint_message = ""

    hint_message_timer = 0

    mistakes = LEVEL_MISTAKES[
        current_level
    ]

    score = 0

    level_start_time = time.time()

    final_time = 0

    final_mistakes_used = 0

    current_stars = 0

    for index, data in enumerate(
        LEVEL_DATA[current_level]
    ):

        row, col, direction = data

        arrows.append({

            "row": row,

            "col": col,

            "direction": direction,

            "index": index
        })


# ============================================================
# 计算通关结果
# ============================================================

def finish_level():

    global level_finished
    global final_time
    global final_mistakes_used
    global current_stars
    global score

    level_finished = True

    final_time = (
        time.time()
        - level_start_time
    )

    final_mistakes_used = (
        LEVEL_MISTAKES[current_level]
        - mistakes
    )

    current_stars = calculate_stars(
        final_time,
        final_mistakes_used
    )

    if current_stars == 3:

        score += 300

    elif current_stars == 2:

        score += 150

    elif current_stars == 1:

        score += 50

    save_game_progress()


# ============================================================
# 保存撤销状态
# ============================================================

def save_undo_state():

    global undo_history

    state = {

        "arrows": copy.deepcopy(arrows),

        "score": score,

        "mistakes": mistakes,

        "moving_arrows": copy.deepcopy(
            moving_arrows
        ),

        "collision_effect": copy.deepcopy(
            collision_effect
        )
    }

    undo_history.append(
        state
    )

    if len(undo_history) > MAX_UNDO:

        undo_history.pop(0)


# ============================================================
# 执行撤销
# ============================================================

def undo_last_move():

    global arrows
    global score
    global mistakes
    global moving_arrows
    global collision_effect

    global level_finished
    global game_failed

    global hint_arrow
    global hint_timer

    global hint_message
    global hint_message_timer

    if len(undo_history) == 0:

        hint_message = "没有可以撤销的操作"
        hint_message_timer = 120

        return False

    state = undo_history.pop()

    arrows = copy.deepcopy(
        state["arrows"]
    )

    score = state["score"]

    mistakes = state["mistakes"]

    moving_arrows = copy.deepcopy(
        state["moving_arrows"]
    )

    collision_effect = copy.deepcopy(
        state["collision_effect"]
    )

    level_finished = False

    game_failed = False

    hint_arrow = None

    hint_timer = 0

    hint_message = "已撤销上一步操作"

    hint_message_timer = 120

    save_game_progress()

    return True


# ============================================================
# 获取提示
# ============================================================

def show_hint():

    global hint_arrow
    global hint_timer

    global hint_message
    global hint_message_timer

    if len(arrows) == 0:

        hint_arrow = None

        hint_timer = 0

        hint_message = "当前没有可提示的飞镖"

        hint_message_timer = 120

        return

    # 找一个当前可以直接飞出的飞镖
    for arrow in arrows:

        row = arrow["row"]

        col = arrow["col"]

        direction = arrow["direction"]

        if is_path_clear(
            row,
            col,
            direction
        ):

            hint_arrow = arrow

            hint_timer = HINT_DURATION

            hint_message = "黄色高亮的飞镖可以直接飞出"

            hint_message_timer = HINT_DURATION

            return

    # 没有可以直接消除的箭头
    hint_arrow = None

    hint_timer = 0

    hint_message = "当前没有可以直接消除的飞镖"

    hint_message_timer = 120


# ============================================================
# 更新提示
# ============================================================

def update_hint():

    global hint_timer
    global hint_arrow

    global hint_message_timer
    global hint_message

    if hint_timer > 0:

        hint_timer -= 1

        if hint_timer <= 0:

            hint_arrow = None

    if hint_message_timer > 0:

        hint_message_timer -= 1

        if hint_message_timer <= 0:

            hint_message = ""


# ============================================================
# 绘制提示
# ============================================================

def draw_hint_effect():

    if hint_arrow is None:
        return

    row = hint_arrow["row"]

    col = hint_arrow["col"]

    x = (
        BOARD_X
        + col * CELL_SIZE
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        (
            x + 4,
            y + 4,
            CELL_SIZE - 8,
            CELL_SIZE - 8
        ),
        width=5,
        border_radius=10
    )

    overlay = pygame.Surface(
        (
            CELL_SIZE,
            CELL_SIZE
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            255,
            215,
            60,
            35
        )
    )

    screen.blit(
        overlay,
        (x, y)
    )


# ============================================================
# 点击箭头
# ============================================================

def handle_arrow_click(
    mouse_pos
):

    global score

    global hint_arrow
    global hint_timer

    mouse_x, mouse_y = mouse_pos

    clicked_arrow = None

    for arrow in reversed(arrows):

        row = arrow["row"]

        col = arrow["col"]

        x = (
            BOARD_X
            + col * CELL_SIZE
        )

        y = (
            BOARD_Y
            + row * CELL_SIZE
        )

        rect = pygame.Rect(
            x,
            y,
            CELL_SIZE,
            CELL_SIZE
        )

        if rect.collidepoint(
            mouse_x,
            mouse_y
        ):

            clicked_arrow = arrow

            break

    if clicked_arrow is None:
        return

    # 在执行操作之前保存状态
    save_undo_state()

    hint_arrow = None
    hint_timer = 0

    row = clicked_arrow["row"]

    col = clicked_arrow["col"]

    direction = clicked_arrow["direction"]

    index = clicked_arrow["index"]

    if is_path_clear(
        row,
        col,
        direction
    ):

        score += SCORE_PER_ARROW

        create_flying_arrow(
            row,
            col,
            direction,
            index
        )

        arrows.remove(
            clicked_arrow
        )

        if len(arrows) == 0:

            finish_level()

        else:

            save_game_progress()

    else:

        trigger_collision(
            row,
            col
        )

        save_game_progress()


# ============================================================
# 绘制棋盘
# ============================================================

def draw_board():

    board_rect = pygame.Rect(
        BOARD_X,
        BOARD_Y,
        COLS * CELL_SIZE,
        ROWS * CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        (248, 249, 251),
        board_rect,
        border_radius=10
    )

    for row in range(ROWS):

        for col in range(COLS):

            x = (
                BOARD_X
                + col * CELL_SIZE
            )

            y = (
                BOARD_Y
                + row * CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                (220, 224, 230),
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                width=1
            )

    # 先画提示效果
    draw_hint_effect()

    for index, arrow in enumerate(
        arrows
    ):

        row = arrow["row"]

        col = arrow["col"]

        direction = arrow["direction"]

        shake_x = get_collision_shake(
            row,
            col
        )

        draw_arrow(
            row,
            col,
            direction,
            index,
            shake_x
        )

    draw_collision_effect()


# ============================================================
# 开始界面
# ============================================================

def draw_start_screen():

    screen.fill(
        (242, 245, 249)
    )

    draw_text(
        "一箭又一箭",
        font_title,
        DARK_GRAY,
        (
            WIDTH // 2,
            100
        )
    )

    draw_text(
        "方向飞镖消除小游戏",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            165
        )
    )

    # 规则框
    rule_rect = pygame.Rect(
        220,
        225,
        560,
        145
    )

    pygame.draw.rect(
        screen,
        WHITE,
        rule_rect,
        border_radius=14
    )

    pygame.draw.rect(
        screen,
        (210, 215, 220),
        rule_rect,
        width=2,
        border_radius=14
    )

    draw_text(
        "游戏规则",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            255
        )
    )

    draw_text(
        "点击飞镖，前方没有其他飞镖即可飞出",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            305
        )
    )

    draw_text(
        "如果前方有阻挡，则消耗一次失误机会",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            345
        )
    )

    draw_button(
        start_button_rect,
        "进入游戏",
        font_medium,
        BLUE
    )

    # ========================================================
    # 继续游戏按钮
    # ========================================================

    if os.path.exists(SAVE_FILE):

        draw_button(
            continue_button_rect,
            "继续游戏",
            font_medium,
            GREEN
        )

    else:

        draw_button(
            continue_button_rect,
            "暂无存档",
            font_medium,
            LOCK_GRAY
        )


# ============================================================
# 关卡选择
# ============================================================

def draw_level_select_screen():

    screen.fill(
        (242, 245, 249)
    )

    draw_text(
        "选择关卡",
        font_title,
        DARK_GRAY,
        (
            WIDTH // 2,
            85
        )
    )

    draw_text(
        f"当前已解锁：1 - {unlocked_level} 关",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            150
        )
    )

    for i in range(3):

        level_number = i + 1

        rect = level_button_rects[i]

        if level_number <= unlocked_level:

            if level_number == current_level:
                button_color = GREEN
            else:
                button_color = BLUE

            draw_button(
                rect,
                f"第 {level_number} 关",
                font_medium,
                button_color
            )

            draw_text(
                f"允许失误 {LEVEL_MISTAKES[level_number]} 次",
                font_small,
                DARK_GRAY,
                (
                    rect.centerx,
                    375
                )
            )

        else:

            draw_button(
                rect,
                "未解锁",
                font_medium,
                LOCK_GRAY
            )

            draw_text(
                "完成上一关解锁",
                font_small,
                GRAY,
                (
                    rect.centerx,
                    375
                )
            )

    draw_text(
        "完成当前关卡后即可解锁下一关",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            500
        )
    )


# ============================================================
# 游戏界面
# ============================================================

def draw_game_screen():

    screen.fill(
        (242, 245, 249)
    )

    # ========================================================
    # 顶部标题
    # ========================================================

    draw_text(
        f"第 {current_level} 关",
        font_big,
        DARK_GRAY,
        (
            WIDTH // 2,
            42
        )
    )

    # ========================================================
    # 左侧信息区域
    # ========================================================

    info_x = 120

    draw_text(
        "关卡信息",
        font_medium,
        DARK_GRAY,
        (
            info_x,
            125
        )
    )

    draw_text(
        f"得分：{score}",
        font_score,
        BLUE,
        (
            info_x,
            175
        )
    )

    elapsed_time = get_current_elapsed_time()

    draw_text(
        f"时间：{format_time(elapsed_time)}",
        font_score,
        DARK_GRAY,
        (
            info_x,
            215
        )
    )

    draw_text(
        f"剩余飞镖：{len(arrows)}",
        font_score,
        DARK_GRAY,
        (
            info_x,
            255
        )
    )

    draw_text(
        f"剩余失误：{mistakes}",
        font_score,
        RED,
        (
            info_x,
            295
        )
    )

    pygame.draw.line(
        screen,
        (210, 215, 220),
        (45, 330),
        (205, 330),
        width=2
    )

    draw_text(
        "操作说明",
        font_medium,
        DARK_GRAY,
        (
            info_x,
            370
        )
    )

    draw_text(
        "点击飞镖",
        font_small,
        GRAY,
        (
            info_x,
            415
        )
    )

    draw_text(
        "让飞镖向前飞出",
        font_small,
        GRAY,
        (
            info_x,
            450
        )
    )

    # ========================================================
    # 提示按钮
    # ========================================================

    draw_button(
        hint_button_rect,
        "提示",
        font_small,
        YELLOW,
        DARK_GRAY
    )

    # ========================================================
    # 撤销按钮
    # ========================================================

    if len(undo_history) > 0:

        undo_color = BLUE

    else:

        undo_color = LOCK_GRAY

    draw_button(
        undo_button_rect,
        "撤销上一步",
        font_small,
        undo_color
    )

    # ========================================================
    # 重新开始
    # ========================================================

    draw_button(
        restart_game_button_rect,
        "重新开始",
        font_small,
        BLUE
    )

    # ========================================================
    # 棋盘
    # ========================================================

    draw_board()

    draw_flying_arrows()

    # ========================================================
    # 碰撞提示
    # ========================================================

    if collision_effect is not None:

        draw_text(
            "前方有阻挡！",
            font_medium,
            RED,
            (
                WIDTH // 2,
                650
            )
        )

    # ========================================================
    # 提示文字
    # ========================================================

    if hint_message:

        draw_text(
            hint_message,
            font_small,
            YELLOW if hint_arrow is not None else RED,
            (
                WIDTH // 2,
                650
            )
        )


# ============================================================
# 绘制三星评价
# ============================================================

def draw_stars(
    stars,
    center_x,
    center_y
):

    star_size = 42

    gap = 25

    total_width = (
        3 * star_size
        + 2 * gap
    )

    start_x = (
        center_x
        - total_width // 2
        + star_size // 2
    )

    for i in range(3):

        x = (
            start_x
            + i * (
                star_size + gap
            )
        )

        if i < stars:
            color = YELLOW
        else:
            color = (210, 210, 210)

        points = []

        for j in range(10):

            angle = (
                -math.pi / 2
                + j * math.pi / 5
            )

            if j % 2 == 0:
                radius = star_size / 2
            else:
                radius = star_size / 4

            px = (
                x
                + math.cos(angle)
                * radius
            )

            py = (
                center_y
                + math.sin(angle)
                * radius
            )

            points.append(
                (px, py)
            )

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.polygon(
            screen,
            DARK_GRAY,
            points,
            width=1
        )


# ============================================================
# 通关界面
# ============================================================

def draw_level_finished_screen():

    screen.fill(
        (242, 245, 249)
    )

    draw_text(
        "恭喜通关！",
        font_title,
        GREEN,
        (
            WIDTH // 2,
            75
        )
    )

    draw_text(
        f"第 {current_level} 关完成",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            135
        )
    )

    draw_stars(
        current_stars,
        WIDTH // 2,
        200
    )

    draw_text(
        f"{current_stars} 星评价",
        font_normal,
        YELLOW,
        (
            WIDTH // 2,
            250
        )
    )

    result_rect = pygame.Rect(
        320,
        280,
        360,
        110
    )

    pygame.draw.rect(
        screen,
        WHITE,
        result_rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (215, 220, 225),
        result_rect,
        width=2,
        border_radius=12
    )

    draw_text(
        f"最终得分：{score}",
        font_normal,
        BLUE,
        (
            WIDTH // 2,
            315
        )
    )

    draw_text(
        f"完成时间：{format_time(final_time)}",
        font_small,
        DARK_GRAY,
        (
            WIDTH // 2,
            360
        )
    )

    if current_level < 3:

        draw_button(
            next_level_button_rect,
            f"进入第 {current_level + 1} 关",
            font_medium,
            GREEN
        )

    else:

        draw_button(
            next_level_button_rect,
            "完成全部关卡",
            font_medium,
            GREEN
        )

    draw_button(
        back_select_button_rect,
        "返回关卡选择",
        font_normal,
        BLUE
    )


# ============================================================
# 失败界面
# ============================================================

def draw_failed_screen():

    screen.fill(
        (250, 242, 242)
    )

    draw_text(
        "挑战失败",
        font_title,
        RED,
        (
            WIDTH // 2,
            115
        )
    )

    draw_text(
        "失误次数已经用完",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            190
        )
    )

    fail_rect = pygame.Rect(
        320,
        235,
        360,
        105
    )

    pygame.draw.rect(
        screen,
        WHITE,
        fail_rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (225, 210, 210),
        fail_rect,
        width=2,
        border_radius=12
    )

    draw_text(
        f"当前为第 {current_level} 关",
        font_normal,
        DARK_GRAY,
        (
            WIDTH // 2,
            270
        )
    )

    draw_text(
        f"当前得分：{score}",
        font_small,
        BLUE,
        (
            WIDTH // 2,
            315
        )
    )

    draw_button(
        restart_button_rect,
        "重新挑战",
        font_medium,
        RED
    )

    draw_button(
        back_select_button_rect,
        "返回关卡选择",
        font_normal,
        BLUE
    )


# ============================================================
# 全部通关界面
# ============================================================

def draw_all_finished_screen():

    screen.fill(
        (242, 245, 249)
    )

    draw_text(
        "全部通关！",
        font_title,
        GREEN,
        (
            WIDTH // 2,
            125
        )
    )

    draw_text(
        "恭喜你完成了全部三个关卡",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            215
        )
    )

    draw_text(
        "你可以返回关卡选择重新挑战",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            275
        )
    )

    draw_button(
        back_select_button_rect,
        "返回关卡选择",
        font_medium,
        BLUE
    )


# ============================================================
# 主循环
# ============================================================

running = True

while running:

    # ========================================================
    # 事件
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            # 关闭游戏之前自动保存
            save_game_progress()

            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            # =================================================
            # 开始界面
            # =================================================

            if (
                not game_started
                and
                not level_selecting
            ):

                if start_button_rect.collidepoint(
                    mouse_pos
                ):

                    game_started = True

                    level_selecting = True

                elif (
                    continue_button_rect.collidepoint(
                        mouse_pos
                    )
                    and
                    os.path.exists(SAVE_FILE)
                ):

                    if not load_game_progress():

                        print("读取存档失败")

            # =================================================
            # 关卡选择
            # =================================================

            elif (
                game_started
                and
                level_selecting
            ):

                for i, rect in enumerate(
                    level_button_rects
                ):

                    level_number = i + 1

                    if (
                        level_number <= unlocked_level
                        and
                        rect.collidepoint(
                            mouse_pos
                        )
                    ):

                        load_level(
                            level_number
                        )

                        level_selecting = False

                        game_started = True

                        save_game_progress()

                        break

            # =================================================
            # 失败界面
            # =================================================

            elif game_failed:

                if restart_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                    save_game_progress()

                elif back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    game_failed = False

                    level_selecting = True

            # =================================================
            # 全部通关
            # =================================================

            elif all_levels_finished:

                if back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    all_levels_finished = False

                    level_selecting = True

                    delete_game_progress()

            # =================================================
            # 当前关卡通关
            # =================================================

            elif level_finished:

                if next_level_button_rect.collidepoint(
                    mouse_pos
                ):

                    if current_level < 3:

                        next_level = (
                            current_level + 1
                        )

                        unlocked_level = max(
                            unlocked_level,
                            next_level
                        )

                        load_level(
                            next_level
                        )

                        save_game_progress()

                    else:

                        level_finished = False

                        all_levels_finished = True

                        delete_game_progress()

                elif back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    level_finished = False

                    level_selecting = True

            # =================================================
            # 正常游戏
            # =================================================

            elif game_started:

                # 提示
                if hint_button_rect.collidepoint(
                    mouse_pos
                ):

                    show_hint()

                # 撤销
                elif undo_button_rect.collidepoint(
                    mouse_pos
                ):

                    undo_last_move()

                # 重新开始
                elif restart_game_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                    save_game_progress()

                else:

                    handle_arrow_click(
                        mouse_pos
                    )

                    if mistakes <= 0:

                        final_time = (
                            time.time()
                            - level_start_time
                        )

                        game_failed = True

                        collision_effect = None

                        save_game_progress()

    # ========================================================
    # 更新
    # ========================================================

    if (
        game_started
        and
        not level_selecting
        and
        not game_failed
        and
        not all_levels_finished
    ):

        update_flying_arrows()

        update_hint()

        if not level_finished:

            update_collision_effect()

    # ========================================================
    # 绘制
    # ========================================================

    if (
        not game_started
        and
        not level_selecting
    ):

        draw_start_screen()

    elif (
        game_started
        and
        level_selecting
    ):

        draw_level_select_screen()

    elif all_levels_finished:

        draw_all_finished_screen()

    elif game_failed:

        draw_failed_screen()

    elif level_finished:

        draw_level_finished_screen()

    elif game_started:

        draw_game_screen()

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# 退出
# ============================================================

save_game_progress()

pygame.quit()

sys.exit()