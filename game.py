import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from screens.Home import Home
from screens.Levels import Levels
from screens.RedLightGreenLight import RedLightGreenLight
from screens.RedLightGreenLightHelp import RedLightGreenLightHelp

current_screen = "home"
screens = {
    "home":Home(),
    "levels":Levels(),
    "red_light_green_light_help": RedLightGreenLightHelp(),
    "red_light_green_light": RedLightGreenLight(),
}

# The game
pg.init()
pg.font.init()
frame = pg.display.set_mode([WIDTH,HEIGHT])
running = True

clock = pg.time.Clock()

screen = screens[current_screen]

frame_count = 0
while running:
    clock.tick(60)
    mouse_x = pg.mouse.get_pos()[0]
    mouse_y = pg.mouse.get_pos()[1]
    mouse_is_down = pg.mouse.get_pressed()[0] == 1

    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("Quitting the game...")
            running = False
    current_screen = screen.handle_buttons(event, mouse_x, mouse_y, current_screen)

    screen = screens[current_screen]
    screen.render(frame, mouse_x, mouse_y)

    pg.display.update()
    frame_count += 1