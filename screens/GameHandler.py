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
        pg.draw.rect(frame,Color.SQUID_GREY,(WIDTH/2-80,HEIGHT//3,160,80))
        helper.render_text(frame,"Get ready in",WIDTH/2,HEIGHT//3+20,font_size=20)
        helper.render_text(frame,str(time_left),WIDTH/2,HEIGHT//3+50,font_size=30)
    def render_seven_seg_num(self,frame,x,y,digit,off_color=Color.DARK_GREY,on_color=Color.SQUID_PINK,font_size=20):
        segments = {
            "A": [(2,1),(3,0),(7,0),(8,1),(7,2),(3,2)],
            "B": [(9,2),(10,3),(10,7),(9,8),(8,7),(8,3)],
            "C": [(9,10),(10,11),(10,15),(9,16),(8,15),(8,11)],
            "D": [(2,17),(3,16),(7,16),(8,17),(7,18),(3,18)],
            "E": [(1,10),(2,11),(2,15),(1,16),(0,15),(0,11)],
            "F": [(1,2),(2,3),(2,7),(1,8),(0,7),(0,3)],
            "G": [(2,9),(3,8),(7,8),(8,9),(7,10),(3,10)],
        }
        digit_segments = {
            '0': ['A','B','C','D','E','F'],
            '1': ['B','C'],
            '2': ['A','B','G','E','D'],
            '3': ['A','B','C','D','G'],
            '4': ['F','G','B','C'],
            '5': ['A','F','G','C','D'],
            '6': ['A','F','G','E','C','D'],
            '7': ['A','B','C'],
            '8': ['A','B','C','D','E','F','G'],
            '9': ['A','B','C','D','F','G'],
        }
        scale = font_size//8
        active = digit_segments.get(str(digit),[])

        for name, points in segments.items():
            scaled_points = [(x + px * scale, y + py * scale) for px, py in points]
            color = on_color if name in active else off_color
            pg.draw.polygon(frame, color, scaled_points)

    def render_timer(self,x,y,frame,time_left,on_color=Color.SQUID_PINK,off_color=Color.DARK_GREY,font_size=20):
        time_seconds = (time_left//60)%60
        time_minutes = math.floor(time_left//3600)
        time_disp = f"{("0" if time_minutes<10 else "") + str(time_minutes)}:{("0" if time_seconds<10 else "") + str(time_seconds)}"
        
        char_spacing = font_size+5
        total_width = len(time_disp)*char_spacing+7
        box_height = font_size*2+7

        pg.draw.rect(frame, Color.SQUID_GREY, (x, y, total_width, box_height))
        pg.draw.rect(frame, on_color, (x, y, total_width, box_height),width=2)
        for i, d in enumerate(time_disp):
            if d!=":":
                self.render_seven_seg_num(frame, x + i * 25+5, y+5, d,on_color=on_color,off_color=off_color,font_size=font_size)
            else:
                pg.draw.rect(frame,on_color,(x+i*25+font_size//2+3,y+10,font_size//3,font_size//3))
                pg.draw.rect(frame,on_color,(x+i*25+font_size//2+3,y+30,font_size//3,font_size//3))
    def handle_buttons(self,event,mouse_x,mouse_y,current_screen):
        next_screen = current_screen
        for btn in self.buttons:
            if btn.visible:
                next_screen = btn.click_listener(event, mouse_x, mouse_y, next_screen)
        return next_screen