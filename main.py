import pygame
import sys
import random

pygame.init()

# =========================
# 游戏窗口
# =========================
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()


# =========================
# 字体
# =========================
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"


# =========================
# 飞镖图片
# =========================
dart_image = pygame.image.load(
    "assets/dart.png"
).convert_alpha()

dart_image = pygame.transform.smoothscale(
    dart_image,
    (50, 50)
)


# =========================
# 飞镖颜色
# =========================
DART_COLORS = [
    (91, 143, 199),     # 雾霾蓝
    (105, 171, 135),    # 鼠尾草绿
    (151, 126, 190),    # 淡紫
    (224, 157, 103),    # 杏橙
    (211, 116, 126),    # 豆沙红
    (92, 169, 173),     # 青绿色
    (190, 151, 92),     # 暖金色
]


# =========================
# 游戏状态
# =========================
game_started = False


# =========================
# 开始界面按钮
# =========================
button_rect = pygame.Rect(
    350,
    250,
    300,
    80
)


# =========================
# 棋盘设置
# =========================
ROWS = 5
COLS = 5

CELL_SIZE = 80

BOARD_X = 300
BOARD_Y = 150


# =========================
# 箭头数据
#
# row, col, direction
#
# direction 表示：
# 飞镖尖端真正朝向的方向
# =========================
arrows = [
    (0, 1, "right"),
    (0, 3, "down"),

    (1, 0, "down"),
    (1, 2, "left"),

    (2, 1, "up"),
    (2, 4, "left"),

    (3, 0, "right"),
    (3, 3, "up"),

    (4, 1, "right"),
    (4, 4, "up"),
]


# =========================
# 每个飞镖随机颜色
# =========================
arrow_colors = [
    random.choice(DART_COLORS)
    for _ in arrows
]


# =========================
# 飞镖颜色处理
# =========================
def colorize_dart(image, color):

    result = image.copy()

    for x in range(result.get_width()):

        for y in range(result.get_height()):

            r, g, b, a = result.get_at((x, y))

            # 只改变飞镖原来的黄色/橙色区域
            if (
                r > 120
                and g > 60
                and b < 120
                and r > b * 1.5
            ):

                brightness = (
                    r + g + b
                ) / 3

                nr = int(
                    color[0]
                    * brightness
                    / 255
                )

                ng = int(
                    color[1]
                    * brightness
                    / 255
                )

                nb = int(
                    color[2]
                    * brightness
                    / 255
                )

                result.set_at(
                    (x, y),
                    (nr, ng, nb, a)
                )

    return result


# =========================
# 路径检测
# =========================
def is_path_clear(row, col, direction):

    """
    从当前飞镖所在位置开始，
    沿着飞镖尖端方向逐格检查。

    True：
        前方没有其他飞镖，可以飞出。

    False：
        前方存在其他飞镖，被挡住。
    """

    # 当前检查的位置
    check_row = row
    check_col = col

    while True:

        # =====================
        # 根据飞镖尖端方向移动一格
        # =====================

        if direction == "right":

            check_col += 1

        elif direction == "left":

            check_col -= 1

        elif direction == "up":

            check_row -= 1

        elif direction == "down":

            check_row += 1

        # =====================
        # 如果已经到达棋盘外
        # =====================

        if (
            check_row < 0
            or check_row >= ROWS
            or check_col < 0
            or check_col >= COLS
        ):

            # 一直没有遇到其他飞镖
            return True

        # =====================
        # 检查当前位置是否存在其他飞镖
        # =====================

        for r, c, d in arrows:

            if r == check_row and c == check_col:

                return False


# =========================
# 绘制飞镖
# =========================
def draw_arrow(
        screen,
        center_x,
        center_y,
        direction,
        color
):

    """
    dart.png 的原始尖端方向为左下 ↙。

    根据这个原始方向进行旋转。
    """

    if direction == "right":

        # ↙ → →
        angle = -135

    elif direction == "up":

        # ↙ → ↑
        angle = -45

    elif direction == "left":

        # ↙ → ←
        angle = 45

    elif direction == "down":

        # ↙ → ↓
        angle = 135

    else:

        angle = 0


    # =====================
    # 改变飞镖颜色
    # =====================
    colored_image = colorize_dart(
        dart_image,
        color
    )


    # =====================
    # 旋转图片
    # =====================
    image = pygame.transform.rotate(
        colored_image,
        angle
    )


    # =====================
    # 设置图片中心
    # =====================
    image_rect = image.get_rect(
        center=(
            center_x,
            center_y
        )
    )


    # =====================
    # 绘制图片
    # =====================
    screen.blit(
        image,
        image_rect
    )


