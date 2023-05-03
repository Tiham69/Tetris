import pygame as pg
from copy import deepcopy
from random import choice, randrange
import os
import sys

W, H = 10, 20
TILE = 35
GAME_RES = W * TILE, H * TILE
FPS = 60
RES = 750, 750 # width = 750, height = 940
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pg.display.set_caption('TITris')
icon = pg.image.load(resource_path('tetris_assets\\tetris.ico'))
pg.display.set_icon(icon)

pg.init()
sc = pg.display.set_mode(RES)
game_sc = pg.Surface(GAME_RES) # display.set_mode(GAME_RES)
clock = pg.time.Clock()
yellow = pg.Color('yellow')

grid = [pg.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, -1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)],
               ]
figures = [[pg.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pg.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

ani_count, ani_speed, ani_limit = 0, 60, 2000 # falling speed and time difference
# BJ area
bg = pg.image.load(resource_path('tetris_assets/Teters_bg_2.jpg')).convert() # background
game_bg = pg.image.load(resource_path('tetris_assets/Teters_bg.jpg')).convert() # foreground
# font area
main_font = pg.font.Font('tetris_assets/rainbow_season.otf', 100)
font = pg.font.Font('tetris_assets/rainbow_season.otf', 50)
text = pg.font.Font('tetris_assets/rainbow_season.otf', 20)
# screen text
title_tetris = main_font.render('TITris', True, 'skyblue') # if used built in font = pg.color('blue')
title_score = font.render('SCORE: ', True, pg.Color('green'))
title_record = font.render('RECORD:', True, pg.Color('gold'))
txt = text.render('WASD or ARROW KEY TO MOVE AND ROTATE', True, yellow)
txt2 = text.render('PRESS SPACE TO FREE FALL', True, yellow)
txt3 = text.render('YOU ARE A GOOD TRASH WASTING TIME', True, yellow)



get_color = lambda: (randrange(80, 255), randrange(80, 255), randrange(80, 255))

figure, next_fig = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 10: 1, 2: 30, 3: 70, 4: 150}

def check_border():
    if figure[i].x < 0 or  figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w')as f:
            f.write('0')

def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))
        f.close()

while True:
    record = get_record()
    dx, rotate = 0, False
    # game_sc.fill(pg.Color('black'))
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (10, 10))
    game_sc.blit(game_bg, (0, 0))
    # delay for full line
    for i in range(lines):
        pg.time.wait(200)

    for event in pg.event.get():
        # quit
        if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
            exit()
        # control
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT or event.key == pg.K_a: # add a and d key
                dx = -1
            elif event.key == pg.K_RIGHT or event.key == pg.K_d:
                dx = 1
            elif event.key == pg.K_SPACE:
                ani_limit = 100
            elif event.key == pg.K_UP:
                rotate = True
    # x direction control
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_border():
            figure = deepcopy(figure_old)
            break
    # y direction movement
    ani_count += ani_speed
    if ani_count > ani_limit:
        ani_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_border():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color # pg.Color('white')
                figure, color = next_fig, next_color
                next_fig, next_color = deepcopy(choice(figures)), get_color()
                ani_limit = 2000
                break
    # rotation
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_border():
                figure = deepcopy(figure_old)
                break
    # line check
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            ani_speed += 3
            lines += 1
    # score count
    score += scores[lines]
    # grid draw
    [pg.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # figure draw
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pg.draw.rect(game_sc, color, figure_rect) # pg.Color('yellow')
    # field draw
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pg.draw.rect(game_sc, col, figure_rect)
    # next fig draw
    for i in range(4):
        figure_rect.x = next_fig[i].x * TILE + 380
        figure_rect.y = next_fig[i].y * TILE + 160
        pg.draw.rect(sc, next_color, figure_rect)
    # TEXT draw
    sc.blit(title_tetris, (445, 25))    # TITres
    sc.blit(title_score, (380, 420))    # x , y cords
    sc.blit(font.render(str(score), True, pg.Color('green')), (385, 470))
    sc.blit(title_record, (380, 300))
    sc.blit(font.render(record, True, pg.Color('gold')), (385, 360))
    sc.blit(txt, (380, 550))
    sc.blit(txt2, (450, 590))
    if score == 250:
        sc.blit(txt3, (400, 650))
    if score == 69 or score == 420:
        sc.blit(text.render('NOICE', True, yellow), (150, 300))


    # game over
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0  for i in range(W)] for i in range(H)]
            ani_count, ani_speed, ani_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pg.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (10, 10))
                pg.display.flip()
                clock.tick(170)

    pg.display.flip()
    clock.tick(FPS)