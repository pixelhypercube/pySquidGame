import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from components.Helper import Helper
from components.Color import Color
from Settings import WIDTH, HEIGHT
helper = Helper()

class GameHandler:
    def __init__(self,time,preparation_time,bg_color):
        self.time = time
        self.preparation_time = preparation_time
        self.bg_color = bg_color
        self.in_game_frame_count = 0
        self.buttons = []
        self.paused = True
    def render_prep_screen(self,frame,time_left):
        pg.draw.rect(frame,Color.SQUID_GREY,(WIDTH/2-80,HEIGHT/4-30,160,80))
        helper.render_text(frame,"Get ready in",WIDTH/2,HEIGHT/4-10,font_size=20)
        helper.render_text(frame,str(time_left),WIDTH/2,HEIGHT/4+20,font_size=30)
    def handle_buttons(self,event,mouse_x,mouse_y,current_screen):
        next_screen = current_screen
        for btn in self.buttons:
            if btn.visible:
                next_screen = btn.click_listener(event, mouse_x, mouse_y, next_screen)
        return next_screen