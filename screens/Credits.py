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

class Credits(GameHandler):
    def __init__(self):
        super().__init__(0, 0, Color.SQUID_GREY)
        self.back_btn = Button(WIDTH//2,HEIGHT*0.8,50,20,"Back",next_screen="home")
        self.github_btn = Button(WIDTH//2,HEIGHT*0.625,90,50,"Github Link",image_path="./assets/img/github.png",image_mode="squeeze",function=lambda: (print("Opening GitHub..."), webbrowser.open("https://github.com/pixelhypercube/pySquidGame"))[1])
        self.buttons = [self.back_btn,self.github_btn]

    def render(self,frame,mouse_x,mouse_y):
        pg.draw.rect(frame, Color.SQUID_GREY, (0, 0, WIDTH, HEIGHT))
    
        # Title
        helper.render_text(frame, "Credits & Acknowledgements", WIDTH // 2, HEIGHT // 6, font_size=36,underline=True)
        
        # Body Text
        credit_lines = [
            "All images and sounds are from the original Squid Game series.",
            "This game is a fan project and not affiliated with Netflix.",
            "Developed by PixelHyperCube with Python and Pygame.",
        ]
        for i, line in enumerate(credit_lines):
            helper.render_text(frame, line, WIDTH // 2, HEIGHT // 3 + i * 40, font_size=22)
        
        # Version
        helper.render_text(frame, "Version 1.0.1", WIDTH // 2, HEIGHT - 30, font_size=18)

        # Buttons
        self.back_btn.render(frame)

        if mouse_x>=WIDTH/2-90 and mouse_x<=WIDTH/2+90 and mouse_y>=HEIGHT*0.625-50 and mouse_y<=HEIGHT*0.625+50:
            helper.render_image(frame,"./assets/img/invitationBackGH.png",WIDTH//2,HEIGHT*0.625,(90,50))
        else:
            helper.render_image(frame,"./assets/img/invitationFrontGH.png",WIDTH//2,HEIGHT*0.625,(90,50))
    
    def keydown_listener(self,event):
        pass
    def keyup_listener(self,event):
        pass