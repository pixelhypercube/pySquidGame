import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from components.Helper import Helper
from components.Color import Color
from components.Button import Button
from Settings import WIDTH, HEIGHT
from screens.GameHandler import GameHandler
from objects.Ddakji import Ddakji
import numpy as np

helper = Helper()

class DdakjiGame(GameHandler):
    def __init__(self, time=6000000, preparation_time=5, bg_color=Color.SQUID_GREY):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.1,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back\nto Levels", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        self.player_turn = 1
        
        self.game_state = -1

        self.is_grabbing = False
        
        self.player_1 = Ddakji(WIDTH//2-30,HEIGHT//2,50,50,Color.SQUID_PINK,stroke_thickness=3)
        self.player_2 = Ddakji(WIDTH//2+30,HEIGHT//2,50,50,Color.SQUID_TEAL,stroke_thickness=3)
    
    def restart_game(self):
        self.player_1 = Ddakji(WIDTH//2-30,HEIGHT//2,50,50,Color.SQUID_PINK,stroke_thickness=3)
        self.player_2 = Ddakji(WIDTH//2+30,HEIGHT//2,50,50,Color.SQUID_TEAL,stroke_thickness=3)

        self.game_state = -1

        self.is_grabbing = False

        self.player_turn = 1

        self.help_back_btn.visible = True
        self.help_start_btn.visible = True

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False

    def toggle_game_state(self,state):
        self.game_state = state
        if state==1:
            self.paused = True
            self.return_lvls_btn.visible = True
        elif state==2:
            self.paused = True
            self.return_lvls_btn.visible = True
        elif state==0:
            self.paused = False
            self.help_back_btn.visible = False
            self.help_start_btn.visible = False
        elif state==-1:
            self.paused = True
            self.return_lvls_btn.visible = False
    
    def render_health_bar(self,frame,player,pos=[WIDTH//2,0],dim=[200,30],color=Color.RED,left_text="",right_text=""):
        x,y = pos
        w,h = dim
        health = player.health
        max_health = self.player_1.max_health
        pg.draw.rect(frame,Color.adj_color_brightness(color,0.2),(x-w//2,y,w,h))
        pg.draw.rect(frame,color,(x-w//2,y,(health/max_health)*w,h))
        pg.draw.rect(frame,Color.adj_color_brightness(color,0.2),(x-w//2,y,w,h),width=2)
        helper.render_text(frame,"Health",x,y+h//2,color=Color.WHITE,font_size=18)
        helper.render_text(frame,left_text,x-w//2-5,y+h//2,color=Color.BLACK,align="right",font_size=18)
        helper.render_text(frame,right_text,x+w//2+5,y+h//2,color=Color.BLACK,align="left",font_size=18)

    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            frame.fill(Color.LIGHT_GREY)
            # for i in range(0,HEIGHT,40):
            #     for j in range(0,WIDTH,40):
            #         pg.draw.rect(frame,Color.DARK_GREY,(j,i,40,40),width=1)
            #         pg.draw.rect(frame,(180,180,180),(j+5,i+5,20,5))
            
            helper.render_text(frame,f"Player {self.player_turn}'s Turn!",WIDTH//2,HEIGHT//2,color=Color.BLACK)
            
            # order of player's turn
            if self.player_turn==1:
                self.player_2.render(frame)
                self.player_1.render(frame)
            else:
                self.player_1.render(frame)
                self.player_2.render(frame)

            self.render_health_bar(frame,self.player_1,left_text="You",color=self.player_1.color)
            self.render_health_bar(frame,self.player_2,left_text="Computer",pos=[WIDTH//2,HEIGHT-30],color=self.player_2.color)

            if self.player_1.is_intersect(self.player_2) and 5 < (self.player_1.z if self.player_turn==1 else self.player_2.z) < 10:
                self.player_2.z = 1
                self.player_2.dz = abs(np.random.normal(0.5,0.25))
                self.player_2.d_angle = np.random.normal(0,0.1)

                self.player_1.z = 1
                self.player_1.dz = abs(np.random.normal(0.5,0.25))
                self.player_1.d_angle = np.random.normal(0,0.1)
                
                self.player_1.vel = [np.random.normal(0,0.25),np.random.normal(0,0.25)]
                self.player_2.vel = [np.random.normal(0,0.25),np.random.normal(0,0.25)]

                helper.play_sound("./assets/sounds/drop.wav")
        else:
            if self.game_state == 1:
                self.render_success(frame)
            elif self.game_state == 2:
                self.render_fail(frame)
            elif self.game_state == -1:
                self.render_help(frame)
            else:
                self.render_paused(frame)

    def toggle_paused(self):
        self.paused = not self.paused

        if self.paused:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()

        self.restart_btn.visible = self.paused
        self.exit_btn.visible = self.paused

    def keydown_listener(self, key):
        if key == pg.K_ESCAPE or key == pg.K_p:
            if self.game_state == 0:
                self.toggle_paused()

    def keyup_listener(self,event):
        pass    

    def mousedown_listener(self,event,mouse_x,mouse_y):
        if not self.paused:
            if event.type==pg.MOUSEBUTTONDOWN:
                if self.player_turn==1:
                    if self.player_1.contains(mouse_x,mouse_y):
                        helper.play_sound("./assets/sounds/grab.wav")
                        self.player_1.is_grabbing = True
                elif self.player_turn==2:
                    if self.player_2.contains(mouse_x,mouse_y):
                        helper.play_sound("./assets/sounds/grab.wav")
                        self.player_2.is_grabbing = True
            elif event.type==pg.MOUSEBUTTONUP:
                if self.player_turn==1:
                    if self.player_1.is_grabbing:
                        self.player_1.smash()
                elif self.player_turn==2:
                    if self.player_2.is_grabbing:
                        self.player_2.smash()
            
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
        # helper.render_image(
        #     frame, "./assets/img/honeycomb/demo.png",
        #     WIDTH // 2, HEIGHT // 2.1, [int(500 / 2.25), int(375 / 2.25)]
        # )
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
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)