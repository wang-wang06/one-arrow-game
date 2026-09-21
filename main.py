import pygame
import sys
import math
import os
import time
import copy
import random
import io
import wave
import struct

try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
except Exception:
    pass

pygame.init()

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    audio_available = True
except Exception:
    audio_available = False

# ============================================================
# 基本设置
# ============================================================

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("镖飞哪算哪")
clock = pygame.time.Clock()

# ============================================================
# 【极光主题色】
# ============================================================

# 背景渐变色
BG_TOP = (6, 12, 34)          # 深空靛蓝
BG_HORIZON = (70, 200, 210)   # 极光冰青
BG_BOTTOM = (12, 6, 40)       # 深紫蓝

# 面板
SURFACE = (12, 28, 52)
SURFACE_LIGHT = (22, 46, 78)
SURFACE_DARK = (6, 15, 32)

# 霓虹色
NEON_MAGENTA = (110, 255, 205)   # 极光青绿（主强调色）
NEON_CYAN = (95, 200, 255)       # 冰蓝
NEON_YELLOW = (185, 255, 140)    # 荧绿
NEON_PURPLE = (170, 125, 255)    # 星云紫
NEON_ORANGE = (100, 235, 245)    # 冰青
NEON_GREEN = (140, 255, 180)     # 薄荷绿

# 主题别名（保持代码统一）
NEON_PINK = NEON_MAGENTA
NEON_AMBER = NEON_YELLOW
NEON_LIME = NEON_GREEN

# 文字
TEXT_PRIMARY = (235, 250, 255)
TEXT_SECONDARY = (170, 210, 235)
TEXT_DIM = (110, 150, 185)

# 按钮
BTN_FILL = (14, 32, 58)
BTN_FILL_LIGHT = (24, 48, 80)

LOCK_GRAY = (58, 78, 105)

# 飞镖配色：极光霓虹
ARROW_COLORS = [
    (100, 230, 255),   # 冰蓝
    (140, 255, 190),   # 极光绿
    (185, 130, 255),   # 星云紫
    (255, 210, 110),   # 暖金
    (80, 255, 225),    # 青碧
    (255, 140, 210),   # 极光粉
]


# 中文字体
# ============================================================

# 使用相对路径加载字体文件
FONT_PATH = os.path.join("assets", "simhei.ttf")

# 备用字体路径（防止 assets 下忘记放字体导致直接崩溃，仅供容错）
FALLBACK_FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",  # macOS 备用
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"  # Linux 备用
]

# 检查 assets 下的字体是否存在
if not os.path.exists(FONT_PATH):
    print(f"警告：未找到 {FONT_PATH}，尝试使用系统字体...")
    FONT_PATH = None
    for p in FALLBACK_FONT_PATHS:
        if os.path.exists(p):
            FONT_PATH = p
            break

if FONT_PATH:
    font_title = pygame.font.Font(FONT_PATH, 58)
    font_big = pygame.font.Font(FONT_PATH, 42)
    font_medium = pygame.font.Font(FONT_PATH, 32)
    font_normal = pygame.font.Font(FONT_PATH, 25)
    font_small = pygame.font.Font(FONT_PATH, 20)
    font_score = pygame.font.Font(FONT_PATH, 23)
    font_tiny = pygame.font.Font(FONT_PATH, 16)
    font_pop = pygame.font.Font(FONT_PATH, 26)
else:
    # 如果连系统字体都没有，只能退回默认字体（会显示方块乱码）
    print("错误：未找到任何可用中文字体，中文可能显示为方块。")
    font_title = pygame.font.SysFont("simhei", 58)
    font_big = pygame.font.SysFont("simhei", 42)
    font_medium = pygame.font.SysFont("simhei", 32)
    font_normal = pygame.font.SysFont("simhei", 25)
    font_small = pygame.font.SysFont("simhei", 20)
    font_score = pygame.font.SysFont("simhei", 23)
    font_tiny = pygame.font.SysFont("simhei", 16)
    font_pop = pygame.font.SysFont("simhei", 26)

# ============================================================
# 飞镖图片
# ============================================================

DART_IMAGE_PATH = "assets/dart.png"

if not os.path.exists(DART_IMAGE_PATH):
    print("错误：找不到 assets/dart.png")
    pygame.quit()
    sys.exit()

DART_SIZE = 44

dart_original = pygame.image.load(DART_IMAGE_PATH).convert_alpha()
dart_original = pygame.transform.smoothscale(dart_original, (DART_SIZE, DART_SIZE))

# ============================================================
# 程序化音效
# ============================================================

def generate_sweep_sound(f_start, f_end, duration, volume=0.3,
                         decay=4.0, waveform="sine"):
    if not audio_available:
        return None
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        if n_samples <= 0:
            return None
        samples = []
        phase = 0.0
        for i in range(n_samples):
            t = i / n_samples
            freq = f_start + (f_end - f_start) * t
            phase += 2 * math.pi * freq / sample_rate
            if waveform == "square":
                v = 1.0 if math.sin(phase) > 0 else -1.0
            else:
                v = math.sin(phase)
            env = math.exp(-decay * t) * (1 - math.exp(-100 * t))
            samples.append(int(v * env * volume * 32767))
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(struct.pack('<' + 'h' * n_samples, *samples))
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    except Exception:
        return None

def generate_sequence_sound(freqs, note_dur, volume=0.3, decay=5.0):
    if not audio_available:
        return None
    try:
        sample_rate = 22050
        samples = []
        for freq in freqs:
            n = int(sample_rate * note_dur)
            phase = 0.0
            for i in range(n):
                t = i / n
                phase += 2 * math.pi * freq / sample_rate
                env = math.exp(-decay * t) * (1 - math.exp(-100 * t))
                samples.append(int(math.sin(phase) * env * volume * 32767))
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    except Exception:
        return None

snd_shoot = generate_sweep_sound(800, 1700, 0.18, volume=0.22, decay=6.5)
snd_collision = generate_sweep_sound(240, 70, 0.32, volume=0.32, decay=3.2)
snd_hint = generate_sweep_sound(700, 1150, 0.16, volume=0.18, decay=5.5)
snd_undo = generate_sweep_sound(1050, 500, 0.22, volume=0.22, decay=4.5)
snd_click = generate_sweep_sound(1200, 1200, 0.06, volume=0.14, decay=10.0)
snd_score = generate_sweep_sound(1400, 2000, 0.10, volume=0.14, decay=9.0)
snd_win = generate_sequence_sound([523, 659, 784, 1047], 0.14, volume=0.28, decay=4.0)
snd_fail = generate_sequence_sound([523, 440, 349, 262], 0.16, volume=0.28, decay=4.0)
snd_star = generate_sweep_sound(900, 1600, 0.13, volume=0.20, decay=7.5)

def play_sound(snd):
    if snd is not None and audio_available:
        try:
            snd.play()
        except Exception:
            pass

# ============================================================
# 棋盘设置
# ============================================================

ROWS = 7
COLS = 7
CELL_SIZE = 70
BOARD_X = 255
BOARD_Y = 110
BOARD_FRAME = 20

# 地平线位置（背景与网格用）
HORIZON_Y = int(HEIGHT * 0.62)

# ============================================================
# 关卡设置
# ============================================================

LEVEL_ARROW_COUNT = {1: 8, 2: 10, 3: 12, 4: 14, 5: 16, 6: 18}
LEVEL_MISTAKES = {1: 3, 2: 4, 3: 5, 4: 5, 5: 6, 6: 7}
MAX_LEVEL = 6
MAX_GENERATE_ATTEMPTS = 5000

SCORE_PER_ARROW = 100
MISTAKE_PENALTY = 50
MIN_SCORE = 0

# ============================================================
# 星级
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

arrows = []
moving_arrows = []

score_popups = []
ripples = []

level_finished_frame = 0

undo_history = []
MAX_UNDO = 10

hint_arrow = None
HINT_DURATION = 120
hint_timer = 0

