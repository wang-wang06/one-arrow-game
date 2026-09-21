import pygame
import sys
import math

pygame.init()

# =========================
# 基本设置
# =========================
WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

# =========================
# 颜色
# =========================
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
DARK_GRAY = (60, 65, 75)
GRAY = (130, 135, 145)
LIGHT_GRAY = (235, 238, 243)

BLUE = (75, 120, 190)
LIGHT_BLUE = (220, 232, 250)

GREEN = (80, 170, 110)
LIGHT_GREEN = (220, 245, 225)

RED = (230, 70, 70)
LIGHT_RED = (255, 225, 225)

ORANGE = (240, 150, 60)
YELLOW = (245, 200, 70)

GRID_COLOR = (190, 195, 205)
BOARD_COLOR = (245, 247, 250)

# =========================
# 字体
# =========================
# =========================
# 中文字体
# =========================

FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

font_title = pygame.font.Font(FONT_PATH, 64)
font_big = pygame.font.Font(FONT_PATH, 48)
font_medium = pygame.font.Font(FONT_PATH, 36)
font_normal = pygame.font.Font(FONT_PATH, 28)
font_small = pygame.font.Font(FONT_PATH, 23)

# =========================
# 棋盘
# =========================
ROWS = 7
COLS = 7
CELL_SIZE = 70

BOARD_X = 255
BOARD_Y = 110

# =========================
# 图片
# =========================
DART_IMAGE = pygame.image.load(
    "assets/dart.png"
).convert_alpha()

# 统一箭头尺寸
DART_SIZE = 48

DART_IMAGE = pygame.transform.smoothscale(
    DART_IMAGE,
    (DART_SIZE, DART_SIZE)
)

# 原始图片中的箭头尖端方向为：↙
#
# 因此：
# right → 135°
# up    → -135°
# left  → -45°
# down  → 45°
ANGLE_MAP = {
    "right": 135,
    "up": -135,
    "left": -45,
    "down": 45
}

DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1)
}

# =========================
# 按钮
# =========================
start_button_rect = pygame.Rect(
    350, 250, 300, 80
)

level_button_rects = [
    pygame.Rect(180, 250, 180, 90),
    pygame.Rect(410, 250, 180, 90),
    pygame.Rect(640, 250, 180, 90)
]

restart_button_rect = pygame.Rect(
    350, 380, 300, 70
)

back_select_button_rect = pygame.Rect(
    350, 470, 300, 65
)

# 游戏过程中重新开始当前关卡
restart_game_button_rect = pygame.Rect(
    770, 520, 170, 55
)

# =========================
# 三个关卡
# =========================
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

# =========================
# 游戏状态
# =========================
game_started = False
level_selecting = False
level_finished = False
game_failed = False
all_levels_finished = False

current_level = 1

# 当前关卡剩余箭头
arrows = []

# 飞出中的箭头
moving_arrows = []

# 错误次数
MAX_MISTAKES = 3
mistakes = MAX_MISTAKES

# =========================
# 碰撞反馈
# =========================
collision_effect = None

# 碰撞反馈持续时间
COLLISION_DURATION = 30

# =========================
# 箭头颜色
# =========================
ARROW_COLORS = [
    (70, 120, 190),
    (90, 150, 210),
    (100, 180, 130),
    (235, 150, 70),
    (180, 110, 190),
    (80, 170, 170),
    (220, 100, 100),
    (120, 130, 190)
]


# ============================================================
# 辅助函数
# ============================================================

def draw_text(text, font, color, x, y, center=True):
    """绘制文字"""

    surface = font.render(text, True, color)

    if center:
        rect = surface.get_rect(
            center=(x, y)
        )
    else:
        rect = surface.get_rect(
            topleft=(x, y)
        )

    screen.blit(surface, rect)


def draw_button(rect, text, color=BLUE):
    """绘制按钮"""

    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        button_color = tuple(
            min(255, c + 20) for c in color
        )
    else:
        button_color = color

    pygame.draw.rect(
        screen,
        button_color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        DARK_GRAY,
        rect,
        width=2,
        border_radius=12
    )

    draw_text(
        text,
        font_medium,
        WHITE,
        rect.centerx,
        rect.centery
    )


