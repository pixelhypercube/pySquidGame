import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from screens.GameHandler import GameHandler
import components.Helper as Helper
from components.Color import Color
from Settings import WIDTH, HEIGHT
from components.Helper import Helper
from components.Button import Button

helper = Helper()

class Home(GameHandler):
    def __init__(self):
        super().__init__(0, 0, Color.SQUID_GREY)
        self.play_btn = Button(WIDTH/2,HEIGHT/1.5,90,50,content="",next_screen="levels",visible=True)
        self.credits_btn = Button(WIDTH/8,HEIGHT/1.15,50,20,content="Credits",next_screen="credits",visible=True)
        self.buttons = [self.play_btn,self.credits_btn]

    def keydown_listener(self, event):
        pass

    def keyup_listener(self, event):
        pass

    def render(self, frame, mouse_x, mouse_y):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_image(frame,"./assets/img/titleLogo.png",WIDTH/2,HEIGHT/3)
        # helper.render_text(frame,"By PixelHyperCube!",WIDTH/2,HEIGHT/1.9,font_size=24)
        # helper.render_text(frame,"Made using pygame!",WIDTH/2,HEIGHT/1.7,font_size=15)
        self.credits_btn.render(frame)
        if mouse_x>=WIDTH/2-90 and mouse_x<=WIDTH/2+90 and mouse_y>=HEIGHT/1.35-50 and mouse_y<=HEIGHT/1.35+50:
            helper.render_image(frame,"./assets/img/invitationBack.png",WIDTH/2,HEIGHT/1.5)
        else:
            helper.render_image(frame,"./assets/img/invitationFront.png",WIDTH/2,HEIGHT/1.5)