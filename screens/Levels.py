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

class Levels(GameHandler):
    def __init__(self):
        super().__init__(0, 0, Color.SQUID_GREY)
        self.lvl_num_btns = []
        self.game_names = ["Red Light,\n Green Light","Honeycomb \n(Coming Soon!)","Tug Of War \n(Coming Soon!)","Marbles \n(Coming Soon!)","Glass Stepping\n Stones \n(Coming Soon!)","Squid Game \n(Coming Soon!)"]
        self.game_image_names = ["red_light_green_light","honey_comb","tug_of_war","marbles","glass_stepping_stones","squid_game"]
        self.back_btn = Button(80,HEIGHT/5,50,25,content="Back",next_screen="home")

        for i in range(1,4):
            if i==1:
                self.lvl_num_btns.append(Button(i*200,(HEIGHT/2)+30,90,50,content=self.game_names[i-1],next_screen=self.game_image_names[i-1]+"_help",function=None,image_path="./assets/img/levels/"+self.game_image_names[i-1]+".png"))
            else:
                self.lvl_num_btns.append(Button(i*200,(HEIGHT/2)+30,90,50,content=self.game_names[i-1],next_screen="levels",function=None,image_path="./assets/img/levels/"+self.game_image_names[i-1]+".png"))
        for i in range(4,7):
            if i==4:
                self.lvl_num_btns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,content=self.game_names[i-1],next_screen=self.game_image_names[i-1]+"_help",function=None,image_path="./assets/img/levels/"+self.game_image_names[i-1]+".png"))
            else:
                self.lvl_num_btns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,content=self.game_names[i-1],next_screen="levels",function=None,image_path="./assets/img/levels/"+self.game_image_names[i-1]+".png"))
        self.buttons = [self.back_btn] + self.lvl_num_btns

    def render(self, frame, mouse_x, mouse_y):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Choose a stage!",WIDTH/2,HEIGHT/5,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to pause",WIDTH/2,220,font_size=15)
        self.back_btn.render(frame)
        for btn in self.lvl_num_btns:
            btn.render(frame)