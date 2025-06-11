import pygame as pg
import math
import random
import webbrowser
from threading import Timer

WIDTH = 800
HEIGHT = 600
running = True

clock = pg.time.Clock()



while running:

    

    clock.tick(60)
    mouse_x = pg.mouse.get_pos()[0]
    mouse_x = pg.mouse.get_pos()[1]
    mouse_is_down = pg.mouse.get_pressed()[0] == 1
    pg.display.update()
    frame_count += 1