mistakes = LEVEL_MISTAKES[current_level]

score = 0
level_start_time = None
final_time = 0
final_mistakes_used = 0
current_stars = 0

collision_effect = None
COLLISION_DURATION = 30

# ============================================================
# 按钮位置
# ============================================================

start_button_rect = pygame.Rect(350, 430, 300, 70)

level_button_rects = [
    pygame.Rect(100, 210, 240, 90),
    pygame.Rect(380, 210, 240, 90),
    pygame.Rect(660, 210, 240, 90),
    pygame.Rect(100, 340, 240, 90),
    pygame.Rect(380, 340, 240, 90),
    pygame.Rect(660, 340, 240, 90),
]

restart_game_button_rect = pygame.Rect(770, 105, 170, 55)
hint_button_rect = pygame.Rect(40, 500, 165, 55)
undo_button_rect = pygame.Rect(40, 570, 165, 55)
next_level_button_rect = pygame.Rect(350, 415, 300, 65)
back_select_button_rect = pygame.Rect(350, 500, 300, 60)
restart_button_rect = pygame.Rect(350, 390, 300, 65)

# ============================================================
# 工具函数
# ============================================================

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def shade(color, amount):
    return (clamp(color[0] + amount),
            clamp(color[1] + amount),
            clamp(color[2] + amount))

def draw_text(text, font, color, center):
    s = font.render(text, True, color)
    screen.blit(s, s.get_rect(center=center))

def draw_text_left(text, font, color, left_center):
    s = font.render(text, True, color)
    screen.blit(s, s.get_rect(midleft=left_center))

def draw_text_with_glow(text, font, color, center, glow_color=None,
                        glow_alpha=120, offset=2):
    if glow_color is None:
        glow_color = color
    glow = font.render(text, True, glow_color)
    glow.set_alpha(glow_alpha)
    for ox, oy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset)):
        screen.blit(glow, glow.get_rect(
            center=(center[0] + ox, center[1] + oy)))
    glow2 = font.render(text, True, glow_color)
    glow2.set_alpha(glow_alpha // 2)
    screen.blit(glow2, glow2.get_rect(center=center))
    main = font.render(text, True, color)
    screen.blit(main, main.get_rect(center=center))

def draw_text_centered_with_glow(text, font, color, center_y,
                                  glow_color=None, glow_alpha=120,
                                  offset=2):
    if glow_color is None:
        glow_color = color

    main = font.render(text, True, color)
    bbox = main.get_bounding_rect()
    if bbox.width <= 0 or bbox.height <= 0:
        draw_text_with_glow(text, font, color, (WIDTH // 2, center_y),
                            glow_color, glow_alpha, offset)
        return

    ink_cx = bbox.centerx
    ink_cy = bbox.centery
    blit_x = WIDTH // 2 - ink_cx
    blit_y = center_y - ink_cy

    glow = font.render(text, True, glow_color)
    glow.set_alpha(glow_alpha)
    for ox, oy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset)):
        screen.blit(glow, (blit_x + ox, blit_y + oy))

    glow2 = font.render(text, True, glow_color)
    glow2.set_alpha(glow_alpha // 2)
    screen.blit(glow2, (blit_x, blit_y))

    screen.blit(main, (blit_x, blit_y))

def draw_text_left_with_glow(text, font, color, left_center,
                             glow_color=None, glow_alpha=120, offset=2):
    if glow_color is None:
        glow_color = color
    glow = font.render(text, True, glow_color)
    glow.set_alpha(glow_alpha)
    for ox, oy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset)):
        screen.blit(glow, glow.get_rect(
            midleft=(left_center[0] + ox, left_center[1] + oy)))
    main = font.render(text, True, color)
    screen.blit(main, main.get_rect(midleft=left_center))

# ============================================================
# 动画系统
# ============================================================

def create_score_popup(x, y, value):
    score_popups.append({
        "x": x, "y": y, "value": value,
        "timer": 0, "duration": 55
    })

def update_score_popups():
    for p in score_popups[:]:
        p["timer"] += 1
        if p["timer"] >= p["duration"]:
            score_popups.remove(p)

def draw_score_popups():
    for p in score_popups:
        t = p["timer"] / p["duration"]
        offset_y = -int(46 * (1 - (1 - t) ** 2.4))
        alpha = int(255 * (1 - t ** 1.5))
        if alpha <= 0:
            continue
        text = f"+{p['value']}"
        glow = font_pop.render(text, True, NEON_YELLOW)
        glow.set_alpha(alpha // 3)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            screen.blit(glow, glow.get_rect(
                center=(p["x"] + ox, p["y"] + offset_y + oy)))
        main = font_pop.render(text, True, NEON_YELLOW)
        main.set_alpha(alpha)
        screen.blit(main, main.get_rect(
            center=(p["x"], p["y"] + offset_y)))

def create_ripple(x, y, color, radius_max=42):
    ripples.append({
        "x": x, "y": y, "color": color,
        "timer": 0, "duration": 32,
        "radius_max": radius_max
    })

def update_ripples():
    for r in ripples[:]:
        r["timer"] += 1
        if r["timer"] >= r["duration"]:
            ripples.remove(r)

