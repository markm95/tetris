"""
俄罗斯方块游戏
作者：Mark
最后更新：2023-12-08
版本：1.0

游戏说明：
- 方向键控制方块移动
- 空格键快速下落
- P键暂停游戏
- ESC退出游戏
- Ctrl+S 保存游戏
- Ctrl+L 加载游戏
"""

import pygame
import random
import sys
import json
import pickle

# 初始化 Pygame
pygame.init()

# 设置游戏窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 计算游戏区域的位置
GAME_AREA_X = (WINDOW_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GAME_AREA_Y = (WINDOW_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('俄罗斯方块')

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),      # 红色
    (0, 255, 0),      # 绿色
    (0, 0, 255),      # 蓝色
    (255, 255, 0),    # 黄色
    (255, 165, 0),    # 橙色
    (0, 255, 255),    # 青色
    (255, 0, 255)     # 紫色
]

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],                       # I
    [[1, 1], [1, 1]],                     # O
    [[1, 1, 1], [0, 1, 0]],              # T
    [[1, 1, 1], [1, 0, 0]],              # L
    [[1, 1, 1], [0, 0, 1]],              # J
    [[1, 1, 0], [0, 1, 1]],              # S
    [[0, 1, 1], [1, 1, 0]]               # Z
]

# 创建游戏网格
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# 分数系统
score = 0
level = 1
LEVEL_UP_SCORE = 500  # 每500分升级一次
INITIAL_FALL_SPEED = 0.5  # 初始下落速度（秒）
SPEED_INCREASE_RATE = 0.05  # 每升一级减少的秒数
MIN_FALL_SPEED = 0.1  # 最小下落速度（最快速度）
font = pygame.font.SysFont('Arial', 24)
SINGLE_LINE_SCORE = 100
SCORE_MULTIPLIER = {
    1: 1,    # 1行 = 100分
    2: 3,    # 2行 = 300分
    3: 6,    # 3行 = 600分
    4: 10    # 4行 = 1000分
}

# 添加保存/加载相关的常量
SAVE_FILE = "tetris_save.dat"

# 添加保存游戏函数
def save_game():
    game_state = {
        'score': score,
        'grid': grid,
        'grid_colors': grid_colors,
        'current_piece': {
            'shape': current_piece.shape,
            'color': current_piece.color,
            'x': current_piece.x,
            'y': current_piece.y
        },
        'fall_speed': fall_speed
    }
    try:
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(game_state, f)
        return True
    except:
        return False

# 添加加载游戏函数
def load_game():
    global score, grid, grid_colors, current_piece, fall_speed
    try:
        with open(SAVE_FILE, 'rb') as f:
            game_state = pickle.load(f)
            
        score = game_state['score']
        grid = game_state['grid']
        grid_colors = game_state['grid_colors']
        
        # 重新创建当前方块
        current_piece = Tetromino()
        current_piece.shape = game_state['current_piece']['shape']
        current_piece.color = game_state['current_piece']['color']
        current_piece.x = game_state['current_piece']['x']
        current_piece.y = game_state['current_piece']['y']
        
        fall_speed = game_state['fall_speed']
        return True
    except:
        return False

def check_lines():
    global score, level, fall_speed
    lines_to_clear = []
    for i in range(GRID_HEIGHT):
        if all(grid[i]):
            lines_to_clear.append(i)
    
    num_lines = len(lines_to_clear)
    if num_lines > 0:
        score += SINGLE_LINE_SCORE * SCORE_MULTIPLIER[num_lines]
        old_level = level
        level = score // LEVEL_UP_SCORE + 1
        
        # 如果等级提升，更新速度
        if level > old_level:
            fall_speed = max(
                MIN_FALL_SPEED,
                INITIAL_FALL_SPEED - (level - 1) * SPEED_INCREASE_RATE
            )
        
        for line in lines_to_clear:
            del grid[line]
            del grid_colors[line]
            grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            grid_colors.insert(0, [BLACK for _ in range(GRID_WIDTH)])

class Tetromino:
    def __init__(self, shape=None):
        self.shape = shape if shape else random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def draw(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, self.color,
                                   (GAME_AREA_X + (self.x + j) * BLOCK_SIZE,
                                    GAME_AREA_Y + (self.y + i) * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    def check_collision(self, x, y):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or 
                        (new_y >= 0 and grid[new_y][new_x])):
                        return True
        return False

    def move_left(self):
        if not self.check_collision(self.x - 1, self.y):
            self.x -= 1

    def move_right(self):
        if not self.check_collision(self.x + 1, self.y):
            self.x += 1

    def move_down(self):
        if not self.check_collision(self.x, self.y + 1):
            self.y += 1
            return False
        return True

    def rotate(self):
        rotated_shape = [[self.shape[j][i] for j in range(len(self.shape)-1, -1, -1)]
                       for i in range(len(self.shape[0]))]
        original_shape = self.shape
        self.shape = rotated_shape
        if self.check_collision(self.x, self.y):
            self.shape = original_shape

    def lock_piece(self):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell and self.y + i >= 0:
                    grid[self.y + i][self.x + j] = 1
                    grid_colors[self.y + i][self.x + j] = self.color
        check_lines()

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                pygame.draw.rect(screen, grid_colors[y][x],
                               (GAME_AREA_X + x * BLOCK_SIZE,
                                GAME_AREA_Y + y * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, (50, 50, 50),
                        (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y),
                        (GAME_AREA_X + x * BLOCK_SIZE, GAME_AREA_Y + GRID_HEIGHT * BLOCK_SIZE))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, (50, 50, 50),
                        (GAME_AREA_X, GAME_AREA_Y + y * BLOCK_SIZE),
                        (GAME_AREA_X + GRID_WIDTH * BLOCK_SIZE, GAME_AREA_Y + y * BLOCK_SIZE))

    pygame.draw.rect(screen, WHITE, 
                    (GAME_AREA_X - 2, GAME_AREA_Y - 2, 
                     GRID_WIDTH * BLOCK_SIZE + 4, 
                     GRID_HEIGHT * BLOCK_SIZE + 4), 2)

def draw_next_piece(piece):
    next_text = font.render('Next:', True, WHITE)
    screen.blit(next_text, (WINDOW_WIDTH - 150, 10))
    
    preview_x = WINDOW_WIDTH - 150
    preview_y = 50
    
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color,
                               (preview_x + j * BLOCK_SIZE,
                                preview_y + i * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))

