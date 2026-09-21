import pygame
import sys
import math
import os
import time
import copy
import random

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
# 随机生成关卡设置
# ============================================================

# 每个关卡随机生成的飞镖数量
LEVEL_ARROW_COUNT = {
    1: 8,
    2: 10,
    3: 12,
    4: 14,
    5: 16,
    6: 18
}

# 每个关卡允许的失误次数
LEVEL_MISTAKES = {
    1: 3,
    2: 4,
    3: 5,
    4: 5,
    5: 6,
    6: 7
}

MAX_LEVEL = 6

# 随机生成最大尝试次数
MAX_GENERATE_ATTEMPTS = 5000


# ============================================================
# 计分设置
# ============================================================

SCORE_PER_ARROW = 100

MISTAKE_PENALTY = 50

MIN_SCORE = 0


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

start_button_rect = pygame.Rect(
    350,
    430,
    300,
    70
)


# 关卡按钮
level_button_rects = [

    pygame.Rect(
        100,
        210,
        240,
        90
    ),

    pygame.Rect(
        380,
        210,
        240,
        90
    ),

    pygame.Rect(
        660,
        210,
        240,
        90
    ),

    pygame.Rect(
        100,
        340,
        240,
        90
    ),

    pygame.Rect(
        380,
        340,
        240,
        90
    ),

    pygame.Rect(
        660,
        340,
        240,
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

def draw_text(
    text,
    font,
    color,
    center
):

    surface = font.render(
        text,
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
# 判断路径是否畅通
# ============================================================

def is_path_clear_for_arrows(
    arrow_list,
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

        for arrow in arrow_list:

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
# 判断随机生成的关卡是否可通关
# ============================================================

def is_generated_level_solvable(
    level_data
):

    remaining = [

        {
            "row": row,
            "col": col,
            "direction": direction
        }

        for row, col, direction
        in level_data
    ]

    while remaining:

        removable = None

        # 找当前可以直接飞出的箭头
        for arrow in remaining:

            if is_path_clear_for_arrows(
                remaining,
                arrow["row"],
                arrow["col"],
                arrow["direction"]
            ):

                removable = arrow

                break

        # 没有可以消除的箭头
        # 说明存在死锁
        if removable is None:

            return False

        remaining.remove(
            removable
        )

    return True


# ============================================================
# 生成随机可通关关卡
# ============================================================

def generate_random_level(
    arrow_count
):

    directions = [
        "up",
        "down",
        "left",
        "right"
    ]

    all_cells = [

        (row, col)

        for row in range(ROWS)

        for col in range(COLS)
    ]

    # --------------------------------------------------------
    # 多次尝试随机生成
    # --------------------------------------------------------

    for attempt in range(
        MAX_GENERATE_ATTEMPTS
    ):

        selected_cells = random.sample(
            all_cells,
            arrow_count
        )

        level_data = []

        for row, col in selected_cells:

            direction = random.choice(
                directions
            )

            level_data.append(
                (
                    row,
                    col,
                    direction
                )
            )

        # 检查是否存在完整通关顺序
        if is_generated_level_solvable(
            level_data
        ):

            return level_data

    # --------------------------------------------------------
    # 如果随机尝试失败
    # 使用一个保证容易生成的备用方案
    # --------------------------------------------------------

    return generate_safe_level(
        arrow_count
    )


# ============================================================
# 备用可通关关卡生成
# ============================================================

def generate_safe_level(
    arrow_count
):

    all_cells = [

        (row, col)

        for row in range(ROWS)

        for col in range(COLS)
    ]

    random.shuffle(
        all_cells
    )

    selected_cells = all_cells[
        :arrow_count
    ]

    level_data = []

    # --------------------------------------------------------
    # 优先让箭头朝棋盘边缘方向
    # --------------------------------------------------------

    for row, col in selected_cells:

        possible = []

        if row > 0:
            possible.append(
                "up"
            )

        if row < ROWS - 1:
            possible.append(
                "down"
            )

        if col > 0:
            possible.append(
                "left"
            )

        if col < COLS - 1:
            possible.append(
                "right"
            )

        random.shuffle(
            possible
        )

        chosen = None

        # 优先寻找不会被当前已生成箭头挡住的方向
        temp_arrows = [
            {
                "row": r,
                "col": c,
                "direction": d
            }

            for r, c, d
            in level_data
        ]

        for direction in possible:

            if is_path_clear_for_arrows(
                temp_arrows,
                row,
                col,
                direction
            ):

                chosen = direction

                break

        if chosen is None:

            chosen = possible[0]

        level_data.append(
            (
                row,
                col,
                chosen
            )
        )

    # 再验证一次
    if is_generated_level_solvable(
        level_data
    ):

        return level_data

    # 最后采用非常稳定的边缘布局
    level_data = []

    cells = [

        (0, 0, "up"),
        (0, 2, "up"),
        (0, 4, "up"),
        (0, 6, "up"),

        (2, 0, "left"),
        (2, 6, "right"),

        (4, 0, "left"),
        (4, 6, "right"),

        (6, 0, "down"),
        (6, 2, "down"),
        (6, 4, "down"),
        (6, 6, "down")
    ]

    random.shuffle(
        cells
    )

    return cells[
        :min(
            arrow_count,
            len(cells)
        )
    ]


# ============================================================
# 判断当前箭头路径
# ============================================================

def is_path_clear(
    row,
    col,
    direction
):

    return is_path_clear_for_arrows(
        arrows,
        row,
        col,
        direction
    )


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
# 加载关卡
# ============================================================

def load_level(
    level_number
):

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

    current_level = level_number

    arrows = []

    moving_arrows = []

    undo_history = []

    hint_arrow = None

    hint_timer = 0

    level_finished = False

    game_failed = False

    all_levels_finished = False

    collision_effect = None

    mistakes = LEVEL_MISTAKES[
        current_level
    ]

    score = 0

    level_start_time = time.time()

    final_time = 0

    final_mistakes_used = 0

    current_stars = 0

    # --------------------------------------------------------
    # 随机生成当前关卡
    # --------------------------------------------------------

    arrow_count = LEVEL_ARROW_COUNT[
        current_level
    ]

    random_level = generate_random_level(
        arrow_count
    )

    # --------------------------------------------------------
    # 创建箭头对象
    # --------------------------------------------------------

    for index, data in enumerate(
        random_level
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


# ============================================================
# 保存撤销状态
# ============================================================

def save_undo_state():

    global undo_history

    state = {

        "arrows":
            copy.deepcopy(arrows),

        "score":
            score,

        "mistakes":
            mistakes,

        "moving_arrows":
            copy.deepcopy(moving_arrows),

        "collision_effect":
            copy.deepcopy(collision_effect)
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

    if len(undo_history) == 0:

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

    return True


# ============================================================
# 获取提示
# ============================================================

def show_hint():

    global hint_arrow
    global hint_timer

    if len(arrows) == 0:

        hint_arrow = None

        hint_timer = 0

        return

    # 优先寻找当前可以直接飞出的箭头
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

            return

    hint_arrow = None

    hint_timer = HINT_DURATION


# ============================================================
# 更新提示
# ============================================================

def update_hint():

    global hint_timer
    global hint_arrow

    if hint_timer <= 0:

        hint_arrow = None

        return

    hint_timer -= 1

    if hint_timer <= 0:

        hint_arrow = None


# ============================================================
# 绘制提示
# ============================================================

def draw_hint_effect():

    if hint_arrow is None:

        return

    # 防止提示对象已经被删除
    if hint_arrow not in arrows:

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

    row = clicked_arrow["row"]

    col = clicked_arrow["col"]

    direction = clicked_arrow["direction"]

    index = clicked_arrow["index"]

    # --------------------------------------------------------
    # 可以飞出
    # --------------------------------------------------------

    if is_path_clear(
        row,
        col,
        direction
    ):

        # 在修改棋盘之前保存撤销状态
        save_undo_state()

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

        # 当前提示箭头被消除
        global hint_arrow
        global hint_timer

        hint_arrow = None
        hint_timer = 0

        if len(arrows) == 0:

            finish_level()

    # --------------------------------------------------------
    # 被阻挡
    # --------------------------------------------------------

    else:

        # 失误也允许撤销
        save_undo_state()

        trigger_collision(
            row,
            col
        )


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

    # 提示效果
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
            70
        )
    )

    draw_text(
        f"当前已解锁：1 - {unlocked_level} 关",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            125
        )
    )

    for i in range(MAX_LEVEL):

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
                f"{LEVEL_ARROW_COUNT[level_number]} 个飞镖",
                font_small,
                DARK_GRAY,
                (
                    rect.centerx,
                    rect.bottom + 25
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
                    rect.bottom + 25
                )
            )

    draw_text(
        "每次进入关卡都会随机生成新的棋盘",
        font_small,
        GRAY,
        (
            WIDTH // 2,
            485
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

        draw_button(
            undo_button_rect,
            "撤销上一步",
            font_small,
            BLUE
        )

    else:

        draw_button(
            undo_button_rect,
            "暂无可撤销",
            font_small,
            LOCK_GRAY
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

    if current_level < MAX_LEVEL:

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
        f"恭喜你完成了全部 {MAX_LEVEL} 个关卡",
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

            # =================================================
            # 当前关卡通关
            # =================================================

            elif level_finished:

                if next_level_button_rect.collidepoint(
                    mouse_pos
                ):

                    if current_level < MAX_LEVEL:

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

                    else:

                        level_finished = False

                        all_levels_finished = True

                elif back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    level_finished = False

                    level_selecting = True

            # =================================================
            # 正常游戏
            # =================================================

            elif game_started:

                # ------------------------------------------------
                # 重新开始
                # ------------------------------------------------

                if restart_game_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                # ------------------------------------------------
                # 提示
                # ------------------------------------------------

                elif hint_button_rect.collidepoint(
                    mouse_pos
                ):

                    show_hint()

                # ------------------------------------------------
                # 撤销
                # ------------------------------------------------

                elif undo_button_rect.collidepoint(
                    mouse_pos
                ):

                    undo_last_move()

                # ------------------------------------------------
                # 点击棋盘
                # ------------------------------------------------

                else:

                    handle_arrow_click(
                        mouse_pos
                    )

                    # ------------------------------------------------
                    # 失误次数耗尽
                    # ------------------------------------------------

                    if mistakes <= 0:

                        final_time = (
                            time.time()
                            - level_start_time
                        )

                        game_failed = True

                        collision_effect = None

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

pygame.quit()

sys.exit()