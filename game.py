import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from screens.Home import Home
from screens.Levels import Levels
from screens.RedLightGreenLight import RedLightGreenLight
from screens.HoneyComb import HoneyComb
from screens.TugOfWar import TugOfWar
from screens.Marbles import Marbles
from screens.GlassSteppingStones import GlassSteppingStones
from screens.SquidGame import SquidGame
from screens.Credits import Credits
import os
import sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def clean_path(path: str) -> str:
    return path.lstrip("./\\")

current_screen = "home"
screens = {
    "home":Home(),
    "levels":Levels(),
    "credits":Credits(),
    "red_light_green_light": RedLightGreenLight(),
    "honey_comb": HoneyComb(),
    "tug_of_war": TugOfWar(),
    "marbles": Marbles(),
    "glass_stepping_stones": GlassSteppingStones(),
    "squid_game": SquidGame()  
}

# The game
pg.init()
pg.font.init()

pg.display.set_caption("pySquidGame")
icon = pg.image.load(resource_path(clean_path('./assets/img/favicon.ico')))
pg.display.set_icon(icon)

frame = pg.display.set_mode([WIDTH,HEIGHT])
running = True

clock = pg.time.Clock()

screen = screens[current_screen]

frame_count = 0

button_cooldown = frame_count + 30

while running:
    clock.tick(60)
    mouse_x = pg.mouse.get_pos()[0]
    mouse_y = pg.mouse.get_pos()[1]
    mouse_is_down = pg.mouse.get_pressed()[0] == 1

    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("Quitting the game...")
            running = False
        if event.type == pg.KEYDOWN:
            screen.keydown_listener(event.key)
        if event.type == pg.KEYUP:
            screen.keyup_listener(event.key)
        
        if hasattr(screen,"mousedown_listener"):
            screen.mousedown_listener(event,mouse_x,mouse_y)
    
    next_screen = screen.handle_buttons(event, mouse_x, mouse_y, current_screen) if button_cooldown<=frame_count else current_screen
    if (next_screen != current_screen) and (next_screen in screens):
        button_cooldown = frame_count + 30
        current_screen = next_screen
        screen = screens[current_screen]
        if hasattr(screen, 'restart_game'):
            screen.restart_game()

    screen = screens[current_screen]
    screen.render(frame, mouse_x, mouse_y)

    pg.display.update()
    frame_count += 1