def reset_game():
    global grid, grid_colors, score, level, fall_time, fall_speed
    global current_piece, next_piece, game_over, paused
    
    # 重置网格
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    grid_colors = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # 重置游戏状态
    score = 0
    level = 1
    fall_speed = INITIAL_FALL_SPEED
    fall_time = 0
    paused = False
    game_over = False
    
    # 重置方块
    current_piece = Tetromino()
    next_piece = Tetromino()

# 创建当前方块和下一个方块
current_piece = Tetromino()
next_piece = Tetromino()

# 游戏主循环
running = True
clock = pygame.time.Clock()
fall_time = 0
fall_speed = INITIAL_FALL_SPEED
paused = False
game_over = False

# 添加按键延迟和重复速度的常量
MOVE_DELAY = 100  # 每次移动的延迟（毫秒）
last_move_time = {
    pygame.K_LEFT: 0,
    pygame.K_RIGHT: 0
}

# 添加消息显示相关变量
show_message = False
message_time = 0
save_message = ""
MESSAGE_DURATION = 2000  # 消息显示持续时间（毫秒）

# 在常量定义部分添加
SOFT_DROP_SPEED = 0.1  # 软下落速度倍数
DROP_DELAY = 50        # 下落延迟（毫秒）

while running:
    fall_time += clock.get_rawtime()
    current_time = pygame.time.get_ticks()
    clock.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and not game_over:
                paused = not paused
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and game_over:
                reset_game()
            elif not paused and not game_over:
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    while not current_piece.move_down():
                        pass
                    current_piece.lock_piece()
                    current_piece = next_piece
                    next_piece = Tetromino()
                    if current_piece.check_collision(current_piece.x, current_piece.y):
                        game_over = True
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+S 保存
                if save_game():
                    # 显示保存成功消息
                    save_message = "Game Saved"
                    show_message = True
                    message_time = pygame.time.get_ticks()
            elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+L 加载
                if load_game():
                    # 显示加载成功消息
                    save_message = "Game Loaded"
                    show_message = True
                    message_time = pygame.time.get_ticks()

    if not paused and not game_over:
        keys = pygame.key.get_pressed()

        # 处理左右移动
        for key in [pygame.K_LEFT, pygame.K_RIGHT]:
            if keys[key]:
                if current_time - last_move_time[key] > MOVE_DELAY:
                    if key == pygame.K_LEFT:
                        current_piece.move_left()
                    elif key == pygame.K_RIGHT:
                        current_piece.move_right()
                    last_move_time[key] = current_time

        # 处理下落
        if keys[pygame.K_DOWN]:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time.get(pygame.K_DOWN, 0) > DROP_DELAY:
                if current_piece.move_down():
                    current_piece.lock_piece()
                    current_piece = next_piece
                    next_piece = Tetromino()
                    if current_piece.check_collision(current_piece.x, current_piece.y):
                        game_over = True
                last_move_time[pygame.K_DOWN] = current_time

        # 自然下落
        if fall_time / 1000 > fall_speed:
            if current_piece.move_down():
                current_piece.lock_piece()
                current_piece = next_piece
                next_piece = Tetromino()
                if current_piece.check_collision(current_piece.x, current_piece.y):
                    game_over = True
            fall_time = 0

    screen.fill(BLACK)
    draw_grid()
    current_piece.draw()
    draw_next_piece(next_piece)

    # 显示分数和等级
    score_text = font.render(f'Score: {score}', True, WHITE)
    level_text = font.render(f'Level: {level}', True, WHITE)
    speed_text = font.render(f'Speed: {1/fall_speed:.1f}', True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    screen.blit(speed_text, (10, 70))

    if paused:
        pause_font = pygame.font.SysFont('Arial', 48)
        pause_text = pause_font.render('PAUSED', True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)

    if game_over:
        game_over_font = pygame.font.SysFont('Arial', 48)
        game_over_text = game_over_font.render('GAME OVER', True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)
        
        final_score_text = font.render(f'Final Score: {score}', True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(final_score_text, final_score_rect)
        
        restart_text = font.render('Press R to restart', True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
        screen.blit(restart_text, restart_rect)
        
        exit_text = font.render('Press ESC to exit', True, WHITE)
        exit_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150))
        screen.blit(exit_text, exit_rect)

    # 显示保存/加载消息
    if show_message:
        if current_time - message_time < MESSAGE_DURATION:
            message_font = pygame.font.SysFont(None, 36)
            message_text = message_font.render(save_message, True, WHITE)
            message_rect = message_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            screen.blit(message_text, message_rect)
        else:
            show_message = False

    pygame.display.flip()

pygame.quit()
sys.exit()