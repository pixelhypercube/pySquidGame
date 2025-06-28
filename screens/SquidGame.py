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

class SquidGame(GameHandler):
    def __init__(self, time=6000000, preparation_time=5, bg_color=Color.STONE,time_left=90,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        
        self.help_page = 0

        self.player_size = player_size
        self.wall_thickness = wall_thickness
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.08,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back\nto Levels", next_screen="levels")
        self.help_next_btn = Button(WIDTH - 80, HEIGHT - 40, 60, 25, content="Next",function=lambda: setattr(self, "help_page", self.help_page + 1 if self.help_page < 3 else 3))
        self.help_prev_btn = Button(80, HEIGHT - 40, 60, 25, content="Back",function=lambda: setattr(self, "help_page", self.help_page - 1 if self.help_page > 0 else 0))
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        
        self.labels_shown = False

        self.toggle_labels = Button(40, HEIGHT - 30, 30, 20, content="Toggle\nLabels",font_size=15,function=lambda: setattr(self,"labels_shown",not self.labels_shown),visible=not self.paused)

        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.help_next_btn,self.help_prev_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn,self.toggle_labels
        ]

        self.wall_blocks = [
            Block(0,0,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(0,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            Block(0,HEIGHT-self.wall_thickness,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(WIDTH-self.wall_thickness,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE)
        ]

        distinct_nums = random.sample(range(0,501),2)

        self.player_offender = Player(90,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=distinct_nums[0])
        self.player_offender.is_hopping = True
        self.player_offender.perm_hopping_disabled = False
        self.player_offender.crossed_areas = []
        self.player_offender.area = None
        self.player_offender.last_area = "A" # prev state area
        self.player_defender = Player(WIDTH//2,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=distinct_nums[1])
        self.player_defender.is_hopping = False
        self.player_defender.crossed_areas = []
        self.player_defender.area = None
        self.player_defender.perm_hopping_disabled = False
        self.player_defender.state = "waiting"
        self.player_defender.last_area = "D" # prev state area
        self.game_state = -1

        self.hopping_cooldown = 25
        self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown
        self.attack_cooldown = 3
        self.next_attack_cooldown = self.in_game_frame_count + self.attack_cooldown

        self.keys_held = {
            # player 1
            pg.K_w:False,
            pg.K_a:False,
            pg.K_s:False,
            pg.K_d:False,
            pg.K_f:False,

            # player 2
            pg.K_i:False,
            pg.K_j:False,
            pg.K_k:False,
            pg.K_l:False,
            pg.K_SEMICOLON:False,
        }

        # SQUID LAYOUT AREAS
        self.circle_A = Circle(WIDTH//2-300,HEIGHT//2,50,Color.WHITE) # A and C
        self.circle_B = Circle(WIDTH//2+300,HEIGHT//2,50,Color.WHITE) # B

        self.circle_E1 = Circle(WIDTH//2,HEIGHT//10,22,Color.WHITE) # E1
        self.circle_E2 = Circle(WIDTH//2,9*HEIGHT//10,22,Color.WHITE) # E2

        self.board_F1 = Block(WIDTH//2-20,HEIGHT//10,44,HEIGHT//2-30-HEIGHT//10,Color.WHITE)
        self.board_F2 = Block(WIDTH//2-20,HEIGHT//2+30,44,HEIGHT//2-30-HEIGHT//10,Color.WHITE)

        self.time_left = time_left*60

    def point_in_triangle(self, pt, v1, v2, v3):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        d1 = sign(pt, v1, v2)
        d2 = sign(pt, v2, v3)
        d3 = sign(pt, v3, v1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    def get_player_area(self,player):
        x,y = player.pos
        if self.circle_A.contains(x, y):
            C = (WIDTH//2 - 300, HEIGHT//2)
            E1 = (WIDTH//2 - 20, HEIGHT//10)
            E2 = (WIDTH//2 - 20, 9 * HEIGHT//10)
            if self.point_in_triangle((x, y), C, E1, E2):
                return 'C'
            else:
                return 'A'
        elif self.circle_B.contains(x, y):
            return 'B'
        elif self.circle_E1.contains(x, y):
            return 'E1'
        elif self.circle_E2.contains(x, y):
            return 'E2'
        elif self.board_F1.contains(x, y):
            return 'F1'
        elif self.board_F2.contains(x, y):
            return 'F2'
        C = (WIDTH//2 - 300, HEIGHT//2)
        E1 = (WIDTH//2 - 20, HEIGHT//10)
        E2 = (WIDTH//2 - 20, 9 * HEIGHT//10)
        if self.point_in_triangle((x, y), C, E1, E2) \
            or WIDTH//2+20 <= x <= WIDTH//2+300 and HEIGHT//10 <= y <= 9*HEIGHT//10:
            return 'D'
        if WIDTH//2-22 <= x <= WIDTH//2+22 and HEIGHT//2-30 <= y <= HEIGHT//2+30:
            return 'D_Bridge'
        return 'None'
    
    def attack_player(self,player_1,player_2):
        p1_x,p1_y = player_1.pos
        p2_x,p2_y = player_2.pos
        angle = math.atan2(p2_y-p1_y,p2_x-p1_x)
        vx,vy = math.cos(angle),math.sin(angle)
        player_2.move(vx,vy)
        t = Timer(0.08,lambda : player_2.accelerate(0,0))
        t.start()

        helper.play_sound(f"./assets/sounds/fight{random.randint(1,3)}.wav")

    def check_path_travelled(self, sub, prev_area):
        return all(item in prev_area for item in sub)
    
    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            frame.fill(self.bg_color)
            
            # wall blocks
            for wall_block in self.wall_blocks:
                wall_block.render(frame)

            # detect wall/player collision
            adj_block = self.player_offender.detect_nearest_block(self.wall_blocks)
            if adj_block and self.player_offender.detect_block_contact(adj_block):
                self.player_offender.contact_block(adj_block)
            
            adj_block = self.player_defender.detect_nearest_block(self.wall_blocks)
            if adj_block and self.player_defender.detect_block_contact(adj_block):
                self.player_defender.contact_block(adj_block)

            # OFFENDER
            if self.player_offender.area is not None:
                if (self.get_player_area(self.player_offender)!=self.player_offender.area) and \
                    self.player_offender.area != "None":
                    self.player_offender.crossed_areas.append(self.player_offender.area)

                    self.player_offender.last_area = self.player_offender.area
                    # self.player_defender.last_area = self.player_defender.area

            self.player_offender.area = self.get_player_area(self.player_offender)

            if self.player_offender.perm_hopping_disabled:
                self.player_offender.is_hopping = False
            else:
                if self.player_offender.area == "D" or \
                    self.player_offender.area == "None":
                    self.player_offender.is_hopping = True
                else:
                    self.player_offender.is_hopping = False
            # offender lose
            if self.player_offender.last_area not in ["B","D_Bridge"] and self.player_offender.area=="D" or \
                self.player_offender.last_area=="A" and self.player_offender.area=="C" or\
                self.player_offender.last_area=="D" and self.player_offender.area=="None":
                self.toggle_game_state(2)
            else:
                # offender win
                if self.player_offender.last_area=="D" and self.player_offender.area=="C":
                    self.toggle_game_state(1)

            # DEFENDER

            if self.player_defender.area is not None:
                if (self.get_player_area(self.player_defender)!=self.player_defender.area) and \
                    self.player_defender.area != "None":
                    self.player_defender.crossed_areas.append(self.player_defender.area)

                    self.player_defender.last_area = self.player_defender.area
            
            self.player_defender.area = self.get_player_area(self.player_defender)

            if self.player_defender.area in ["D","D_Bridge","F1","F2"]:
                self.player_defender.is_hopping = False
            else:
                self.player_defender.is_hopping = True
            if self.player_defender.area in ["None","A","C"] and self.player_defender.last_area != "B":
                self.toggle_game_state(1)
        
            # helper.render_text(frame, f"{str(self.player_offender.last_area)},{str(self.player_offender.area)} {str(self.player_defender.last_area)},{str(self.player_defender.area)}", 100, 100, color=Color.WHITE, font_size=20)

            if self.labels_shown:
                labels = [
                    ("A", self.circle_A.pos,(-20,0)),
                    ("B", self.circle_B.pos,(-20,0)),
                    ("B", self.circle_B.pos,(20,0)),
                    ("C", self.circle_A.pos,(30,0)),
                    ("D", (WIDTH//2+50,HEIGHT//2),(0,0)),
                    ("E", self.circle_E1.pos,(0,0)),
                    ("E", self.circle_E2.pos,(0,0)),
                    ("F", self.board_F1.pos,(self.board_F1.dim[0]/2,self.board_F1.dim[1]/2)),
                    ("F", self.board_F2.pos,(self.board_F2.dim[0]/2,self.board_F2.dim[1]/2)),
                ]
                for label, (x, y), (tx,ty) in labels:
                    helper.render_text(frame, label, x + tx, y + ty, font_size=32)


            # crossed bridges, then don't need to hop
            if self.check_path_travelled(["E1","F1","D_Bridge","F2","E2"],self.player_offender.crossed_areas):
                self.player_offender.perm_hopping_disabled = True
            # helper.render_text(frame, f"{str(self.player_offender.crossed_areas)}", 100, 50, color=Color.WHITE, font_size=20)
            # squid layout
            pg.draw.circle(frame,Color.WHITE,(WIDTH//2-300,HEIGHT//2),50,width=5)
            pg.draw.circle(frame,Color.WHITE,(WIDTH//2+300,HEIGHT//2),50,width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-300,HEIGHT//2),(WIDTH//2-20,HEIGHT//10),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-300,HEIGHT//2),(WIDTH//2-20,9*HEIGHT//10),width=5)
            pg.draw.circle(frame,Color.WHITE,(WIDTH//2,HEIGHT//10),22,width=5)
            pg.draw.circle(frame,Color.WHITE,(WIDTH//2,9*HEIGHT//10),22,width=5)
            
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-20,HEIGHT//10),(WIDTH//2-20,HEIGHT//2-30),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-20,9*HEIGHT//10),(WIDTH//2-20,HEIGHT//2+30),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-22,HEIGHT//2-30),(WIDTH//2+22,HEIGHT//2-30),width=5)

            pg.draw.line(frame,Color.WHITE,(WIDTH//2+20,HEIGHT//10),(WIDTH//2+20,HEIGHT//2-30),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2+20,9*HEIGHT//10),(WIDTH//2+20,HEIGHT//2+30),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2-22,HEIGHT//2+30),(WIDTH//2+22,HEIGHT//2+30),width=5)

            pg.draw.line(frame,Color.WHITE,(WIDTH//2+20,HEIGHT//10),(WIDTH//2+300,HEIGHT//10),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2+300,HEIGHT//10),(WIDTH//2+300,9*HEIGHT//10),width=5)
            pg.draw.line(frame,Color.WHITE,(WIDTH//2+20,9*HEIGHT//10),(WIDTH//2+300,9*HEIGHT//10),width=5)

            a1_x,a1_y = self.player_offender.acc
            a1_y = -0.5 if self.keys_held[pg.K_w] else 0.5 if self.keys_held[pg.K_s] else 0
            a1_x = -0.5 if self.keys_held[pg.K_a] else 0.5 if self.keys_held[pg.K_d] else 0
            magnitude = math.hypot(a1_x,a1_y)
            if magnitude>0:
                a1_y /= magnitude
                a1_x /= magnitude
            
            a2_x,a2_y = self.player_defender.acc
            a2_y = -0.5 if self.keys_held[pg.K_i] else 0.5 if self.keys_held[pg.K_k] else 0
            a2_x = -0.5 if self.keys_held[pg.K_j] else 0.5 if self.keys_held[pg.K_l] else 0
            magnitude = math.hypot(a2_x,a2_y)
            if magnitude>0:
                a2_y /= magnitude
                a2_x /= magnitude

            # attack player(s)
            if self.player_offender.get_other_circle_dist(self.player_defender)<=30:
                if self.keys_held[pg.K_f]:
                    self.attack_player(self.player_offender,self.player_defender)
                if self.keys_held[pg.K_SEMICOLON]:
                    self.attack_player(self.player_defender,self.player_offender)

            if self.player_offender.is_hopping:
                if self.in_game_frame_count >= self.next_hopping_cooldown:
                    self.player_offender.accelerate(a1_x,a1_y)
                else:
                    self.player_offender.accelerate(0, 0)
            else:
                self.player_offender.accelerate(a1_x, a1_y)

            if self.player_defender.is_hopping:
                if self.in_game_frame_count >= self.next_hopping_cooldown:
                    self.player_defender.accelerate(a2_x,a2_y)
                else:
                    self.player_defender.accelerate(0, 0)
            else:
                self.player_defender.accelerate(a2_x, a2_y)

            self.player_offender.render(frame)
            self.player_defender.render(frame)

            self.toggle_labels.render(frame)

            if self.next_hopping_cooldown==self.in_game_frame_count:
                self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown

            if self.next_attack_cooldown==self.in_game_frame_count:
                self.next_attack_cooldown = self.in_game_frame_count + self.attack_cooldown

            # self.render_timer(10,10,frame,self.time_left)


            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            else:
                self.time_left-=1

            # game over:
            if self.time_left<=0:
                self.toggle_game_state(2)

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

    def keydown_listener(self,key):
        if key in self.keys_held:
            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if not in_preparation:
                self.keys_held[key] = True
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
        if key in self.keys_held:
            self.keys_held[key] = False
    
    def mousedown_listener(self,event,mouse_x,mouse_y):
        pass

    def restart_game(self):
        self.in_game_frame_count = 0
        self.game_state = -1
        self.help_page = 0

        self.time_left = self.time * 60
        self.preparation_time = 5

        self.wall_blocks = [
            Block(0,0,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(0,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            Block(0,HEIGHT-self.wall_thickness,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(WIDTH-self.wall_thickness,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
        ]

        distinct_nums = random.sample(range(0,501),2)

        self.player_offender = Player(90,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=distinct_nums[0])
        self.player_offender.is_hopping = True
        self.player_offender.perm_hopping_disabled = False
        self.player_offender.crossed_areas = []
        self.player_offender.area = None
        self.player_offender.last_area = "A"
        self.player_defender = Player(WIDTH//2,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=distinct_nums[1])
        self.player_defender.is_hopping = False
        self.player_defender.crossed_areas = []
        self.player_defender.area = None
        self.player_defender.perm_hopping_disabled = False
        self.player_defender.state = "waiting"
        self.player_defender.last_area = "D"

        self.hopping_cooldown = 25
        self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown

        self.help_back_btn.visible = True
        self.help_start_btn.visible = True
        self.help_next_btn.visible = True
        self.help_prev_btn.visible = True

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False
        self.toggle_labels.visible = False
    
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
            self.toggle_labels.visible = True
        elif state==-1:
            self.paused = True
            self.return_lvls_btn.visible = False
    
    def render_help(self,frame):
        pg.draw.rect(frame, Color.SQUID_GREY, (0, 0, WIDTH, HEIGHT))
        if self.help_page == 0:
            helper.render_text(frame, "How to Play: Squid Game (Final Game):", WIDTH // 2, 50, font_size=28, color=Color.WHITE,underline=True)
            helper.render_text(frame, "Starting Positions:", WIDTH // 2, 100, font_size=25, color=Color.WHITE)
            # helper.render_text(frame, "Offender: Reach the head.\nDefender: Stop the Offender.", WIDTH // 2, HEIGHT // 1.1, font_size=22, color=Color.WHITE)
            helper.render_image(frame, "./assets/img/squidgame/layout_letters_labels.png", WIDTH // 2, HEIGHT // 1.85, [int(400/1.5), int(300/1.5)])

        elif self.help_page == 1:
            helper.render_text(frame, "Squid Layout Explained:", WIDTH // 2, 50, font_size=28, color=Color.WHITE,underline=True)
            helper.render_image(frame, "./assets/img/squidgame/layout_letters.png", WIDTH // 2, HEIGHT // 3 + 10, [int(400/2.25), int(300/2.25)])
            labels = ["A","B","C","D","E","F","Promotion Zone"]
            descriptions = [
                "Start Zone (Offender only)",
                "Defender Forbidden Zone",
                "Squid Head - Offender wins by reaching here",
                "Main Squid Body (Offender must enter to win)",
                "Checkpoint circles to cross the bridge",
                "Bridges - hopping required unless checkpoints crossed",
                "Allows Offender to run freely outside after crossing"
            ]

            for i, (label, desc) in enumerate(zip(labels, descriptions)):
                y_pos = HEIGHT // 1.65 + i * 25
                helper.render_text(frame, f"{label}:", WIDTH // 3, y_pos, font_size=20, color=Color.SKY_BLUE,align="right")
                helper.render_text(frame, desc, WIDTH // 2.9, y_pos, font_size=18, color=Color.WHITE,align="left")

        elif self.help_page == 2:
            helper.render_text(frame, "Controls:", WIDTH // 2, 50, font_size=28, color=Color.WHITE,underline=True)

            helper.render_text(frame,"Offender:",WIDTH//5,HEIGHT//4,font_size=24,align="left",underline=True)

            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//5,HEIGHT//2-50,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//5-50,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//5,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//5+50,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//5+100,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.BLACK,(WIDTH//5,HEIGHT//2-50,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//5-50,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//5,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//5+50,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//5+100,HEIGHT//2,50,50),width=3)

            helper.render_text(frame,"Attack",WIDTH//5+125,HEIGHT//2+100,font_size=18)
            pg.draw.line(frame,Color.WHITE,(WIDTH//5+125,HEIGHT//2+50),(WIDTH//5+125,HEIGHT//2+90),width=3)

            helper.render_text(frame,"Move Buttons",WIDTH//5,HEIGHT//2-80,font_size=18)
            pg.draw.rect(frame,Color.WHITE,(WIDTH//5-60,HEIGHT//2-60,170,120),width=3)

            helper.render_text(frame,"W",WIDTH//5+25,HEIGHT//2-25)
            helper.render_text(frame,"A",WIDTH//5-25,HEIGHT//2+25)
            helper.render_text(frame,"S",WIDTH//5+25,HEIGHT//2+25)
            helper.render_text(frame,"D",WIDTH//5+75,HEIGHT//2+25)
            helper.render_text(frame,"F",WIDTH//5+125,HEIGHT//2+25)

            helper.render_text(frame,"Defender:",2*WIDTH//3,HEIGHT//4,font_size=24,align="left",underline=True)

            pg.draw.rect(frame,Color.DARK_GREY,(2*WIDTH//3,HEIGHT//2-50,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(2*WIDTH//3-50,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(2*WIDTH//3,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(2*WIDTH//3+50,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(2*WIDTH//3+100,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.BLACK,(2*WIDTH//3,HEIGHT//2-50,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(2*WIDTH//3-50,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(2*WIDTH//3,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(2*WIDTH//3+50,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(2*WIDTH//3+100,HEIGHT//2,50,50),width=3)

            helper.render_text(frame,"Move Buttons",2*WIDTH//3,HEIGHT//2-80,font_size=18)
            pg.draw.rect(frame,Color.WHITE,(2*WIDTH//3-60,HEIGHT//2-60,170,120),width=3)

            helper.render_text(frame,"Attack",2*WIDTH//3+125,HEIGHT//2+100,font_size=18)
            pg.draw.line(frame,Color.WHITE,(2*WIDTH//3+125,HEIGHT//2+50),(2*WIDTH//3+125,HEIGHT//2+90),width=3)

            helper.render_text(frame,"I",2*WIDTH//3+25,HEIGHT//2-25)
            helper.render_text(frame,"J",2*WIDTH//3-25,HEIGHT//2+25)
            helper.render_text(frame,"K",2*WIDTH//3+25,HEIGHT//2+25)
            helper.render_text(frame,"L",2*WIDTH//3+75,HEIGHT//2+25)
            helper.render_text(frame,";",2*WIDTH//3+125,HEIGHT//2+25)

        elif self.help_page == 3:
            helper.render_image(frame, "./assets/img/squidgame/layout_letters_win.png", WIDTH // 3.33, HEIGHT // 2.25, [int(400/1.75), int(300/1.75)])
            helper.render_text(frame, "Win Conditions", WIDTH // 2, 50, font_size=28, color=Color.WHITE,underline=True)
            helper.render_text(frame, "Offender Wins:", WIDTH // 1.275, HEIGHT // 3-45, font_size=20, color=Color.WHITE,underline=True)
            helper.render_text(frame, "- Reaches C from D\n - Defender enters invalid area", WIDTH // 1.275, HEIGHT // 3, font_size=20, color=Color.WHITE)
            helper.render_text(frame, "Defender Wins:", WIDTH // 1.275, HEIGHT // 1.8-60, font_size=20, color=Color.WHITE,underline=True)
            helper.render_text(frame, "- Offender enters D \nwithout crossing bridges\n - Offender exits or violates rules", WIDTH // 1.275, HEIGHT // 1.8, font_size=20, color=Color.WHITE)

        # Navigation Buttons
        if self.help_page < 3: self.help_next_btn.render(frame)
        if self.help_page > 0: self.help_prev_btn.render(frame)

        self.help_back_btn.render(frame)
        if self.help_page == 3:
            self.help_start_btn.render(frame)
            self.help_start_btn.function = lambda: self.toggle_game_state( 0)

    def render_fail(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Defender Wins!",WIDTH/2,HEIGHT/3,font_size=40)
        self.return_lvls_btn.render(frame)
    def render_success(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Offender Wins!",WIDTH/2,HEIGHT/3,font_size=40)
        self.return_lvls_btn.render(frame)
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)