def get_arrow_angle(direction):
    """获得箭头旋转角度"""

    return ANGLE_MAP[direction]


def get_arrow_color(index):
    """获得箭头颜色"""

    return ARROW_COLORS[index % len(ARROW_COLORS)]


def colorize_image(image, color):
    """
    给箭头图片染色
    """

    result = image.copy()

    color_surface = pygame.Surface(
        result.get_size(),
        pygame.SRCALPHA
    )

    color_surface.fill(color)

    result.blit(
        color_surface,
        (0, 0),
        special_flags=pygame.BLEND_RGBA_MULT
    )

    return result


def draw_arrow(
        row,
        col,
        direction,
        index,
        shake_x=0,
        shake_y=0,
        force_red=False
):
    """
    在棋盘上绘制箭头
    """

    x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    x += shake_x
    y += shake_y

    if force_red:
        color = (245, 65, 65)
    else:
        color = get_arrow_color(index)

    image = colorize_image(
        DART_IMAGE,
        color
    )

    angle = get_arrow_angle(direction)

    rotated = pygame.transform.rotate(
        image,
        angle
    )

    rect = rotated.get_rect(
        center=(x, y)
    )

    screen.blit(
        rotated,
        rect
    )


# ============================================================
# 路径判断
# ============================================================

def is_path_clear(row, col, direction):
    """
    判断箭头前方是否有其他箭头

    True  = 没有阻挡，可以飞出
    False = 有阻挡，不能飞出
    """

    dr, dc = DIRECTION_VECTOR[direction]

    next_row = row + dr
    next_col = col + dc

    while (
        0 <= next_row < ROWS
        and
        0 <= next_col < COLS
    ):

        for arrow in arrows:

            ar, ac, _ = arrow

            if ar == next_row and ac == next_col:
                return False

        next_row += dr
        next_col += dc

    return True


# ============================================================
# 初始化关卡
# ============================================================

def load_level(level):
    """
    加载指定关卡
    """

    global arrows
    global moving_arrows
    global mistakes
    global level_finished
    global game_failed
    global collision_effect

    arrows = [
        tuple(item)
        for item in LEVEL_DATA[level]
    ]

    moving_arrows = []

    mistakes = MAX_MISTAKES

    level_finished = False
    game_failed = False

    collision_effect = None


# ============================================================
# 创建飞出箭头
# ============================================================

def create_flying_arrow(
        row,
        col,
        direction,
        index
):
    """
    创建飞出动画
    """

    return {
        "row": row,
        "col": col,
        "direction": direction,
        "index": index,

        "x": (
            BOARD_X
            + col * CELL_SIZE
            + CELL_SIZE // 2
        ),

        "y": (
            BOARD_Y
            + row * CELL_SIZE
            + CELL_SIZE // 2
        ),

        "speed": 14
    }


# ============================================================
# 更新飞出动画
# ============================================================

def update_flying_arrows():
    """
    更新飞出中的箭头
    """

    for arrow in moving_arrows[:]:

        direction = arrow["direction"]

        speed = arrow["speed"]

        if direction == "up":
            arrow["y"] -= speed

        elif direction == "down":
            arrow["y"] += speed

        elif direction == "left":
            arrow["x"] -= speed

        elif direction == "right":
            arrow["x"] += speed

        # 飞出屏幕后删除
        if (
            arrow["x"] < -100
            or arrow["x"] > WIDTH + 100
            or arrow["y"] < -100
            or arrow["y"] > HEIGHT + 100
        ):
            moving_arrows.remove(arrow)


def draw_flying_arrows():
    """
    绘制飞出动画
    """

    for arrow in moving_arrows:

        direction = arrow["direction"]
        index = arrow["index"]

        color = get_arrow_color(index)

        image = colorize_image(
            DART_IMAGE,
            color
        )

        angle = get_arrow_angle(
            direction
        )

        rotated = pygame.transform.rotate(
            image,
            angle
        )

        rect = rotated.get_rect(
            center=(
                arrow["x"],
                arrow["y"]
            )
        )

        screen.blit(
            rotated,
            rect
        )


