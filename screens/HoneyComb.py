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
from objects.Dalgona import Dalgona

helper = Helper()

class HoneyComb(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,time_left=60,dalgona_size=150):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.33,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]
        self.game_state = -1
        self.dalgona_size = dalgona_size
        # dalgona
        self.dalgona_shapes = ["circle", "star", "triangle", "umbrella"]
        self.dalgona = Dalgona(WIDTH//2, HEIGHT//2, self.dalgona_size, Color.HONEYCOMB_YELLOW,self.dalgona_shapes[random.randint(0, len(self.dalgona_shapes) - 1)])
        self.selected_shape = None

    def restart_game(self):
        self.game_state = -1
        self.dalgona.reset()

        self.help_back_btn.visible = True
        self.help_start_btn.visible = True

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False

    def toggle_game_state(self,frame,state):
        self.game_state = state
        if state==1:
            self.paused = True
            self.return_lvls_btn.visible = True
            self.render_success(frame)
        elif state==2:
            self.paused = True
            self.return_lvls_btn.visible = True
            self.render_fail(frame)
        elif state==0:
            self.paused = False
            self.help_back_btn.visible = False
            self.help_start_btn.visible = False
        elif state==-1:
            self.paused = True
            self.return_lvls_btn.visible = False
            self.render_help(frame)

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

    def keyup_listener(self, key):
        pass

    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)

    def draw_needle(self, frame, mouse_x, mouse_y):
        length = 100 
        width = 10
        angle_deg = 45
        angle_rad = math.radians(angle_deg)

        tip = (mouse_x, mouse_y)

        base_left = (mouse_x - width // 2, mouse_y + length)
        base_right = (mouse_x + width // 2, mouse_y + length)

        def rotate_point(px, py, cx, cy, angle):
            sin_a = math.sin(angle)
            cos_a = math.cos(angle)
            dx = px - cx
            dy = py - cy
            rx = cos_a * dx - sin_a * dy + cx
            ry = sin_a * dx + cos_a * dy + cy
            return (rx, ry)

        base_left_rotated = rotate_point(*base_left, *tip, angle_rad)
        base_right_rotated = rotate_point(*base_right, *tip, angle_rad)

        pg.draw.polygon(frame, Color.GREY, [tip, base_left_rotated, base_right_rotated])
        pg.draw.polygon(frame, Color.SQUID_GREY, [tip, base_left_rotated, base_right_rotated], width=2)
    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            pg.draw.rect(frame, self.bg_color, (0, 0, WIDTH, HEIGHT))
            self.dalgona.render(frame)
            self.draw_needle(frame,mouse_x,mouse_y)
        else:
            if self.game_state == 1:
                self.render_success(frame)
            elif self.game_state == 2:
                self.render_fail(frame)
            elif self.game_state == -1:
                self.render_help(frame)
            else:
                self.render_paused(frame)
        
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