from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from objects.GlassBlock import GlassBlock
from objects.Circle import Circle
from screens.GameHandler import GameHandler
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from components.Button import Button
import numpy as np

helper = Helper()

class GlassSteppingStones(GameHandler):
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

        self.player = Player(0,0,8,Color.SQUID_LIGHT_TEAL,stroke_color=Color.SQUID_PURPLE2,stroke_thickness=2,num_label=str(random.randint(1,500)))

        self.players = []

        self.correct_path = [1 for _ in range(9)] + [0 for _ in range(9)]
        np.random.shuffle(self.correct_path)
        self.known_safe = [None] * 18

        self.glass_blocks_left = [
            GlassBlock(i*34+103,HEIGHT//2+10,25,25,Color.WHITE,stroke_thickness=2,breakable=state==0) for i,state in enumerate(self.correct_path)
            # GlassBlock(i*34+103,HEIGHT//2+10,25,25,Color.YELLOW if self.correct_path[i]==0 else Color.WHITE,stroke_thickness=2,breakable=state==0) for i,state in enumerate(self.correct_path)
        ]
        self.glass_blocks_right = [
            GlassBlock(i*34+103,HEIGHT//2-30,25,25,Color.WHITE,stroke_thickness=2,breakable=state==1) for i,state in enumerate(self.correct_path)
            # GlassBlock(i*34+103,HEIGHT//2-30,25,25,Color.YELLOW if self.correct_path[i]==1 else Color.WHITE,stroke_thickness=2,breakable=state==1) for i,state in enumerate(self.correct_path)
        ]

        self.game_state = -1

        self.cooldown = 50
        self.next_cooldown = self.in_game_frame_count + self.cooldown
        self.current_player = 0
        self.is_game_win = None

    def set_players(self,r=8,players_count=16):
        player_index = random.randint(0,players_count-1)
        self.player.num_label = player_index
        for i in range(players_count):
            if i==player_index:
                self.player.set_pos(80-(i%5)*(r+1)*2,(r+1)*2*(i//5)+HEIGHT//2.25)
                self.players.append(self.player)
            else:
                self.players.append(Player(80-(i%5)*(r+1)*2,(r+1)*2*(i//5)+HEIGHT//2.25,r,Color.SQUID_TEAL,num_label=random.randint(1,500)))

    def restart_game(self):
        self.in_game_frame_count = 0
        self.game_state = -1
        self.correct_path = [1 for _ in range(9)] + [0 for _ in range(9)]
        np.random.shuffle(self.correct_path)
        self.known_safe = [None] * 18
        self.glass_blocks_left = [
            GlassBlock(i*34+103,HEIGHT//2+10,25,25,Color.WHITE,stroke_thickness=2,breakable=state==0) for i,state in enumerate(self.correct_path)
            # GlassBlock(i*34+103,HEIGHT//2+10,25,25,Color.YELLOW if self.correct_path[i]==0 else Color.WHITE,stroke_thickness=2,breakable=state==0) for i,state in enumerate(self.correct_path)
        ]
        self.glass_blocks_right = [
            GlassBlock(i*34+103,HEIGHT//2-30,25,25,Color.WHITE,stroke_thickness=2,breakable=state==1) for i,state in enumerate(self.correct_path)
            # GlassBlock(i*34+103,HEIGHT//2-30,25,25,Color.YELLOW if self.correct_path[i]==1 else Color.WHITE,stroke_thickness=2,breakable=state==1) for i,state in enumerate(self.correct_path)
        ]
        self.player = Player(0,0,8,Color.SQUID_LIGHT_TEAL,stroke_color=Color.SQUID_PURPLE2,stroke_thickness=2,num_label=str(random.randint(1,500)))
        self.current_player = 0
        self.cooldown = 50
        self.next_cooldown = self.in_game_frame_count + self.cooldown

        self.help_back_btn.visible = True
        self.help_start_btn.visible = True

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False

        self.is_game_win = None
        self.players = []
        self.set_players()

    def render_dialog(self,frame,pos,dim,player_index,font_size=20,color=Color.SQUID_PURPLE,stroke_color=Color.WHITE,stroke_thickness=3):
        if player_index < 0 or player_index >= len(self.players):
            return
        x,y = pos
        w,h = dim
        pg.draw.rect(frame,color,(*pos,*dim))
        pg.draw.rect(frame,stroke_color,(*pos,*dim),width=stroke_thickness)

        helper.render_text(frame,f"Player {self.players[player_index].num_label}'s Turn!",int(x)+w//2,y+30,font_size=font_size)
        pg.draw.circle(frame,Color.BLACK,(int(x)+w//2,h-30+y),14)
        pg.draw.circle(frame,Color.SQUID_TEAL,(int(x)+w//2,h-30+y),12)
        helper.render_text(frame,str(self.players[player_index].num_label),int(x)+w//2,h-30+y,font_size=12)

    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            if self.is_game_win is not None:
                if self.is_game_win:
                    self.toggle_game_state(frame,1)
                else:
                    self.toggle_game_state(frame,2)

            frame.fill(self.bg_color)

            Circle(0,HEIGHT//2,100,Color.SQUID_PINK,stroke_color=Color.SQUID_LIGHT_TEAL,stroke_thickness=2).render(frame)
            Circle(WIDTH+10,HEIGHT//2,100,Color.SQUID_PINK,stroke_color=Color.SQUID_LIGHT_TEAL,stroke_thickness=2).render(frame)

            pg.draw.line(frame,Color.GREY,(103,HEIGHT//2+35),((len(self.correct_path))*34+103,HEIGHT//2+35),width=3)
            pg.draw.line(frame,Color.GREY,(103,HEIGHT//2-32),((len(self.correct_path))*34+103,HEIGHT//2-32),width=3)
            for i in range(154):
                pg.draw.circle(frame,Color.WHITE,(4*i+103,HEIGHT//2+35),1)
                pg.draw.circle(frame,Color.WHITE,(4*i+103,HEIGHT//2-32),1)

            for glass in self.glass_blocks_left+self.glass_blocks_right:
                if not glass.broken:
                    glass.render(frame)

            # for i,state in enumerate(self.correct_path):
                # Block(i*34+103,HEIGHT//2+10,25,25,Color.WHITE if state==0 else Color.YELLOW,stroke_thickness=2).render(frame)
                # Block(i*34+103,HEIGHT//2-30,25,25,Color.WHITE if state==1 else Color.YELLOW,stroke_thickness=2).render(frame)
            
            for player in self.players:
                player.render(frame)
            
            helper.render_text(frame,str(self.current_player),50,20)
            if 0 <= self.current_player < len(self.players):
                self.render_dialog(frame,(WIDTH//2-100,20),(200,100),self.current_player,font_size=20)

            if self.in_game_frame_count==self.next_cooldown:
                if self.current_player<len(self.players):
                    player = self.players[self.current_player]
                    if getattr(player,'step_index',0) < len(self.correct_path):
                        self.comp_next_step()
                    else:
                        self.current_player+=1
                self.next_cooldown = self.in_game_frame_count + self.cooldown

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

    def comp_next_step(self):
        if self.current_player>=len(self.players):
            return

        player = self.players[self.current_player]
        if player==self.player:
            return

        if not hasattr(player,"step_index"):
            player.step_index = 0
        
        i = player.step_index
        if i>=len(self.correct_path):
            return

        known = self.known_safe[i]
        choice = known if known is not None else random.randint(0,1)

        glass = self.glass_blocks_left[i] if choice==0 else self.glass_blocks_right[i]

        x,y = glass.pos
        w,h = glass.dim
        player.set_pos(x+w//2,y+h//2)

        self.known_safe[i] = self.correct_path[i]

        if choice != self.correct_path[i]:
            glass.broken = True
            del self.players[self.current_player]
            self.current_player = max(self.current_player-1,0)
            return
        else:
            player.step_index += 1
        
    def player_next_step(self,choice):
        if not hasattr(self.player,"step_index"):
            self.player.step_index = 0
        
        i = self.player.step_index
        if i>=len(self.correct_path):
            self.is_game_win = True
            return

        # known = self.known_safe[i]

        glass = self.glass_blocks_left[i] if choice==0 else self.glass_blocks_right[i]

        x,y = glass.pos
        w,h = glass.dim
        self.player.set_pos(x+w//2,y+h//2)

        self.known_safe[i] = self.correct_path[i]

        if choice != self.correct_path[i]:
            glass.broken = True
            self.is_game_win = False
            # game over!
            return
        else:
            self.player.step_index += 1


    def keydown_listener(self,key):
        if key == pg.K_ESCAPE or key == pg.K_p:
            if self.game_state == 0:
                self.toggle_paused()
        elif key==pg.K_0:
            if not self.paused:
                self.player_next_step(0)
        elif key==pg.K_1:
            if not self.paused:
                self.player_next_step(1)

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
        pass

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