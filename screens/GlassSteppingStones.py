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
    def __init__(self, time=300, preparation_time=5, bg_color=Color.BLACK,start_y=HEIGHT-100,finish_y=100,time_left=120,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.1,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back\nto Levels", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        self.player = Player(50,HEIGHT//2+50,10,Color.SQUID_TEAL,stroke_color=Color.DARK_RED,stroke_thickness=3)

        self.players = []

        # generate correct path
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

        self.time_left = time_left*60

        self.cooldown = random.randint(50,75)
        self.next_cooldown = self.in_game_frame_count + self.cooldown
        self.is_game_win = None

        self.player_index = 0

        self.wait_cooldown = 100
        self.next_wait_cooldown = self.in_game_frame_count + self.wait_cooldown

    # helper function to determine valid position
    def is_valid_position(self,placed_positions,x,y,r):
        for px, py in placed_positions:
            if math.hypot(x-px,y-py)<2*r:
                return False
        return True

    def set_players(self,r=10,players_count=15):
        distinct_nums = random.sample(range(1,501),players_count)
        self.player_index = random.randint(0,players_count-1)
        # self.player_index = 0 # debug
        placed_positions = []
        
        for i in range(players_count):
            while True:
                x = random.randint(10,80)
                y = random.randint(HEIGHT//2-60,HEIGHT//2+60)
                if not self.is_valid_position(placed_positions,x,y,r): continue
                placed_positions.append((x,y))
                if i==self.player_index:
                    self.player.num_label = distinct_nums[i]
                    self.player.set_pos(x,y)
                    self.player.__setattr__("moved",False)
                    self.player.__setattr__("eliminated",False)
                else:
                    player = Player(x,y,r,Color.get_random_color_from_base(Color.SQUID_TEAL),num_label=distinct_nums[i])
                    player.__setattr__("moved",False)
                    player.__setattr__("eliminated",False)
                    self.players.append(player)
                break
    def restart_game(self):
        self.in_game_frame_count = 0

        self.time_left = self.time * 60
        self.preparation_time = 5
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
        self.player = Player(50,HEIGHT//2+50,10,Color.SQUID_TEAL,stroke_color=Color.DARK_RED,stroke_thickness=3)
        self.cooldown = random.randint(50,75)
        self.next_cooldown = self.in_game_frame_count + self.cooldown

        self.help_back_btn.visible = True
        self.help_start_btn.visible = True

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False

        self.is_game_win = None
        self.players = []
        self.set_players()

    def render_dialog(self,frame,pos,dim,player,font_size=20,color=Color.DARK_GREY,stroke_color=Color.WHITE,stroke_thickness=3):
        x,y = pos
        w,h = dim
        pg.draw.rect(frame,color,(*pos,*dim))
        pg.draw.rect(frame,stroke_color,(*pos,*dim),width=stroke_thickness)


        helper.render_text(frame,f"Your Turn!",int(x)+w//2,y+30,font_size=font_size)
        pg.draw.circle(frame,player.stroke_color,(int(x)+w//2,h-30+y),14)
        pg.draw.circle(frame,player.color,(int(x)+w//2,h-30+y),12)
        helper.render_text(frame,str(player.num_label),int(x)+w//2,h-30+y,font_size=12)
    
    def render_waiting_dialog(self,frame,pos,dim,font_size=20,color=Color.DARK_GREY,stroke_color=Color.WHITE,stroke_thickness=3):
        x,y = pos
        w,h = dim
        pg.draw.rect(frame,color,(*pos,*dim))
        pg.draw.rect(frame,stroke_color,(*pos,*dim),width=stroke_thickness)


        helper.render_text(frame,f"Wait for your turn!",int(x)+w//2,y+30,font_size=font_size)

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

            for player in self.players:
                if not (hasattr(player,"eliminated") and player.eliminated):
                    player.render(frame)

            self.player.render(frame)


            px,py = self.player.pos
            r = self.player.r
            if py<=HEIGHT//2 or px<100:
                pg.draw.polygon(frame,Color.RED,[(px-r,py-r*2.5),(px+r,py-r*2.5),(px,py-r-7)])
                pg.draw.polygon(frame,Color.BLACK,[(px-r,py-r*2.5),(px+r,py-r*2.5),(px,py-r-7)],width=2)
            else:
                pg.draw.polygon(frame,Color.RED,[(px-r,py+r*2.5),(px+r,py+r*2.5),(px,py+r+7)])
                pg.draw.polygon(frame,Color.BLACK,[(px-r,py+r*2.5),(px+r,py+r*2.5),(px,py+r+7)],width=2)
            

            # dialog rendering: optional
            number_moving_players = len([p for p in self.players if hasattr(p,"moved") and p.moved]) + (1 if hasattr(self.player,"moved") and self.player.moved else 0)
            # helper.render_text(frame,f"{str(number_moving_players)} {str(self.player_index)}",100,100)
            if self.player_index==number_moving_players:
                self.render_dialog(frame,(WIDTH//2-100,20),(200,100),self.player,font_size=20)

            if self.next_wait_cooldown>self.in_game_frame_count and self.in_game_frame_count>self.wait_cooldown:
                self.render_waiting_dialog(frame,(WIDTH//2-100,20),(200,60),font_size=20)

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if not in_preparation:
                if self.in_game_frame_count==self.next_cooldown and self.player_index!=number_moving_players:
                    self.comp_next_step()
                    self.next_cooldown = self.in_game_frame_count + self.cooldown

            self.render_timer(10,10,frame,self.time_left)

            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            elif self.preparation_time*60-self.in_game_frame_count==0:
                self.next_cooldown = self.in_game_frame_count + self.cooldown
            else:
                self.time_left-=1

            # game over:
            if self.time_left<=0:
                self.toggle_game_state(frame,2)

            helper.render_text(frame,"Press 'Esc' or 'P' to pause",WIDTH-20,HEIGHT-20,font_size=18,color=Color.WHITE,align="right")
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

        # priority list of movable players
        movable_players = [
            player for player in self.players
            if hasattr(player,"step_index") and 0<=player.step_index<=len(self.correct_path)
            and not (hasattr(player,"eliminated") and player.eliminated)
        ]

        movable_player = None
        
        if len(movable_players)>0:
            movable_player_index = random.randint(0,len(movable_players)-1) if len(movable_players)>1 else 0
            movable_player = movable_players[movable_player_index]
        
        alive_players = [player for player in self.players if not (hasattr(player,"eliminated") and player.eliminated)]

        player_index = random.randint(0,len(alive_players)-1)
        player = alive_players[player_index] if random.random()<0.2 or movable_player is None else movable_player

        self.cooldown = random.randint(50,75)

        if not hasattr(player,"step_index"):
            player.step_index = 0

        if hasattr(player,"moved"):
            player.moved = True
        
        i = player.step_index
        if i>=len(self.correct_path):
            r = getattr(player,"r",10)
            if not hasattr(player,"winning_pos"):
                placed_positions = [
                    other.winning_pos for other in self.players
                    if hasattr(other,"winning_pos")
                ]

                while True:
                    x = random.randint(WIDTH-80,WIDTH-10)
                    y = random.randint(HEIGHT//2-60,HEIGHT//2+60)
                    if self.is_valid_position(placed_positions,x,y,r):
                        player.winning_pos = (x,y)
                        break
            
            wx,wy = player.winning_pos
            player.set_pos(wx,wy)
            return

        known = self.known_safe[i]
        choice = known if self.known_safe[i] is not None else random.randint(0,1)
        
        glass = self.glass_blocks_left[i] if choice==0 else self.glass_blocks_right[i]

        x,y = glass.pos
        w,h = glass.dim
        px = x+w//2 + random.uniform(-7,7)
        py = y+h//2 + random.uniform(-7,7)
        player.set_pos(px,py)

        if choice != self.correct_path[i]:
            glass.broken = True
            player.eliminated = True
            # self.players.remove(player)
            helper.play_sound("./assets/sounds/glassBreak.wav",volume=0.3)
        else:
            player.step_index += 1
            helper.play_sound("./assets/sounds/step.wav")
        self.known_safe[i] = self.correct_path[i]
        
    def player_next_step(self,choice):
        if not hasattr(self.player,"step_index"):
            self.player.step_index = 0
        
        i = self.player.step_index

        # last glass
        if i>=len(self.correct_path)-1:
            self.is_game_win = True
            return

        if hasattr(self.player,"moved"):
            self.player.moved = True

        glass = self.glass_blocks_left[i] if choice==0 else self.glass_blocks_right[i]

        x,y = glass.pos
        w,h = glass.dim
        px = x+w//2 + random.uniform(-7,7)
        py = y+h//2 + random.uniform(-7,7)
        self.player.set_pos(px,py)

        self.known_safe[i] = self.correct_path[i]

        if choice != self.correct_path[i]:
            glass.broken = True
            self.is_game_win = False
            helper.play_sound("./assets/sounds/glassBreak.wav",volume=0.4)
            # game over!
            return
        else:
            self.player.step_index += 1
            helper.play_sound("./assets/sounds/step.wav")
        
        self.next_cooldown = self.in_game_frame_count + self.cooldown


    def keydown_listener(self,key):
        if key == pg.K_ESCAPE or key == pg.K_p:
            if self.game_state == 0:
                self.toggle_paused()
        # elif key==pg.K_UP:
        #     in_preparation = self.preparation_time*60-self.in_game_frame_count>0
        #     if not self.paused and not in_preparation:
        #         self.player_next_step(1)
        # elif key==pg.K_DOWN:
        #     in_preparation = self.preparation_time*60-self.in_game_frame_count>0
        #     if not self.paused and not in_preparation:
        #         self.player_next_step(0)

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
            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if not self.paused and not in_preparation:
                if not hasattr(self.player,"step_index"):
                    self.player.step_index = 0
                step_index = self.player.step_index
                if step_index<len(self.glass_blocks_left):
                    number_moving_players = len([p for p in self.players if hasattr(p,"moved") and p.moved]) + (1 if hasattr(self.player,"moved") and self.player.moved else 0)
                    left_block = self.glass_blocks_left[step_index]
                    right_block = self.glass_blocks_right[step_index]
                    if left_block.contains(mouse_x,mouse_y):
                        if self.player_index<=number_moving_players:
                            self.player_next_step(0)
                        else:
                            self.next_wait_cooldown = self.in_game_frame_count + self.wait_cooldown
                    elif right_block.contains(mouse_x,mouse_y):
                        if self.player_index<=number_moving_players:
                            self.player_next_step(1)
                        else:
                            self.next_wait_cooldown = self.in_game_frame_count + self.wait_cooldown
                        

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
        helper.render_text(frame,"How to play: Glass Stepping Stones",WIDTH/2,HEIGHT/12,font_size=30,underline=True)
        helper.render_text(
            frame, "Objective: Reach the end by stepping\nonly on tempered glass panels.",
            WIDTH // 2, HEIGHT // 5.9, font_size=22, color=Color.WHITE
        )

        helper.render_image(
            frame, "./assets/img/glasssteppingstones/demoNoTime.png",
            WIDTH // 2, HEIGHT // 1.85, [int(500 / 2), int(375 / 2)]
        )

        helper.render_text(
            frame, "Each round, only one player is allowed to move.",
            WIDTH // 2, HEIGHT // 4, font_size=20, color=Color.WHITE
        )

        helper.render_text(
            frame, "Wait patiently for your turn!",
            WIDTH // 2, HEIGHT // 3.4, font_size=20, color=Color.WHITE
        )

        helper.render_text(
            frame, "Only one panel in each pair is safe. Choose wisely.",
            WIDTH // 2, HEIGHT // 1.28, font_size=20, color=Color.WHITE
        )

        helper.render_text(
            frame, "Tip: You will see a prompt when it's your turn to move.",
            WIDTH // 2, HEIGHT // 1.22, font_size=18, color=Color.WHITE
        )

        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(frame,0) 

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
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)