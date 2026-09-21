import pygame
import sys
import math
import os

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
else:
    font_title = pygame.font.SysFont("simhei", 58)
    font_big = pygame.font.SysFont("simhei", 42)
    font_medium = pygame.font.SysFont("simhei", 32)
    font_normal = pygame.font.SysFont("simhei", 25)
    font_small = pygame.font.SysFont("simhei", 20)


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
# 游戏状态
# ============================================================

game_started = False

level_selecting = False

level_finished = False

game_failed = False

all_levels_finished = False


# 当前关卡
current_level = 1

# 当前已经解锁到第几关
unlocked_level = 1


# ============================================================
# 游戏对象
# ============================================================

arrows = []

moving_arrows = []


# ============================================================
# 当前剩余失误次数
# ============================================================

mistakes = LEVEL_MISTAKES[current_level]


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
    75
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


# 通关后进入下一关
next_level_button_rect = pygame.Rect(
    350,
    350,
    300,
    70
)


# 返回关卡选择
back_select_button_rect = pygame.Rect(
    350,
    455,
    300,
    60
)


# 失败后重新挑战
restart_button_rect = pygame.Rect(
    350,
    350,
    300,
    70
)


# ============================================================
# 工具函数
# ============================================================

def draw_text(text, font, color, center):

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
# 箭头角度
# ============================================================

def get_arrow_angle(direction):

    # dart.png 原始尖端方向为 ↙

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

    mistakes -= 1

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

def load_level(level_number):

    global arrows
    global moving_arrows
    global current_level
    global mistakes
    global level_finished
    global game_failed
    global all_levels_finished
    global collision_effect

    current_level = level_number

    arrows = []

    moving_arrows = []

    level_finished = False

    game_failed = False

    all_levels_finished = False

    collision_effect = None

    mistakes = LEVEL_MISTAKES[
        current_level
    ]

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
# 点击箭头
# ============================================================

def handle_arrow_click(
    mouse_pos
):

    global level_finished

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

    # ========================================================
    # 路径畅通
    # ========================================================

    if is_path_clear(
        row,
        col,
        direction
    ):

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

            level_finished = True

    # ========================================================
    # 路径被阻挡
    # ========================================================

    else:

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

    # 网格
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

    # 箭头
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
        "一镖又一镖",
        font_title,
        DARK_GRAY,
        (
            WIDTH // 2,
            110
        )
    )

    draw_text(
        "方向飞镖消除小游戏",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            175
        )
    )

    # 规则框
    rule_rect = pygame.Rect(
        220,
        230,
        560,
        135
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
            260
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
            340
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

    # 三个关卡
    for i in range(3):

        level_number = i + 1

        rect = level_button_rects[i]

        # 已解锁
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

        # 未解锁
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

    # 底部提示
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
    # 顶部
    # ========================================================

    draw_text(
        f"第 {current_level} 关",
        font_big,
        DARK_GRAY,
        (
            WIDTH // 2,
            45
        )
    )

    # ========================================================
    # 左侧信息
    # ========================================================

    info_x = 120

    draw_text(
        "关卡信息",
        font_medium,
        DARK_GRAY,
        (
            info_x,
            135
        )
    )

    draw_text(
        f"剩余飞镖：{len(arrows)}",
        font_normal,
        DARK_GRAY,
        (
            info_x,
            190
        )
    )

    draw_text(
        f"剩余失误：{mistakes}",
        font_normal,
        RED,
        (
            info_x,
            245
        )
    )

    draw_text(
        f"本关允许：{LEVEL_MISTAKES[current_level]} 次",
        font_small,
        GRAY,
        (
            info_x,
            290
        )
    )

    # 分割线
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

    # 飞行箭头
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
            135
        )
    )

    draw_text(
        f"第 {current_level} 关完成",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            215
        )
    )

    draw_text(
        f"剩余失误次数：{mistakes}",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            270
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
            135
        )
    )

    draw_text(
        "失误次数已经用完",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            215
        )
    )

    draw_text(
        f"当前为第 {current_level} 关",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            270
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
            145
        )
    )

    draw_text(
        "恭喜你完成了全部三个关卡",
        font_medium,
        DARK_GRAY,
        (
            WIDTH // 2,
            235
        )
    )

    draw_text(
        "你可以返回关卡选择重新挑战",
        font_normal,
        GRAY,
        (
            WIDTH // 2,
            295
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

                # 下一关
                if next_level_button_rect.collidepoint(
                    mouse_pos
                ):

                    if current_level < 3:

                        next_level = (
                            current_level + 1
                        )

                        # 解锁下一关
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

                # 返回关卡选择
                elif back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    level_finished = False

                    level_selecting = True

            # =================================================
            # 正常游戏
            # =================================================

            elif game_started:

                # 重新开始当前关卡
                if restart_game_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                else:

                    handle_arrow_click(
                        mouse_pos
                    )

                    # 失误次数耗尽
                    if mistakes <= 0:

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