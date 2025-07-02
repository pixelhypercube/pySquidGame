import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from components.Helper import Helper
from components.Color import Color
from Settings import WIDTH, HEIGHT
from screens.GameHandler import GameHandler
from objects.Ddakji import Ddakji

helper = Helper()

class DdakjiGame(GameHandler):
    def __init__(self, time=6000000, preparation_time=5, bg_color=Color.SQUID_GREY):
        super().__init__(time, preparation_time, bg_color)
        self.player_1 = Ddakji(WIDTH//2-30,HEIGHT//2,50,50,Color.RED,stroke_thickness=2)
        self.player_2 = Ddakji(WIDTH//2+30,HEIGHT//2,50,50,Color.LIGHT_BLUE,stroke_thickness=2)
    def render(self,frame,mouse_x,mouse_y):
        frame.fill(Color.GREY)
        
        self.player_2.render(frame)
        self.player_1.render(frame)
    
    def mousedown_listener(self,event,mouse_x,mouse_y):
        if event.type==pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0]:
                self.player_1.grab(mouse_x,mouse_y)
        elif event.type==pg.MOUSEBUTTONUP:
            self.player_1.is_grabbing = False
            # if self.player_1.is_grabbing:
            #     self.player_1.smash(self.player_2)
            
    def render_fail(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Eliminated :(",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,font_size=20)
        helper.render_text(frame," by clicking the 'Back to Levels' button! :)",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_success(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Success!",WIDTH/2,HEIGHT/3,font_size=40)
        self.return_lvls_btn.render(frame)
    def render_help(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame, "How to play: Ddakji", WIDTH // 2, 50, color=Color.WHITE, font_size=40,underline=True)
        helper.render_text(
            frame, "Objective: Smash your opponent's Ddakji by flipping it over!",
            WIDTH // 2, HEIGHT // 6, font_size=22, color=Color.WHITE
        )
        helper.render_image(
            frame, "./assets/img/honeycomb/demo.png",
            WIDTH // 2, HEIGHT // 2.1, [int(500 / 2.25), int(375 / 2.25)]
        )
        helper.render_text(
            frame, "Click and drag to aim at your opponent!",
            WIDTH // 2, HEIGHT // 1.29, font_size=20, color=Color.WHITE
        )
        helper.render_text(
            frame, "Ensure that the right angle has been put in place!",
            WIDTH // 2, HEIGHT // 1.22, font_size=20, color=Color.WHITE
        )

        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(0) 