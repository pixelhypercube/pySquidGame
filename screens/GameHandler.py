import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from components.Helper import Helper
import components.Color as Color
from Settings import WIDTH, HEIGHT
helper = Helper()

class GameHandler:
    def __init__(self,time,preparation_time,bg_color):
        self.time = time
        self.preparation_time = preparation_time
        self.bg_color = bg_color
        self.inGameFrameCount = 0
        self.buttons = []
    def render_prep_screen(self,frame,time_left):
        pg.draw.rect(frame,Color.squid_grey,(WIDTH/2-80,HEIGHT/4-30,160,80))
        helper.renderText("Get ready in",WIDTH/2,HEIGHT/4-10,font_size=20)
        helper.renderText(str(time_left),WIDTH/2,HEIGHT/4+20,font_size=30)
    def handle_buttons(self,event,mouse_x,mouse_y,current_screen):
        next_screen = current_screen
        for btn in self.buttons:
            next_screen = btn.click_listener(event, mouse_x, mouse_y, next_screen)
        return next_screen