# =========================
# 绘制棋盘
# =========================
def draw_board():

    # =====================
    # 绘制棋盘格
    # =====================
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

            cell_rect = pygame.Rect(
                x + 4,
                y + 4,
                CELL_SIZE - 8,
                CELL_SIZE - 8
            )

            # 棋盘背景
            pygame.draw.rect(
                screen,
                (220, 226, 234),
                cell_rect,
                border_radius=12
            )

            # 棋盘边框
            pygame.draw.rect(
                screen,
                (200, 208, 218),
                cell_rect,
                width=2,
                border_radius=12
            )


    # =====================
    # 绘制所有飞镖
    # =====================
    for index, arrow in enumerate(arrows):

        row, col, direction = arrow

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

        draw_arrow(
            screen,
            center_x,
            center_y,
            direction,
            arrow_colors[index]
        )


# =========================
# 主循环
# =========================
while True:

    # =========================
    # 处理事件
    # =========================
    for event in pygame.event.get():

        # =====================
        # 退出游戏
        # =====================
        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()


        # =====================
        # 鼠标点击
        # =====================
        if event.type == pygame.MOUSEBUTTONDOWN:

            # =================
            # 开始界面
            # =================
            if not game_started:

                if button_rect.collidepoint(
                        event.pos
                ):

                    game_started = True


            # =================
            # 游戏界面
            # =================
            else:

                mouse_x, mouse_y = event.pos

                # =================
                # 遍历所有飞镖
                # =================
                for arrow in arrows:

                    row, col, direction = arrow

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

                    # =================
                    # 判断是否点击飞镖
                    # =================
                    if (
                        abs(
                            mouse_x - center_x
                        ) <= 30
                        and
                        abs(
                            mouse_y - center_y
                        ) <= 30
                    ):

                        # =================
                        # 检测飞镖路径
                        # =================
                        if is_path_clear(
                            row,
                            col,
                            direction
                        ):

                            print(
                                "路径畅通，可以飞出：",
                                arrow
                            )

                        else:

                            print(
                                "路径被挡住：",
                                arrow
                            )

                        # 已经找到点击的飞镖
                        break


    # =========================
    # 开始界面
    # =========================
    if not game_started:

        screen.fill(
            (245, 247, 250)
        )

        # =====================
        # 游戏标题
        # =====================
        font = pygame.font.Font(
            FONT_PATH,
            48
        )

        title = font.render(
            "一箭又一箭",
            True,
            (40, 50, 70)
        )

        title_rect = title.get_rect(
            center=(500, 150)
        )

        screen.blit(
            title,
            title_rect
        )


        # =====================
        # 进入游戏按钮
        # =====================
        pygame.draw.rect(
            screen,
            (70, 130, 180),
            button_rect,
            border_radius=15
        )

        button_font = pygame.font.Font(
            FONT_PATH,
            30
        )

        button_text = button_font.render(
            "进入游戏",
            True,
            (255, 255, 255)
        )

        text_rect = button_text.get_rect(
            center=button_rect.center
        )

        screen.blit(
            button_text,
            text_rect
        )


    # =========================
    # 游戏界面
    # =========================
    else:

        screen.fill(
            (235, 240, 245)
        )


        # =====================
        # 第 1 关
        # =====================
        game_font = pygame.font.Font(
            FONT_PATH,
            32
        )

        game_title = game_font.render(
            "第 1 关",
            True,
            (40, 50, 70)
        )

        game_title_rect = game_title.get_rect(
            center=(500, 70)
        )

        screen.blit(
            game_title,
            game_title_rect
        )


        # =====================
        # 游戏提示
        # =====================
        tip_font = pygame.font.Font(
            FONT_PATH,
            20
        )

        tip_text = tip_font.render(
            "点击尖端方向没有被其他飞镖挡住的飞镖",
            True,
            (90, 100, 115)
        )

        tip_rect = tip_text.get_rect(
            center=(500, 110)
        )

        screen.blit(
            tip_text,
            tip_rect
        )


        # =====================
        # 绘制棋盘
        # =====================
        draw_board()


    # =========================
    # 刷新画面
    # =========================
    pygame.display.flip()

    clock.tick(60)