# ============================================================
# 碰撞反馈
# ============================================================

def trigger_collision(row, col):
    """
    触发碰撞反馈
    """

    global collision_effect
    global mistakes
    global game_failed

    # 错误次数 -1
    mistakes -= 1

    # 保存碰撞箭头
    collision_effect = {
        "row": row,
        "col": col,
        "timer": COLLISION_DURATION
    }

    # 错误次数耗尽
    if mistakes <= 0:
        mistakes = 0


def update_collision_effect():
    """
    更新碰撞动画
    """

    global collision_effect

    if collision_effect is None:
        return

    collision_effect["timer"] -= 1

    if collision_effect["timer"] <= 0:
        collision_effect = None


def get_collision_shake():
    """
    获取箭头震动偏移
    """

    if collision_effect is None:
        return 0, 0

    timer = collision_effect["timer"]

    if timer <= 0:
        return 0, 0

    # 前 24 帧震动
    if timer > 6:

        if timer % 4 < 2:
            return -6, 0

        return 6, 0

    return 0, 0


def draw_collision_effect():
    """
    绘制明显的碰撞反馈
    """

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

    # =========================
    # 1. 红色闪烁格子
    # =========================

    # 闪烁效果
    if timer % 6 < 4:

        pygame.draw.rect(
            screen,
            (255, 70, 70),
            (
                x + 3,
                y + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            ),
            width=5,
            border_radius=8
        )

    # =========================
    # 2. 半透明红色背景
    # =========================

    overlay = pygame.Surface(
        (CELL_SIZE, CELL_SIZE),
        pygame.SRCALPHA
    )

    alpha = 70

    overlay.fill(
        (255, 60, 60, alpha)
    )

    screen.blit(
        overlay,
        (x, y)
    )

    # =========================
    # 3. 顶部警告文字
    # =========================

    if timer > 0:

        draw_text(
            "前方有阻挡！",
            font_big,
            RED,
            WIDTH // 2,
            55
        )

        draw_text(
            "错误次数 -1",
            font_normal,
            RED,
            WIDTH // 2,
            85
        )


# ============================================================
# 绘制棋盘
# ============================================================

def draw_board():
    """
    绘制棋盘和箭头
    """

    # 棋盘背景
    board_rect = pygame.Rect(
        BOARD_X,
        BOARD_Y,
        COLS * CELL_SIZE,
        ROWS * CELL_SIZE
    )

    pygame.draw.rect(
        screen,
        BOARD_COLOR,
        board_rect,
        border_radius=8
    )

    # 网格
    for row in range(ROWS):

        for col in range(COLS):

            rect = pygame.Rect(
                BOARD_X + col * CELL_SIZE,
                BOARD_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                rect,
                width=1
            )

    # 绘制箭头
    for index, arrow in enumerate(arrows):

        row, col, direction = arrow

        shake_x = 0
        shake_y = 0

        force_red = False

        # 当前正在碰撞的箭头
        if collision_effect is not None:

            if (
                collision_effect["row"] == row
                and
                collision_effect["col"] == col
            ):

                shake_x, shake_y = (
                    get_collision_shake()
                )

                force_red = True

        draw_arrow(
            row,
            col,
            direction,
            index,
            shake_x,
            shake_y,
            force_red
        )


# ============================================================
# 点击箭头
# ============================================================

