from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from objects.Block import Block
from screens.GameHandler import GameHandler
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from components.Button import Button
from objects.RadialForceArea import RadialForceArea
from objects.LinearForceArea import LinearForceArea
from objects.Marble import Marble

helper = Helper()

class Marbles(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.33,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")

        # fail/success screen
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        # objects

        self.marbles = [
            Marble(WIDTH//2,HEIGHT//1.3,5,Color.SQUID_TEAL,max_speed=1)
        ]

        self.force_areas = [
            RadialForceArea(WIDTH//2-50,HEIGHT//2-50,100,100,Color.SQUID_LIGHT_TEAL,stroke_thickness=0,stroke_color=Color.BLACK,force_strength=1)
        ]
    

    def render(self,frame,mouse_x,mouse_y):
        frame.fill(self.bg_color)
        for force_area in self.force_areas:
            force_area.render(frame)
        for marble in self.marbles:
            marble.render(frame)

    def render_fail(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Eliminated :(",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,font_size=20)
        helper.render_text(frame," by clicking the 'Go back' button! :)",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_success(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Success!",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Thanks a lot for playing! Since this program is in beta,",WIDTH/2,HEIGHT/2.4,font_size=20)
        helper.render_text(frame,"there are 4 games are currently in progress!",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_help(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame, "HoneyComb", WIDTH//2, 50, color=Color.WHITE, font_size=30)
        helper.render_text(frame, "Instructions:", WIDTH//2, 100, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "1. Choose a shape to cut out.", WIDTH//2, 150, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "2. Use the mouse to cut along the lines.", WIDTH//2, 200, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "3. Avoid breaking the shape.", WIDTH//2, 250, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "4. Complete the shape within the time limit.", WIDTH//2, 300, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "5. If you break the shape, you lose.", WIDTH//2, 350, color=Color.WHITE, font_size=20)
        helper.render_text(frame, "6. Good luck!", WIDTH//2, 400, color=Color.WHITE, font_size=20)

        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(frame,0) 