def draw_ripples():
    for r in ripples:
        t = r["timer"] / r["duration"]
        progress = 1 - (1 - t) ** 2
        radius = int(6 + (r["radius_max"] - 6) * progress)
        alpha = int(180 * (1 - t) ** 1.6)
        if alpha <= 0 or radius <= 0:
            continue
        size = radius * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*r["color"], alpha),
            (size // 2, size // 2), radius, 3
        )
        inner_alpha = alpha // 2
        pygame.draw.circle(
            surf, (*r["color"], inner_alpha),
            (size // 2, size // 2), max(1, radius - 5), 1
        )
        screen.blit(surf, (r["x"] - size // 2, r["y"] - size // 2))

# ============================================================
# 极光背景：渐变 + 星星 + 光轮 + 透视网格
# ============================================================

def build_vapor_sun():
    """极光光轮：渐变 + 横向条纹"""
    radius = 150
    size = radius * 2 + 80
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    scx = scy = size // 2

    # 外层光晕
    for i in range(24):
        a = int(50 * (1 - i / 24) ** 1.7)
        if a <= 0:
            continue
        pygame.draw.circle(surf, (120, 240, 255, a),
                           (scx, scy), radius + i, 2)

    # 光轮圆盘渐变（中心冰白，边缘深青）
    for i in range(radius, 0, -1):
        t = i / radius
        r = int(40 + 170 * (1 - t))
        g = int(115 + 140 * (1 - t))
        b = int(165 + 90 * (1 - t))
        pygame.draw.circle(surf, (r, g, b), (scx, scy), i)

    # 下半部分的横向条纹
    for k in range(10):
        y_off = int(radius * (0.05 + k * 0.09))
        h = 3 + k
        y = scy - radius + y_off
        if y > scy + radius:
            break
        dy = abs(y - scy)
        if dy >= radius:
            continue
        w = int(math.sqrt(radius * radius - dy * dy) * 2) - 16
        if w <= 0:
            continue
        pygame.draw.rect(surf, (8, 20, 42, 230),
                         (scx - w // 2, y, w, h))
    return surf

def build_vapor_grid(w, h):
    """透视网格：垂直线汇聚到消失点"""
    grid = pygame.Surface((w, h), pygame.SRCALPHA)
    horizon = HORIZON_Y
    vanish_x = w // 2

    # 水平线
    for i in range(1, 15):
        t = i / 15
        y = horizon + int((h - horizon) * (t ** 1.9))
        if y >= h:
            break
        a = int(170 * t)
        pygame.draw.line(grid, (*NEON_MAGENTA, a),
                         (0, y), (w, y), 1)

    # 垂直线
    for i in range(-16, 17):
        x_bottom = vanish_x + i * 80
        a = 130
        pygame.draw.line(grid, (*NEON_CYAN, a),
                         (vanish_x, horizon), (x_bottom, h), 1)
    return grid

def build_vapor_stars(w, h):
    """背景星星"""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(888)
    for _ in range(140):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, int(h * 0.58) - 1)
        r = rng.choice((1, 1, 1, 2))
        a = rng.randint(60, 180)
        c = rng.choice((NEON_CYAN, NEON_MAGENTA, TEXT_PRIMARY, NEON_YELLOW))
        pygame.draw.circle(surf, (*c, a), (x, y), r)
    return surf

def build_background_full(w, h):
    # 渐变：深空靛蓝 → 极光冰青 → 深紫蓝
    sw, sh = 200, 140
    small = pygame.Surface((sw, sh))
    horizon_t = 0.62
    for y in range(sh):
        t = y / (sh - 1)
        if t < horizon_t:
            f = (t / horizon_t) ** 1.4
            r = int(BG_TOP[0] + (BG_HORIZON[0] - BG_TOP[0]) * f)
            g = int(BG_TOP[1] + (BG_HORIZON[1] - BG_TOP[1]) * f)
            b = int(BG_TOP[2] + (BG_HORIZON[2] - BG_TOP[2]) * f)
        else:
            f = ((t - horizon_t) / (1 - horizon_t)) ** 0.7
            r = int(BG_HORIZON[0] + (BG_BOTTOM[0] - BG_HORIZON[0]) * f)
            g = int(BG_HORIZON[1] + (BG_BOTTOM[1] - BG_HORIZON[1]) * f)
            b = int(BG_HORIZON[2] + (BG_BOTTOM[2] - BG_HORIZON[2]) * f)
        for x in range(sw):
            small.set_at((x, y), (r, g, b))
    bg = pygame.transform.smoothscale(small, (w, h))

    # 星星
    bg.blit(build_vapor_stars(w, h), (0, 0))

    # 光轮
    sun = build_vapor_sun()
    sun_rect = sun.get_rect(center=(w // 2, HORIZON_Y))
    bg.blit(sun, sun_rect)

    # 透视网格
    bg.blit(build_vapor_grid(w, h), (0, 0))

    return bg

background = build_background_full(WIDTH, HEIGHT)

# ============================================================
# 棋盘表面（冰蓝玻璃 + 霓虹网格）
# ============================================================

def build_board_surface():
    frame = BOARD_FRAME
    board_w = COLS * CELL_SIZE
    board_h = ROWS * CELL_SIZE
    total_w = board_w + frame * 2
    total_h = board_h + frame * 2

    surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

    # 外圈紫色光晕
    for i in range(16):
        a = int(75 * (1 - i / 16) ** 1.8)
        if a <= 0:
            continue
        pygame.draw.rect(
            surf, (*NEON_PURPLE, a),
            pygame.Rect(i // 2, i // 2,
                        total_w - i, total_h - i),
            width=2, border_radius=18
        )

    # 深色外框
    pygame.draw.rect(surf, SURFACE_DARK,
                     (frame - 6, frame - 6,
                      board_w + 12, board_h + 12),
                     border_radius=14)
    # 主面板
    pygame.draw.rect(surf, SURFACE,
                     (frame, frame, board_w, board_h),
                     border_radius=10)

    # 顶部高光
    panel_hl = pygame.Surface((board_w - 4, 30), pygame.SRCALPHA)
    for y in range(30):
        t = y / 30
        a = int(55 * (1 - t))
        pygame.draw.line(panel_hl, (180, 235, 255, a),
                         (0, y), (board_w - 4, y))
    surf.blit(panel_hl, (frame + 2, frame + 2))

    # 格子：冰蓝交错
    for row in range(ROWS):
        for col in range(COLS):
            x = frame + col * CELL_SIZE
            y = frame + row * CELL_SIZE
            if (row + col) % 2 == 0:
                cell_fill = (30, 48, 80)
            else:
                cell_fill = (20, 34, 62)
            pygame.draw.rect(surf, cell_fill,
                             (x + 2, y + 2,
                              CELL_SIZE - 4, CELL_SIZE - 4),
                             border_radius=4)

    # 霓虹网格：青色主，粉色辅
    for row in range(ROWS + 1):
        y = frame + row * CELL_SIZE
        pygame.draw.line(surf, (*NEON_CYAN, 90),
                         (frame, y), (frame + board_w, y), 1)
    for col in range(COLS + 1):
        x = frame + col * CELL_SIZE
        pygame.draw.line(surf, (*NEON_CYAN, 90),
                         (x, frame), (x, frame + board_h), 1)

    # 每格高光
    for row in range(ROWS):
        for col in range(COLS):
            x = frame + col * CELL_SIZE
            y = frame + row * CELL_SIZE
            hl = pygame.Surface((CELL_SIZE - 6, 2), pygame.SRCALPHA)
            hl.fill((190, 235, 255, 60))
            surf.blit(hl, (x + 3, y + 4))
            hl2 = pygame.Surface((2, CELL_SIZE - 6), pygame.SRCALPHA)
            hl2.fill((190, 235, 255, 45))
            surf.blit(hl2, (x + 4, y + 3))

    # 主边框
    pygame.draw.rect(surf, NEON_CYAN,
                     (frame, frame, board_w, board_h),
                     width=2, border_radius=10)
    pygame.draw.rect(surf, (*NEON_MAGENTA, 200),
                     (frame - 4, frame - 4,
                      board_w + 8, board_h + 8),
                     width=1, border_radius=14)

    return surf

board_surface = build_board_surface()

board_shadow = pygame.Surface(
    (board_surface.get_width() + 50,
     board_surface.get_height() + 50),
    pygame.SRCALPHA
)
for i in range(22):
    a = int(150 * (1 - i / 22) ** 1.8)
    if a <= 0:
        continue
    pygame.draw.rect(
        board_shadow, (4, 10, 26, a),
        pygame.Rect(25 - i // 2, 27 - i // 2,
                    board_surface.get_width() + i,
                    board_surface.get_height() + i),
        width=3, border_radius=22
    )

# ============================================================
# 飞镖阴影 / 光晕
# ============================================================

def create_soft_oval(w, h, color, max_alpha=160, layers=16):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    base = max_alpha / layers * 1.8
    for i in range(layers):
        t = i / max(1, layers - 1)
        ew = int(w * (1 - t * 0.55))
        eh = int(h * (1 - t * 0.55))
        if ew <= 0 or eh <= 0:
            continue
        rect = pygame.Rect((w - ew) // 2, (h - eh) // 2, ew, eh)
        a = int(base * (0.3 + t))
        pygame.draw.ellipse(surf, (*color, a), rect)
    return surf

dart_shadow = create_soft_oval(DART_SIZE + 14, 18, (0, 0, 0),
                               max_alpha=180, layers=14)

def create_glow(radius, color, max_alpha=110, ring=2):
    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    r = radius
    while r > 0:
        t = r / radius
        a = int(max_alpha * (1 - t) ** 1.9)
        if a > 0:
            pygame.draw.circle(surf, (*color, a),
                               (radius, radius), r, ring)
        r -= ring
    return surf

GLOW_RADIUS = DART_SIZE // 2 + 12
ARROW_GLOWS = {
    c: create_glow(GLOW_RADIUS, c, max_alpha=130, ring=2)
    for c in ARROW_COLORS
}

# ============================================================
# 染色
# ============================================================

def tint_image(image, color, alpha=255):
    tinted = image.copy()
    cs = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    cs.fill((*color, 255))
    tinted.blit(cs, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if alpha < 255:
        tinted.set_alpha(alpha)
    return tinted

# ============================================================
# 时间 / 角度 / 颜色
# ============================================================

def format_time(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def get_current_elapsed_time():
    if level_start_time is None:
        return 0
    if level_finished or game_failed:
        return final_time
    return time.time() - level_start_time

def get_arrow_angle(direction):
    return {"right": 135, "up": -135, "left": -45, "down": 45}[direction]

def get_arrow_color(index):
    return ARROW_COLORS[index % len(ARROW_COLORS)]

# ============================================================
# 路径 / 可解性
# ============================================================

def is_path_clear_for_arrows(arrow_list, row, col, direction):
    dr = dc = 0
    if direction == "up": dr = -1
    elif direction == "down": dr = 1
    elif direction == "left": dc = -1
    elif direction == "right": dc = 1
    cr, cc = row + dr, col + dc
    while 0 <= cr < ROWS and 0 <= cc < COLS:
        for a in arrow_list:
            if a["row"] == cr and a["col"] == cc:
                return False
        cr += dr
        cc += dc
    return True

def is_generated_level_solvable(level_data):
    remaining = [
        {"row": r, "col": c, "direction": d}
        for r, c, d in level_data
    ]
    while remaining:
        removable = None
        for a in remaining:
            if is_path_clear_for_arrows(
                remaining, a["row"], a["col"], a["direction"]
            ):
                removable = a
                break
        if removable is None:
            return False
        remaining.remove(removable)
    return True

def generate_random_level(arrow_count):
    directions = ["up", "down", "left", "right"]
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
    for _ in range(MAX_GENERATE_ATTEMPTS):
        selected = random.sample(all_cells, arrow_count)
        level_data = [
            (r, c, random.choice(directions)) for r, c in selected
        ]
        if is_generated_level_solvable(level_data):
            return level_data
    return generate_safe_level(arrow_count)

def generate_safe_level(arrow_count):
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
    random.shuffle(all_cells)
    selected = all_cells[:arrow_count]
    level_data = []
    for r, c in selected:
        possible = []
        if r > 0: possible.append("up")
        if r < ROWS - 1: possible.append("down")
        if c > 0: possible.append("left")
        if c < COLS - 1: possible.append("right")
        random.shuffle(possible)
        chosen = None
        temp = [
            {"row": rr, "col": cc, "direction": dd}
            for rr, cc, dd in level_data
        ]
        for d in possible:
            if is_path_clear_for_arrows(temp, r, c, d):
                chosen = d
                break
        if chosen is None:
            chosen = possible[0]
        level_data.append((r, c, chosen))
    if is_generated_level_solvable(level_data):
        return level_data
    cells = [
        (0, 0, "up"), (0, 2, "up"), (0, 4, "up"), (0, 6, "up"),
        (2, 0, "left"), (2, 6, "right"),
        (4, 0, "left"), (4, 6, "right"),
        (6, 0, "down"), (6, 2, "down"), (6, 4, "down"), (6, 6, "down")
    ]
    random.shuffle(cells)
    return cells[:min(arrow_count, len(cells))]

def is_path_clear(row, col, direction):
    return is_path_clear_for_arrows(arrows, row, col, direction)

# ============================================================
# 碰撞
# ============================================================

def trigger_collision(row, col):
    global mistakes, collision_effect, score
    mistakes -= 1
    score = max(MIN_SCORE, score - MISTAKE_PENALTY)
    collision_effect = {"row": row, "col": col, "timer": COLLISION_DURATION}

def update_collision_effect():
    global collision_effect
    if collision_effect is None:
        return
    collision_effect["timer"] -= 1
    if collision_effect["timer"] <= 0:
        collision_effect = None

def get_collision_shake(row, col):
    if collision_effect is None:
        return 0
    if collision_effect["row"] != row or collision_effect["col"] != col:
        return 0
    return int(math.sin(collision_effect["timer"] * 1.8) * 7)

def draw_collision_effect():
    if collision_effect is None:
        return
    row = collision_effect["row"]
    col = collision_effect["col"]
    timer = collision_effect["timer"]
    x = BOARD_X + col * CELL_SIZE
    y = BOARD_Y + row * CELL_SIZE
    pygame.draw.rect(screen, NEON_MAGENTA,
                     (x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6),
                     width=3, border_radius=8)
    a = int(110 * timer / COLLISION_DURATION)
    ov = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    ov.fill((*NEON_MAGENTA, a))
    screen.blit(ov, (x, y))

# ============================================================
# 飞出动画
# ============================================================

def create_flying_arrow(row, col, direction, index):
    cx = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
    cy = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

    if direction == "up":
        tx, ty = cx, -120
    elif direction == "down":
        tx, ty = cx, HEIGHT + 120
    elif direction == "left":
        tx, ty = -120, cy
    else:
        tx, ty = WIDTH + 120, cy

    moving_arrows.append({
        "start_x": cx, "start_y": cy,
        "target_x": tx, "target_y": ty,
        "x": cx, "y": cy,
        "direction": direction,
        "index": index,
        "frame": 0,
        "duration": 42,
        "progress": 0.0,
    })

def update_flying_arrows():
    for a in moving_arrows[:]:
        a["frame"] += 1
        t = a["frame"] / a["duration"]
        if t >= 1.0:
            moving_arrows.remove(a)
            continue
        if t < 0.5:
            eased = 4 * t * t * t
        else:
            eased = 1 - pow(-2 * t + 2, 3) / 2
        a["progress"] = eased
        a["x"] = a["start_x"] + (a["target_x"] - a["start_x"]) * eased
        a["y"] = a["start_y"] + (a["target_y"] - a["start_y"]) * eased

def draw_flying_arrows():
    for a in moving_arrows:
        progress = a.get("progress", 0.0)
        scale = 1.0 - progress * 0.55
        alpha = int(255 * (1 - progress * 0.85))
        if alpha <= 0:
            continue

        angle = get_arrow_angle(a["direction"])
        image = pygame.transform.rotate(dart_original, angle)
        color = get_arrow_color(a["index"])
        image = tint_image(image, color)

        if scale < 0.98:
            w, h = image.get_size()
            nw = max(1, int(w * scale))
            nh = max(1, int(h * scale))
            image = pygame.transform.smoothscale(image, (nw, nh))

        glow = ARROW_GLOWS.get(color)
        if glow is not None and alpha > 40:
            g = glow.copy()
            g.set_alpha(alpha // 2)
            screen.blit(g, g.get_rect(center=(a["x"], a["y"])))

        image.set_alpha(alpha)
        screen.blit(image, image.get_rect(center=(a["x"], a["y"])))

# ============================================================
# 加载关卡 / 结算
# ============================================================

def load_level(level_number):
    global arrows, moving_arrows, current_level, mistakes
    global level_finished, game_failed, all_levels_finished, collision_effect
    global score, level_start_time, final_time, final_mistakes_used, current_stars
    global undo_history, hint_arrow, hint_timer
    global level_finished_frame

    current_level = level_number
    arrows = []
    moving_arrows = []
    score_popups.clear()
    ripples.clear()
    undo_history = []
    hint_arrow = None
    hint_timer = 0
    level_finished = False
    game_failed = False
    all_levels_finished = False
    collision_effect = None
    mistakes = LEVEL_MISTAKES[current_level]
    score = 0
    level_start_time = time.time()
    final_time = 0
    final_mistakes_used = 0
    current_stars = 0
    level_finished_frame = 0

    arrow_count = LEVEL_ARROW_COUNT[current_level]
    random_level = generate_random_level(arrow_count)
    for index, (r, c, d) in enumerate(random_level):
        arrows.append({"row": r, "col": c, "direction": d, "index": index})

def finish_level():
    global level_finished, final_time, final_mistakes_used, current_stars, score
    global level_finished_frame
    level_finished = True
    level_finished_frame = 0
    final_time = time.time() - level_start_time
    final_mistakes_used = LEVEL_MISTAKES[current_level] - mistakes
    current_stars = calculate_stars(final_time, final_mistakes_used)
    if current_stars == 3:
        score += 300
    elif current_stars == 2:
        score += 150
    elif current_stars == 1:
        score += 50
    play_sound(snd_win)

def save_undo_state():
    global undo_history
    undo_history.append({
        "arrows": copy.deepcopy(arrows),
        "score": score,
        "mistakes": mistakes,
        "moving_arrows": copy.deepcopy(moving_arrows),
        "collision_effect": copy.deepcopy(collision_effect)
    })
    if len(undo_history) > MAX_UNDO:
        undo_history.pop(0)

def undo_last_move():
    global arrows, score, mistakes, moving_arrows, collision_effect
    global level_finished, game_failed, hint_arrow, hint_timer
    if not undo_history:
        return False
    state = undo_history.pop()
    arrows = copy.deepcopy(state["arrows"])
    score = state["score"]
    mistakes = state["mistakes"]
    moving_arrows = copy.deepcopy(state["moving_arrows"])
    collision_effect = copy.deepcopy(state["collision_effect"])
    level_finished = False
    game_failed = False
    hint_arrow = None
    hint_timer = 0
    play_sound(snd_undo)
    return True

def show_hint():
    global hint_arrow, hint_timer
    if not arrows:
        hint_arrow = None
        hint_timer = 0
        return
    for a in arrows:
        if is_path_clear(a["row"], a["col"], a["direction"]):
            hint_arrow = a
            hint_timer = HINT_DURATION
            play_sound(snd_hint)
            return
    hint_arrow = None
    hint_timer = HINT_DURATION
    play_sound(snd_hint)

def update_hint():
    global hint_timer, hint_arrow
    if hint_timer <= 0:
        hint_arrow = None
        return
    hint_timer -= 1
    if hint_timer <= 0:
        hint_arrow = None

def draw_hint_effect():
    if hint_arrow is None or hint_arrow not in arrows:
        return
    x = BOARD_X + hint_arrow["col"] * CELL_SIZE
    y = BOARD_Y + hint_arrow["row"] * CELL_SIZE
    pulse = 0.65 + 0.35 * math.sin(hint_timer * 0.35)
    alpha_border = int(230 * pulse)
    alpha_fill = int(85 * pulse)
    border_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*NEON_YELLOW, alpha_border),
                     (4, 4, CELL_SIZE - 8, CELL_SIZE - 8),
                     width=4, border_radius=10)
    screen.blit(border_surf, (x, y))
    fill_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    fill_surf.fill((*NEON_YELLOW, alpha_fill))
    screen.blit(fill_surf, (x, y))

# ============================================================
# 点击处理
# ============================================================

def handle_arrow_click(mouse_pos):
    global score, hint_arrow, hint_timer
    mx, my = mouse_pos
    clicked = None
    for a in reversed(arrows):
        x = BOARD_X + a["col"] * CELL_SIZE
        y = BOARD_Y + a["row"] * CELL_SIZE
        if pygame.Rect(x, y, CELL_SIZE, CELL_SIZE).collidepoint(mx, my):
            clicked = a
            break
    if clicked is None:
        return
    r, c, d = clicked["row"], clicked["col"], clicked["direction"]
    cx = BOARD_X + c * CELL_SIZE + CELL_SIZE // 2
    cy = BOARD_Y + r * CELL_SIZE + CELL_SIZE // 2

    if is_path_clear(r, c, d):
        save_undo_state()
        score += SCORE_PER_ARROW
        color = get_arrow_color(clicked["index"])
        create_flying_arrow(r, c, d, clicked["index"])
        create_ripple(cx, cy, color, radius_max=48)
        create_score_popup(cx, cy - 6, SCORE_PER_ARROW)
        play_sound(snd_shoot)
        play_sound(snd_score)
        arrows.remove(clicked)
        hint_arrow = None
        hint_timer = 0
        if not arrows:
            finish_level()
    else:
        save_undo_state()
        create_ripple(cx, cy, NEON_MAGENTA, radius_max=42)
        play_sound(snd_collision)
        trigger_collision(r, c)

# ============================================================
# 绘制棋盘 / 箭头
# ============================================================

def draw_board():
    screen.blit(board_shadow,
                (BOARD_X - BOARD_FRAME - 25,
                 BOARD_Y - BOARD_FRAME - 25))
    screen.blit(board_surface,
                (BOARD_X - BOARD_FRAME, BOARD_Y - BOARD_FRAME))

    draw_ripples()
    draw_hint_effect()

    for index, a in enumerate(arrows):
        draw_arrow(a["row"], a["col"], a["direction"], index,
                   get_collision_shake(a["row"], a["col"]))

    draw_score_popups()
    draw_collision_effect()

def draw_arrow(row, col, direction, index, shake_x=0):
    cx = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2 + shake_x
    cy = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
    angle = get_arrow_angle(direction)
    image = pygame.transform.rotate(dart_original, angle)
    color = get_arrow_color(index)
    image = tint_image(image, color)

    glow = ARROW_GLOWS.get(color)
    if glow is not None:
        screen.blit(glow, glow.get_rect(center=(cx, cy)))

    screen.blit(dart_shadow, dart_shadow.get_rect(center=(cx, cy + 13)))
    screen.blit(image, image.get_rect(center=(cx, cy)))

# ============================================================
# 顶部霓虹色条
# ============================================================

def draw_top_vapor_bar():
    bar = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
    n = len(ARROW_COLORS)
    for x in range(WIDTH):
        t = x / WIDTH
        idx = t * (n - 1)
        i0 = int(idx)
        i1 = min(n - 1, i0 + 1)
        f = idx - i0
        c = (
            int(ARROW_COLORS[i0][0] * (1 - f) + ARROW_COLORS[i1][0] * f),
            int(ARROW_COLORS[i0][1] * (1 - f) + ARROW_COLORS[i1][1] * f),
            int(ARROW_COLORS[i0][2] * (1 - f) + ARROW_COLORS[i1][2] * f),
        )
        pygame.draw.line(bar, (*c, 230), (x, 0), (x, 3))
    screen.blit(bar, (0, 0))

# ============================================================
# 霓虹按钮
# ============================================================

def draw_button(rect, text, font, accent_color, text_color=None,
                fill_color=None):
    if text_color is None:
        text_color = TEXT_PRIMARY
    if fill_color is None:
        fill_color = BTN_FILL

    # 外光晕
    glow_surf = pygame.Surface(
        (rect.width + 44, rect.height + 44), pygame.SRCALPHA
    )
    for i in range(22):
        a = int(60 * (1 - i / 22) ** 2.2)
        if a <= 0:
            continue
        pygame.draw.rect(
            glow_surf, (*accent_color, a),
            pygame.Rect(22 - i // 2, 22 - i // 2,
                        rect.width + i, rect.height + i),
            width=2, border_radius=11
        )
    screen.blit(glow_surf, (rect.x - 22, rect.y - 22))

    # 深色填充
    pygame.draw.rect(screen, fill_color, rect, border_radius=10)

    # 顶部高光
    grad = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        a = int(45 * (1 - t))
        pygame.draw.line(grad, (255, 255, 255, a),
                         (0, y), (rect.width, y))
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=10)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(grad, rect.topleft)

    # 双色霓虹边框
    pygame.draw.rect(screen, accent_color, rect, width=2, border_radius=10)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(screen, (*accent_color[:3], 255), inner,
                     width=1, border_radius=8)
    # 底部另一色霓虹线
    bottom_line = pygame.Surface((rect.width - 12, 2), pygame.SRCALPHA)
    other_color = NEON_MAGENTA if accent_color != NEON_MAGENTA else NEON_CYAN
    bottom_line.fill((*other_color, 200))
    screen.blit(bottom_line, (rect.x + 6, rect.y + rect.height - 5))

    draw_text_with_glow(text, font, text_color, rect.center,
                        glow_color=accent_color, glow_alpha=150)

# ============================================================
# 开始界面
# ============================================================

START_DECOR_DATA = [
    ("up", ARROW_COLORS[0]),
    ("right", ARROW_COLORS[1]),
    ("down", ARROW_COLORS[2]),
    ("left", ARROW_COLORS[3]),
    ("up", ARROW_COLORS[4]),
    ("right", ARROW_COLORS[5]),
    ("down", ARROW_COLORS[0]),
    ("left", ARROW_COLORS[1]),
    ("up", ARROW_COLORS[2]),
]

_ANGLE_MAP = {"right": 135, "up": -135, "left": -45, "down": 45}

start_decor_arrows = []
for direction, color in START_DECOR_DATA:
    base = pygame.transform.rotate(dart_original, _ANGLE_MAP[direction])
    base = pygame.transform.smoothscale(
        base, (int(DART_SIZE * 1.05), int(DART_SIZE * 1.05)))
    base = tint_image(base, color, 230)
    start_decor_arrows.append(base)

def draw_start_screen():
    screen.blit(background, (0, 0))
    draw_top_vapor_bar()

    # 标题上方装饰线
    for side in (-1, 1):
        base_x = WIDTH // 2 + side * 220
        pygame.draw.line(screen, NEON_CYAN,
                         (base_x, 100), (base_x + side * 80, 100), 2)
        pygame.draw.circle(screen, NEON_MAGENTA,
                           (base_x + side * 88, 100), 4)
        pygame.draw.circle(screen, NEON_CYAN, (base_x, 100), 3)

    # 标题：双色霓虹
    draw_text_with_glow("镖飞哪算哪", font_title, TEXT_PRIMARY,
                        (WIDTH // 2, 100),
                        glow_color=NEON_CYAN, glow_alpha=150, offset=3)

    # 副标题
    draw_text("A U R O R A   ·   E L I M I N A T I O N",
              font_small, NEON_CYAN, (WIDTH // 2, 160))
    draw_text("点击飞镖，让它穿屏而出",
              font_normal, TEXT_SECONDARY, (WIDTH // 2, 192))

    # 规则面板
    rule_rect = pygame.Rect(220, 225, 560, 155)

    rglow = pygame.Surface((rule_rect.width + 40, rule_rect.height + 40),
                           pygame.SRCALPHA)
    for i in range(16):
        a = int(65 * (1 - i / 16) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(rglow, (*NEON_CYAN, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     rule_rect.width + i,
                                     rule_rect.height + i),
                         width=2, border_radius=12)
    screen.blit(rglow, (rule_rect.x - 20, rule_rect.y - 20))

    pygame.draw.rect(screen, SURFACE, rule_rect, border_radius=12)
    for i in range(16):
        a = int(50 * (1 - i / 16))
        if a <= 0:
            continue
        pygame.draw.line(screen, (190, 230, 255, a),
                         (rule_rect.x + 2, rule_rect.y + 2 + i),
                         (rule_rect.right - 2, rule_rect.y + 2 + i))
    pygame.draw.rect(screen, NEON_CYAN, rule_rect,
                     width=2, border_radius=12)
    pygame.draw.rect(screen, (*NEON_MAGENTA, 220),
                     rule_rect.inflate(-8, -8), width=1, border_radius=9)

    for cx, cy in (
        (rule_rect.left + 12, rule_rect.top + 12),
        (rule_rect.right - 12, rule_rect.top + 12),
        (rule_rect.left + 12, rule_rect.bottom - 12),
        (rule_rect.right - 12, rule_rect.bottom - 12)
    ):
        pygame.draw.circle(screen, NEON_MAGENTA, (cx, cy), 4)
        pygame.draw.circle(screen, NEON_CYAN, (cx, cy), 2)

    draw_text_with_glow("游 戏 规 则", font_medium, TEXT_PRIMARY,
                        (WIDTH // 2, 262),
                        glow_color=NEON_MAGENTA, glow_alpha=110)
    draw_text("点击飞镖，前方没有其他飞镖即可飞出",
              font_small, TEXT_SECONDARY, (WIDTH // 2, 312))
    draw_text("如果前方有阻挡，则消耗一次失误机会",
              font_small, TEXT_SECONDARY, (WIDTH // 2, 352))

    draw_button(start_button_rect, "进 入 游 戏",
                font_medium, NEON_MAGENTA)

    # 底部装饰飞镖
    decor_y = 592
    span = 640
    start_x = WIDTH // 2 - span // 2
    step = span // max(1, len(start_decor_arrows) - 1)
    for i, arrow_img in enumerate(start_decor_arrows):
        x = start_x + i * step
        y = decor_y + int(math.sin(i * 0.8) * 14)
        glow_r = 26
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for rr in range(glow_r, 0, -2):
            a = int(70 * (1 - rr / glow_r) ** 2)
            if a <= 0:
                continue
            pygame.draw.circle(glow, (255, 255, 255, a),
                               (glow_r, glow_r), rr, 2)
        screen.blit(glow, glow.get_rect(center=(x, y)))
        screen.blit(arrow_img, arrow_img.get_rect(center=(x, y)))

    draw_text("M O V E   ·   C L E A R   ·   W I N",
              font_small, NEON_YELLOW, (WIDTH // 2, 655))

# ============================================================
# 关卡选择
# ============================================================

def draw_level_select_screen():
    screen.blit(background, (0, 0))
    draw_top_vapor_bar()

    draw_text_with_glow("选 择 关 卡", font_title, TEXT_PRIMARY,
                        (WIDTH // 2, 70),
                        glow_color=NEON_CYAN, glow_alpha=130, offset=3)

    for side in (-1, 1):
        bx = WIDTH // 2 + side * 170
        pygame.draw.line(screen, NEON_CYAN,
                         (bx, 70), (bx + side * 80, 70), 2)
        pygame.draw.circle(screen, NEON_MAGENTA, (bx + side * 88, 70), 3)

    draw_text(f"当前已解锁：1 - {unlocked_level} 关",
              font_small, TEXT_SECONDARY, (WIDTH // 2, 125))

    for i in range(MAX_LEVEL):
        level_number = i + 1
        rect = level_button_rects[i]
        if level_number <= unlocked_level:
            accent = NEON_GREEN if level_number == current_level else NEON_CYAN
            draw_button(rect, f"第 {level_number} 关",
                        font_medium, accent)
            draw_text(f"{LEVEL_ARROW_COUNT[level_number]} 个飞镖",
                      font_small, TEXT_SECONDARY,
                      (rect.centerx, rect.bottom + 25))
        else:
            draw_button(rect, "未 解 锁", font_medium, LOCK_GRAY,
                        text_color=TEXT_DIM)
            draw_text("完成上一关解锁",
                      font_small, TEXT_DIM,
                      (rect.centerx, rect.bottom + 25))

    draw_text("每次进入关卡都会随机生成新的棋盘",
              font_small, TEXT_SECONDARY, (WIDTH // 2, 485))

    pygame.draw.line(screen, (*NEON_CYAN, 220),
                     (WIDTH // 2 - 220, 520), (WIDTH // 2 + 220, 520), 1)
    pygame.draw.circle(screen, NEON_MAGENTA, (WIDTH // 2, 520), 4)

# ============================================================
# 游戏界面
# ============================================================

def draw_game_screen():
    screen.blit(background, (0, 0))
    draw_top_vapor_bar()

    # 顶部关卡标题
    banner_rect = pygame.Rect(WIDTH // 2 - 150, 16, 300, 52)
    bglow = pygame.Surface((banner_rect.width + 40, banner_rect.height + 40),
                           pygame.SRCALPHA)
    for i in range(16):
        a = int(60 * (1 - i / 16) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(bglow, (*NEON_CYAN, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     banner_rect.width + i,
                                     banner_rect.height + i),
                         width=2, border_radius=12)
    screen.blit(bglow, (banner_rect.x - 20, banner_rect.y - 20))

    pygame.draw.rect(screen, SURFACE, banner_rect, border_radius=12)
    for i in range(16):
        a = int(55 * (1 - i / 16))
        if a <= 0:
            continue
        pygame.draw.line(screen, (190, 230, 255, a),
                         (banner_rect.x + 2, banner_rect.y + 2 + i),
                         (banner_rect.right - 2, banner_rect.y + 2 + i))
    pygame.draw.rect(screen, NEON_CYAN, banner_rect,
                     width=2, border_radius=12)

    draw_text_with_glow(f"第 {current_level} 关", font_big, TEXT_PRIMARY,
                        (WIDTH // 2, 42),
                        glow_color=NEON_CYAN, glow_alpha=120, offset=2)

    # 左侧信息面板
    panel_rect = pygame.Rect(28, 98, 196, 400)
    pglow = pygame.Surface((panel_rect.width + 40, panel_rect.height + 40),
                           pygame.SRCALPHA)
    for i in range(16):
        a = int(50 * (1 - i / 16) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(pglow, (*NEON_CYAN, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     panel_rect.width + i,
                                     panel_rect.height + i),
                         width=2, border_radius=14)
    screen.blit(pglow, (panel_rect.x - 20, panel_rect.y - 20))

    pygame.draw.rect(screen, SURFACE, panel_rect, border_radius=14)
    for i in range(16):
        a = int(55 * (1 - i / 16))
        if a <= 0:
            continue
        pygame.draw.line(screen, (190, 230, 255, a),
                         (panel_rect.x + 2, panel_rect.y + 2 + i),
                         (panel_rect.right - 2, panel_rect.y + 2 + i))
    pygame.draw.rect(screen, NEON_CYAN, panel_rect,
                     width=2, border_radius=14)
    pygame.draw.rect(screen, (*NEON_MAGENTA, 220),
                     panel_rect.inflate(-10, -10),
                     width=1, border_radius=10)

    info_center_x = panel_rect.centerx
    label_x = panel_rect.x + 20
    value_x = panel_rect.x + 90

    draw_text_with_glow("关 卡 信 息", font_medium, TEXT_PRIMARY,
                        (info_center_x, 132),
                        glow_color=NEON_CYAN, glow_alpha=90)
    pygame.draw.line(screen, (*NEON_MAGENTA, 180),
                     (panel_rect.left + 18, 156),
                     (panel_rect.right - 18, 156), 1)

    draw_text_left("得分", font_tiny, TEXT_DIM, (label_x, 184))
    draw_text_left_with_glow(str(score), font_score, NEON_CYAN,
                             (value_x, 184),
                             glow_color=NEON_CYAN, glow_alpha=100)

    elapsed = get_current_elapsed_time()
    draw_text_left("时间", font_tiny, TEXT_DIM, (label_x, 222))
    draw_text_left(format_time(elapsed), font_score, TEXT_PRIMARY,
                   (value_x, 222))

    draw_text_left("飞镖", font_tiny, TEXT_DIM, (label_x, 260))
    draw_text_left(str(len(arrows)), font_score, TEXT_PRIMARY,
                   (value_x, 260))

    draw_text_left("失误", font_tiny, TEXT_DIM, (label_x, 298))
    draw_text_left_with_glow(str(mistakes), font_score, NEON_MAGENTA,
                             (value_x, 298),
                             glow_color=NEON_MAGENTA, glow_alpha=120)

    pygame.draw.line(screen, (*NEON_MAGENTA, 180),
                     (panel_rect.left + 18, 328),
                     (panel_rect.right - 18, 328), 2)

    draw_text_with_glow("操 作 说 明", font_medium, TEXT_PRIMARY,
                        (info_center_x, 364),
                        glow_color=NEON_CYAN, glow_alpha=90)
    draw_text_left("点击飞镖", font_small, TEXT_SECONDARY,
                   (label_x, 408))
    draw_text_left("让飞镖向前飞出", font_small, TEXT_SECONDARY,
                   (label_x, 444))

    draw_button(hint_button_rect, "提 示", font_small, NEON_YELLOW)

    if len(undo_history) > 0:
        draw_button(undo_button_rect, "撤销上一步", font_small, NEON_GREEN)
    else:
        draw_button(undo_button_rect, "暂无可撤销", font_small, LOCK_GRAY,
                    text_color=TEXT_DIM)

    draw_button(restart_game_button_rect, "重新开始",
                font_small, NEON_PURPLE)

    draw_board()
    draw_flying_arrows()

    if collision_effect is not None:
        tip_rect = pygame.Rect(WIDTH // 2 - 130, 626, 260, 42)
        tglow = pygame.Surface((tip_rect.width + 20, tip_rect.height + 20),
                               pygame.SRCALPHA)
        for i in range(14):
            a = int(80 * (1 - i / 14) ** 2)
            if a <= 0:
                continue
            pygame.draw.rect(tglow, (*NEON_MAGENTA, a),
                             pygame.Rect(10 - i // 2, 10 - i // 2,
                                         tip_rect.width + i,
                                         tip_rect.height + i),
                             width=2, border_radius=10)
        screen.blit(tglow, (tip_rect.x - 10, tip_rect.y - 10))
        pygame.draw.rect(screen, SURFACE_DARK, tip_rect, border_radius=10)
        pygame.draw.rect(screen, NEON_MAGENTA, tip_rect,
                         width=2, border_radius=10)
        draw_text_with_glow("前方有阻挡！", font_small, NEON_MAGENTA,
                            (WIDTH // 2, 647),
                            glow_color=NEON_MAGENTA, glow_alpha=150)

# ============================================================
# 三星
# ============================================================

def draw_stars(stars, center_x, center_y, frame=999):
    star_size = 44
    gap = 26
    total = 3 * star_size + 2 * gap
    start_x = center_x - total // 2 + star_size // 2
    for i in range(3):
        x = start_x + i * (star_size + gap)

        if i < stars:
            delay = i * 8
            if frame < delay:
                continue
            tt = min(1.0, (frame - delay) / 20.0)
            c1 = 1.70158
            c3 = c1 + 1
            scale = 1 + c3 * (tt - 1) ** 3 + c1 * (tt - 1) ** 2
            if scale < 0.05:
                continue
        else:
            scale = 1.0

        color = NEON_YELLOW if i < stars else (48, 65, 92)
        points = []
        for j in range(10):
            angle = -math.pi / 2 + j * math.pi / 5
            radius = star_size / 2 if j % 2 == 0 else star_size / 4
            points.append((x + math.cos(angle) * radius * scale,
                           center_y + math.sin(angle) * radius * scale))

        if i < stars and scale > 0.5:
            glow_surf = pygame.Surface(
                (star_size * 2 + 30, star_size * 2 + 30),
                pygame.SRCALPHA)
            gr = star_size + 15
            for rr in range(gr, 0, -2):
                a = int(85 * (1 - rr / gr) ** 2)
                if a <= 0:
                    continue
                pygame.draw.circle(glow_surf, (*NEON_YELLOW, a),
                                   (gr, gr), rr, 2)
            screen.blit(glow_surf, glow_surf.get_rect(
                center=(x, center_y)))

        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (12, 28, 50), points, 1)

        if i < stars and scale > 0.5:
            inner_pts = [(x + (px - x) * 0.55,
                          center_y + (py - center_y) * 0.55)
                         for px, py in points]
            pygame.draw.polygon(screen, (240, 255, 250), inner_pts)

# ============================================================
# 通关界面
# ============================================================

_star_sound_frames = {0: False, 1: False, 2: False}

def draw_level_finished_screen():
    global _star_sound_frames
    screen.blit(background, (0, 0))
    draw_top_vapor_bar()

    for i in range(current_stars):
        delay = i * 8
        if level_finished_frame >= delay and not _star_sound_frames.get(i, False):
            play_sound(snd_star)
            _star_sound_frames[i] = True

    draw_text_centered_with_glow("恭喜通关！", font_title, NEON_CYAN, 75,
                                  glow_color=NEON_CYAN, glow_alpha=160,
                                  offset=3)
    draw_text(f"第 {current_level} 关完成",
              font_medium, TEXT_PRIMARY, (WIDTH // 2, 135))
    draw_stars(current_stars, WIDTH // 2, 200, level_finished_frame)
    draw_text_with_glow(f"{current_stars} 星评价",
                        font_normal, NEON_YELLOW, (WIDTH // 2, 250),
                        glow_color=NEON_YELLOW, glow_alpha=120)

    result_rect = pygame.Rect(320, 280, 360, 110)
    rglow = pygame.Surface((result_rect.width + 40, result_rect.height + 40),
                           pygame.SRCALPHA)
    for i in range(16):
        a = int(60 * (1 - i / 16) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(rglow, (*NEON_CYAN, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     result_rect.width + i,
                                     result_rect.height + i),
                         width=2, border_radius=12)
    screen.blit(rglow, (result_rect.x - 20, result_rect.y - 20))

    pygame.draw.rect(screen, SURFACE, result_rect, border_radius=12)
    for i in range(16):
        a = int(50 * (1 - i / 16))
        if a <= 0:
            continue
        pygame.draw.line(screen, (190, 230, 255, a),
                         (result_rect.x + 2, result_rect.y + 2 + i),
                         (result_rect.right - 2, result_rect.y + 2 + i))
    pygame.draw.rect(screen, NEON_CYAN, result_rect,
                     width=2, border_radius=12)
    pygame.draw.rect(screen, (*NEON_MAGENTA, 220),
                     result_rect.inflate(-8, -8), width=1, border_radius=9)

    draw_text_with_glow(f"最终得分：{score}", font_normal, NEON_CYAN,
                        (WIDTH // 2, 315),
                        glow_color=NEON_CYAN, glow_alpha=100)
    draw_text(f"完成时间：{format_time(final_time)}",
              font_small, TEXT_SECONDARY, (WIDTH // 2, 360))

    if current_level < MAX_LEVEL:
        draw_button(next_level_button_rect,
                    f"进入第 {current_level + 1} 关",
                    font_medium, NEON_GREEN)
    else:
        draw_button(next_level_button_rect, "完成全部关卡",
                    font_medium, NEON_GREEN)

    draw_button(back_select_button_rect, "返回关卡选择",
                font_normal, NEON_CYAN)

# ============================================================
# 失败界面
# ============================================================

def draw_failed_screen():
    screen.blit(background, (0, 0))
    red = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    red.fill((*NEON_MAGENTA, 18))
    screen.blit(red, (0, 0))
    draw_top_vapor_bar()

    draw_text_centered_with_glow("挑战失败", font_title, NEON_MAGENTA, 115,
                                  glow_color=NEON_MAGENTA, glow_alpha=160,
                                  offset=3)
    draw_text("失误次数已经用完", font_medium, TEXT_PRIMARY,
              (WIDTH // 2, 190))

    fail_rect = pygame.Rect(320, 235, 360, 105)
    fglow = pygame.Surface((fail_rect.width + 40, fail_rect.height + 40),
                           pygame.SRCALPHA)
    for i in range(16):
        a = int(65 * (1 - i / 16) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(fglow, (*NEON_MAGENTA, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     fail_rect.width + i,
                                     fail_rect.height + i),
                         width=2, border_radius=12)
    screen.blit(fglow, (fail_rect.x - 20, fail_rect.y - 20))

    pygame.draw.rect(screen, SURFACE, fail_rect, border_radius=12)
    for i in range(16):
        a = int(50 * (1 - i / 16))
        if a <= 0:
            continue
        pygame.draw.line(screen, (190, 240, 255, a),
                         (fail_rect.x + 2, fail_rect.y + 2 + i),
                         (fail_rect.right - 2, fail_rect.y + 2 + i))
    pygame.draw.rect(screen, NEON_MAGENTA, fail_rect,
                     width=2, border_radius=12)
    pygame.draw.rect(screen, (*NEON_MAGENTA, 255),
                     fail_rect.inflate(-8, -8), width=1, border_radius=9)

    draw_text(f"当前为第 {current_level} 关",
              font_normal, TEXT_PRIMARY, (WIDTH // 2, 270))
    draw_text(f"当前得分：{score}",
              font_small, NEON_CYAN, (WIDTH // 2, 315))

    draw_button(restart_button_rect, "重新挑战", font_medium, NEON_MAGENTA)
    draw_button(back_select_button_rect, "返回关卡选择",
                font_normal, NEON_CYAN)

# ============================================================
# 全部通关
# ============================================================

def draw_all_finished_screen():
    screen.blit(background, (0, 0))
    draw_top_vapor_bar()

    draw_text_centered_with_glow("全部通关！", font_title, NEON_CYAN, 125,
                                  glow_color=NEON_CYAN, glow_alpha=160,
                                  offset=3)
    draw_text(f"恭喜你完成了全部 {MAX_LEVEL} 个关卡",
              font_medium, TEXT_PRIMARY, (WIDTH // 2, 215))
    draw_text("你可以返回关卡选择重新挑战",
              font_normal, TEXT_SECONDARY, (WIDTH // 2, 275))

    cx, cy = WIDTH // 2, 370
    size = 96
    glow_surf = pygame.Surface((size * 2 + 40, size * 2 + 40),
                               pygame.SRCALPHA)
    for i in range(20):
        a = int(90 * (1 - i / 20) ** 2)
        if a <= 0:
            continue
        pygame.draw.rect(glow_surf, (*NEON_YELLOW, a),
                         pygame.Rect(20 - i // 2, 20 - i // 2,
                                     size * 2 + i, size * 2 + i),
                         width=2, border_radius=20)
    screen.blit(glow_surf, glow_surf.get_rect(center=(cx, cy)))

    pygame.draw.rect(screen, SURFACE,
                     (cx - size // 2, cy - size // 2, size, size),
                     border_radius=14)
    pygame.draw.rect(screen, NEON_YELLOW,
                     (cx - size // 2, cy - size // 2, size, size),
                     width=3, border_radius=14)
    pygame.draw.rect(screen, (*NEON_MAGENTA, 220),
                     (cx - size // 2 + 6, cy - size // 2 + 6,
                      size - 12, size - 12),
                     width=1, border_radius=10)
    draw_text_with_glow("成", font_title, NEON_YELLOW, (cx, cy),
                        glow_color=NEON_YELLOW, glow_alpha=180)

    draw_button(back_select_button_rect, "返回关卡选择",
                font_medium, NEON_CYAN)

# ============================================================
# 主循环
# ============================================================

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if not game_started and not level_selecting:
                if start_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    game_started = True
                    level_selecting = True
            elif game_started and level_selecting:
                for i, rect in enumerate(level_button_rects):
                    level_number = i + 1
                    if (level_number <= unlocked_level
                            and rect.collidepoint(mouse_pos)):
                        play_sound(snd_click)
                        load_level(level_number)
                        level_selecting = False
                        game_started = True
                        break
            elif game_failed:
                if restart_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    load_level(current_level)
                elif back_select_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    game_failed = False
                    level_selecting = True
            elif all_levels_finished:
                if back_select_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    all_levels_finished = False
                    level_selecting = True
            elif level_finished:
                if next_level_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    if current_level < MAX_LEVEL:
                        next_level = current_level + 1
                        unlocked_level = max(unlocked_level, next_level)
                        load_level(next_level)
                    else:
                        level_finished = False
                        all_levels_finished = True
                elif back_select_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    level_finished = False
                    level_selecting = True
            elif game_started:
                if restart_game_button_rect.collidepoint(mouse_pos):
                    play_sound(snd_click)
                    load_level(current_level)
                elif hint_button_rect.collidepoint(mouse_pos):
                    show_hint()
                elif undo_button_rect.collidepoint(mouse_pos):
                    undo_last_move()
                else:
                    handle_arrow_click(mouse_pos)
                    if mistakes <= 0:
                        final_time = time.time() - level_start_time
                        game_failed = True
                        collision_effect = None
                        play_sound(snd_fail)

    if (game_started and not level_selecting
            and not game_failed and not all_levels_finished):
        update_flying_arrows()
        update_hint()
        update_score_popups()
        update_ripples()
        if not level_finished:
            update_collision_effect()

    if level_finished:
        level_finished_frame += 1

    if not game_started and not level_selecting:
        draw_start_screen()
    elif game_started and level_selecting:
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

pygame.quit()
sys.exit()