def handle_arrow_click(mouse_pos):
    """
    处理玩家点击箭头
    """

    global level_finished
    global game_failed

    # 如果正在碰撞反馈，不处理新的箭头点击
    if collision_effect is not None:
        return

    clicked_arrow = None
    clicked_index = -1

    for index, arrow in enumerate(arrows):

        row, col, direction = arrow

        rect = pygame.Rect(
            BOARD_X + col * CELL_SIZE,
            BOARD_Y + row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        if rect.collidepoint(mouse_pos):

            clicked_arrow = arrow
            clicked_index = index
            break

    if clicked_arrow is None:
        return

    row, col, direction = clicked_arrow

    # ========================================================
    # 情况一：前方没有阻挡
    # ========================================================

    if is_path_clear(
        row,
        col,
        direction
    ):

        moving_arrow = create_flying_arrow(
            row,
            col,
            direction,
            clicked_index
        )

        moving_arrows.append(
            moving_arrow
        )

        # 从棋盘中删除
        arrows.pop(clicked_index)

        # 检查是否全部清除
        if len(arrows) == 0:
            level_finished = True

    # ========================================================
    # 情况二：前方有阻挡
    # ========================================================

    else:

        trigger_collision(
            row,
            col
        )

        # 注意：
        # 这里绝对不能 arrows.pop()
        #
        # 所以箭头会继续留在棋盘上


# ============================================================
# 画开始界面
# ============================================================

def draw_start_screen():

    screen.fill(WHITE)

    draw_text(
        "一箭又一箭",
        font_title,
        DARK_GRAY,
        WIDTH // 2,
        120
    )

    draw_text(
        "箭头解谜小游戏",
        font_normal,
        GRAY,
        WIDTH // 2,
        170
    )

    # 游戏规则
    rule_rect = pygame.Rect(
        250,
        365,
        500,
        120
    )

    pygame.draw.rect(
        screen,
        LIGHT_BLUE,
        rule_rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        BLUE,
        rule_rect,
        width=2,
        border_radius=12
    )

    draw_text(
        "游戏规则",
        font_medium,
        BLUE,
        WIDTH // 2,
        390
    )

    draw_text(
        "点击箭头，若前方没有阻挡，箭头即可飞出",
        font_small,
        DARK_GRAY,
        WIDTH // 2,
        425
    )

    draw_text(
        "若前方有其他箭头，则无法飞出并扣除一次错误",
        font_small,
        DARK_GRAY,
        WIDTH // 2,
        455
    )

    draw_button(
        start_button_rect,
        "进入游戏",
        BLUE
    )


# ============================================================
# 选关界面
# ============================================================

def draw_level_select_screen():

    screen.fill(WHITE)

    draw_text(
        "选择关卡",
        font_title,
        DARK_GRAY,
        WIDTH // 2,
        120
    )

    draw_text(
        "请选择一个关卡开始游戏",
        font_normal,
        GRAY,
        WIDTH // 2,
        175
    )

    for i, rect in enumerate(
        level_button_rects
    ):

        draw_button(
            rect,
            f"第 {i + 1} 关",
            BLUE
        )

    draw_text(
        "共 3 个关卡",
        font_small,
        GRAY,
        WIDTH // 2,
        390
    )


# ============================================================
# 游戏界面
# ============================================================

def draw_game_screen():

    screen.fill(WHITE)

    # 标题
    draw_text(
        f"第 {current_level} 关",
        font_big,
        DARK_GRAY,
        WIDTH // 2,
        45
    )

    # 剩余箭头
    draw_text(
        f"剩余箭头：{len(arrows)}",
        font_normal,
        DARK_GRAY,
        120,
        125
    )

    # 错误次数
    mistakes_color = (
        RED if mistakes == 1
        else DARK_GRAY
    )

    draw_text(
        f"剩余错误次数：{mistakes}",
        font_normal,
        mistakes_color,
        125,
        165
    )

    # 棋盘
    draw_board()

    # 游戏中的重新开始按钮
    draw_button(
        restart_game_button_rect,
        "重新开始",
        BLUE
    )

    # 操作提示
    draw_text(
        "点击箭头使其飞出",
        font_small,
        GRAY,
        855,
        455
    )

    # 碰撞反馈
    draw_collision_effect()

    # 飞出动画
    draw_flying_arrows()


# ============================================================
# 关卡完成界面
# ============================================================

def draw_level_finished_screen():

    screen.fill(WHITE)

    draw_text(
        "关卡完成！",
        font_title,
        GREEN,
        WIDTH // 2,
        170
    )

    draw_text(
        f"第 {current_level} 关已成功通关",
        font_medium,
        DARK_GRAY,
        WIDTH // 2,
        235
    )

    if current_level < 3:

        draw_button(
            back_select_button_rect,
            "进入下一关",
            GREEN
        )

    else:

        draw_button(
            back_select_button_rect,
            "查看通关结果",
            GREEN
        )


# ============================================================
# 失败界面
# ============================================================

def draw_failed_screen():

    screen.fill(WHITE)

    draw_text(
        "挑战失败",
        font_title,
        RED,
        WIDTH // 2,
        170
    )

    draw_text(
        "错误次数已经用完",
        font_medium,
        DARK_GRAY,
        WIDTH // 2,
        235
    )

    draw_button(
        restart_button_rect,
        "重新挑战",
        BLUE
    )

    draw_button(
        back_select_button_rect,
        "返回选关",
        DARK_GRAY
    )


# ============================================================
# 全部通关界面
# ============================================================

def draw_all_finished_screen():

    screen.fill(WHITE)

    draw_text(
        "恭喜通关！",
        font_title,
        GREEN,
        WIDTH // 2,
        170
    )

    draw_text(
        "你已经完成全部 3 个关卡",
        font_medium,
        DARK_GRAY,
        WIDTH // 2,
        235
    )

    draw_button(
        restart_button_rect,
        "重新开始",
        BLUE
    )

    draw_button(
        back_select_button_rect,
        "返回选关",
        DARK_GRAY
    )


# ============================================================
# 主程序
# ============================================================

load_level(1)

running = True

while running:

    clock.tick(60)

    # ========================================================
    # 事件处理
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # 鼠标点击
        # ====================================================

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                continue

            mouse_pos = event.pos

            # ================================================
            # 开始界面
            # ================================================

            if not game_started:

                if start_button_rect.collidepoint(
                    mouse_pos
                ):

                    game_started = True
                    level_selecting = True

            # ================================================
            # 选关界面
            # ================================================

            elif level_selecting:

                for i, rect in enumerate(
                    level_button_rects
                ):

                    if rect.collidepoint(
                        mouse_pos
                    ):

                        current_level = i + 1

                        load_level(
                            current_level
                        )

                        level_selecting = False

                        break

            # ================================================
            # 游戏失败
            # ================================================

            elif game_failed:

                if restart_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                    continue

                if back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    level_selecting = True
                    game_failed = False

                    continue

            # ================================================
            # 全部通关
            # ================================================

            elif all_levels_finished:

                if restart_button_rect.collidepoint(
                    mouse_pos
                ):

                    current_level = 1

                    load_level(
                        current_level
                    )

                    all_levels_finished = False
                    level_selecting = False
                    game_started = True

                    continue

                if back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    current_level = 1

                    load_level(
                        current_level
                    )

                    all_levels_finished = False
                    level_selecting = True
                    game_started = True

                    continue

            # ================================================
            # 关卡完成
            # ================================================

            elif level_finished:

                if back_select_button_rect.collidepoint(
                    mouse_pos
                ):

                    if current_level < 3:

                        current_level += 1

                        load_level(
                            current_level
                        )

                        level_finished = False

                    else:

                        level_finished = False
                        all_levels_finished = True

            # ================================================
            # 正常游戏
            # ================================================

            else:

                # 游戏中的重新开始
                if restart_game_button_rect.collidepoint(
                    mouse_pos
                ):

                    load_level(
                        current_level
                    )

                    continue

                # 点击箭头
                handle_arrow_click(
                    mouse_pos
                )

                # 错误次数耗尽
                if mistakes <= 0:

                    game_failed = True

    # ========================================================
    # 更新
    # ========================================================

    update_flying_arrows()

    update_collision_effect()

    # ========================================================
    # 绘制
    # ========================================================

    if not game_started:

        draw_start_screen()

    elif level_selecting:

        draw_level_select_screen()

    elif game_failed:

        draw_failed_screen()

    elif all_levels_finished:

        draw_all_finished_screen()

    elif level_finished:

        draw_level_finished_screen()

    else:

        draw_game_screen()

    pygame.display.flip()


pygame.quit()
sys.exit()