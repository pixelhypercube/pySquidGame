from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from objects.Block import Block
from objects.Circle import Circle
from screens.GameHandler import GameHandler
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from components.Button import Button

helper = Helper()

class TugOfWar(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.BLACK,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.33,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        self.num_players = 10
        self.player_size = 10

        self.platform_left = Block(0,HEIGHT//2,WIDTH//2-75,20,Color.YELLOW)
        self.platform_right = Block(WIDTH//2+75,HEIGHT//2,WIDTH//2-75,20,Color.YELLOW)

        self.players_left = [
            Player(50+i*self.player_size*2,HEIGHT//2-self.player_size,self.player_size,Color.SQUID_TEAL,num_label=random.randint(1,500)) for i in range(self.num_players)
        ]

        self.players_right = [
            Player(WIDTH-50-i*self.player_size*2,HEIGHT//2-self.player_size,self.player_size,Color.SQUID_TEAL,num_label=random.randint(1,500)) for i in range(self.num_players)
        ]

        self.rope = Block(50,HEIGHT//2-2*self.player_size+2,700,2,Color.SAND)

        self.balance = 0

        self.game_state = -1

        self.prev_mouse_x = None
        self.mouse_x_speed = 0

        self.pull_duration = 20
        self.pull_duration_cooldown = self.in_game_frame_count + self.pull_duration
        self.pull_cooldown = 50
        self.next_pull_cooldown = self.in_game_frame_count + self.pull_cooldown

    def get_mouse_x_speed(self,mouse_x):
        prev_mouse_x = self.prev_mouse_x
        self.prev_mouse_x = mouse_x
        if prev_mouse_x is not None:
            return mouse_x-prev_mouse_x

    def set_balance(self,balance):
        rope_y = self.rope.pos[1]
        self.balance = balance
        self.rope.pos = [50 + self.balance,rope_y]
        for i,player in enumerate(self.players_left):
            player_y = player.pos[1]
            player.set_pos(50+i*self.player_size*2+self.balance,player_y)
        for i,player in enumerate(self.players_right):
            player_y = player.pos[1]
            player.set_pos(WIDTH-50-i*self.player_size*2+self.balance,player_y)

    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            frame.fill(self.bg_color)

            self.platform_left.render(frame)
            self.platform_right.render(frame)
            
            self.set_balance(self.balance+self.mouse_x_speed//10)

            for player in self.players_left+self.players_right:
                player.render(frame)
            
            self.rope.render(frame)

            if (self.in_game_frame_count==self.next_pull_cooldown):
                self.pull_duration_cooldown = self.in_game_frame_count + self.pull_duration
                self.next_pull_cooldown = self.in_game_frame_count + self.pull_cooldown

            if self.in_game_frame_count<self.pull_duration_cooldown and self.in_game_frame_count>self.pull_duration:
                force = 0.3*(self.pull_duration_cooldown-self.in_game_frame_count)
                self.set_balance(self.balance-force)

            rightmost_left_player = self.players_left[len(self.players_left)-1]
            leftmost_right_player = self.players_right[len(self.players_right)-1]
            fall_left = self.platform_left.pos[0] + self.platform_left.dim[0]
            fall_right = self.platform_right.pos[0]
            if rightmost_left_player.pos[0]>fall_left:
                self.toggle_game_state(frame,1)
            elif leftmost_right_player.pos[0]<fall_right:
                self.toggle_game_state(frame,2)

            self.in_game_frame_count += 1
        else:
            if self.game_state == 1:
                self.render_success(frame)
            elif self.game_state == 2:
                self.render_fail(frame)
            elif self.game_state == -1:
                self.render_help(frame)
            else:
                self.render_paused(frame)

    def keydown_listener(self,key):
        if key == pg.K_ESCAPE or key == pg.K_p:
            if self.game_state == 0:
                self.toggle_paused()

    def toggle_paused(self):
        self.paused = not self.paused

        if self.paused:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()

        self.restart_btn.visible = self.paused
        self.exit_btn.visible = self.paused

    def keyup_listener(self,key):
        pass

    def mousedown_listener(self,event,mouse_x,mouse_y):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.prev_mouse_x = mouse_x
        if event.type == pg.MOUSEMOTION:
            if not self.paused and pg.mouse.get_pressed()[0]:
                self.mouse_x_speed = self.get_mouse_x_speed(mouse_x)
            else:
                self.mouse_x_speed = 0
    
    def mouseup_listener(self,event,mouse_x,mouse_y):
        pass

    def restart_game(self):
        self.in_game_frame_count = 0
        self.pull_duration = 20
        self.pull_duration_cooldown = self.in_game_frame_count + self.pull_duration
        self.pull_cooldown = 50
        self.next_pull_cooldown = self.in_game_frame_count + self.pull_cooldown
        self.platform_left = Block(0,HEIGHT//2,WIDTH//2-75,20,Color.YELLOW)
        self.platform_right = Block(WIDTH//2+75,HEIGHT//2,WIDTH//2-75,20,Color.YELLOW)

        self.players_left = [
            Player(50+i*self.player_size*2,HEIGHT//2-self.player_size,self.player_size,Color.SQUID_TEAL,num_label=random.randint(1,500)) for i in range(self.num_players)
        ]

        self.players_right = [
            Player(WIDTH-50-i*self.player_size*2,HEIGHT//2-self.player_size,self.player_size,Color.SQUID_TEAL,num_label=random.randint(1,500)) for i in range(self.num_players)
        ]

        self.rope = Block(50,HEIGHT//2-2*self.player_size+2,700,2,Color.SAND)

        self.balance = 0

        self.game_state = -1

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
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)