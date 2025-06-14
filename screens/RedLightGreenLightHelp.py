from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from screens.GameHandler import GameHandler
from screens.RedLightGreenLight import RedLightGreenLight
from components.Button import Button
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
helper = Helper()

class RedLightGreenLightHelp(RedLightGreenLight):
    def __init__(self):
        super().__init__()
        self.back_btn = Button(80,HEIGHT/5,50,25,content="Back",next_screen="home")
        self.start_btn = Button(WIDTH/2,HEIGHT/1.35,60,20,content="Start",next_screen="red_light_green_light")
        self.buttons = [
            self.back_btn,self.start_btn
        ]
    
    def render(self,frame,mouse_x,mouse_y):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"How to play:",WIDTH/2,HEIGHT/12,font_size=40)
        helper.render_text(frame,"Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,font_size=20)
        helper.render_image(frame,"./assets/img/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
        helper.render_text(frame,"When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,font_size=20)
        helper.render_text(frame,"Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,font_size=20)
        helper.render_text(frame,"Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,font_size=20)
        helper.render_text(frame,"Repeatedly press W if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,font_size=20)
        for btn in self.buttons:
            btn.render(frame)