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
    def __init__(self, time=60, preparation_time=5, bg_color=Color.STONE,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.33,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        self.player_1 = Player(90,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=random.randint(0,500))
        self.player_1.is_hopping = True
        self.player_1.perm_hopping_disabled = False
        self.player_1.crossed_areas = []
        self.player_1.area = None
        self.player_1.last_area = "A" # prev state area
        self.player_2 = Player(WIDTH//2,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=random.randint(0,500))
        self.player_2.is_hopping = False
        self.player_2.crossed_areas = []
        self.player_2.area = None
        self.player_2.perm_hopping_disabled = False
        self.player_2.state = "waiting"
        self.player_2.last_area = "D" # prev state area
        # self.glasses_state = [random.randint(0,1) for _ in range(18)]
        self.game_state = -1

        self.hopping_cooldown = 25
        self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown
        self.attack_cooldown = 20
        self.next_attack_cooldown = self.in_game_frame_count + self.attack_cooldown

        self.keys_held = {
            pg.K_w:False,
            pg.K_a:False,
            pg.K_s:False,
            pg.K_d:False
        }


        # SQUID LAYOUT AREAS
        self.circle_A = Circle(WIDTH//2-300,HEIGHT//2,50,Color.WHITE) # A and C
        self.circle_B = Circle(WIDTH//2+300,HEIGHT//2,50,Color.WHITE) # B

        self.circle_E1 = Circle(WIDTH//2,HEIGHT//10,22,Color.WHITE) # E1
        self.circle_E2 = Circle(WIDTH//2,9*HEIGHT//10,22,Color.WHITE) # E2

        self.board_F1 = Block(WIDTH//2-20,HEIGHT//10,44,HEIGHT//2-30-HEIGHT//10,Color.WHITE)
        self.board_F2 = Block(WIDTH//2-20,HEIGHT//2+30,44,HEIGHT//2-30-HEIGHT//10,Color.WHITE)

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

    def follow_player(self,player_1,player_2):
        p1_x,p1_y = player_1.pos
        p2_x,p2_y = player_2.pos
        angle = math.atan2(p2_y-p1_y,p2_x-p1_x)
        vx,vy = math.cos(angle),math.sin(angle)
        if player_2.is_hopping:
            if self.in_game_frame_count >= self.next_hopping_cooldown:
                self.player_2.accelerate(-vx,-vy)
            else:
                self.player_2.accelerate(0, 0)
        else:
            player_2.move(-vx*0.5,-vy*0.5)

    # player_1 - attacker, player_2 - attacked player
    def attack_player(self,player_1,player_2):
        p1_x,p1_y = player_1.pos
        p2_x,p2_y = player_2.pos
        angle = math.atan2(p2_y-p1_y,p2_x-p1_x)
        vx,vy = math.cos(angle),math.sin(angle)
        player_2.move(vx,vy)
        t = Timer(0.08,lambda : player_2.accelerate(0,0))
        t.start()

    def check_path_travelled(self, sub, prev_area):
        return all(item in prev_area for item in sub)

    # for player_2
    def defender_move(self,player_1,player_2):
        p1_x,p1_y = player_1.pos
        p2_x,p2_y = player_2.pos
        player_1_area = player_1.area
        player_2_area = player_2.area

        # # triangle vertices
        # C = (WIDTH//2 - 300, HEIGHT//2)
        # E1 = (WIDTH//2 - 20, HEIGHT//10)
        # E2 = (WIDTH//2 - 20, 9 * HEIGHT//10)

        bx,by = self.circle_B.pos

        angle = math.atan2(p2_y-p1_y,p2_x-p1_x)
        vx = math.cos(angle)
        vy = math.sin(angle)
        if player_1_area=="None":
            if player_2_area in ["D","D_Bridge","E1","E2","F1","F2"]:
                # self.follow_player(player_1,player_2)
                angle = math.atan2(p2_y-by,p2_x-bx)
                vx = 0.5*math.cos(angle)
                vy = 0.5*math.sin(angle)
                player_2.move(-vx,-vy)
            elif player_2_area=="B":
                player_2.move(0.5,0)
            elif player_2_area=="None":
                if p2_x>WIDTH//2+300:
                    if HEIGHT//10-40 < p2_y < 9*HEIGHT//1+40:
                        if self.in_game_frame_count==self.next_hopping_cooldown:
                            if p1_x<WIDTH//2+300:
                                if p1_y>HEIGHT//2: player_2.move(0,1)
                                else: player_2.move(0,-1)
                            else:
                                player_2.move(-vx,-vy)
                    else:
                        player_2.move(-vx,-vy)
                else:
                    if self.in_game_frame_count==self.next_hopping_cooldown:
                        player_2.move(-vx,0 if p2_x>WIDTH//2 else -vy)
        elif player_1_area in ["B","D"]:
            if p2_x>WIDTH//2+300:
                if player_2_area!="None" or self.in_game_frame_count==self.next_hopping_cooldown:
                    if by-50 <= p2_y <= by+50:
                        player_2.move(-0.5*vx,-0.5*vy)
                    else:
                        if p1_y>p2_y: player_2.move(0,1)
                        else: player_2.move(0,-1)
            else:
                if player_2_area in ["B","D","D_Bridge"]:
                    player_2.move(-0.5*vx,-0.5*vy)

            


    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            frame.fill(self.bg_color)
            
            # PLAYER 1
            if self.player_1.area is not None:
                if (self.get_player_area(self.player_1)!=self.player_1.area) and \
                    self.player_1.area != "None":
                    self.player_1.crossed_areas.append(self.player_1.area)

                    self.player_1.last_area = self.player_1.area
                    self.player_2.last_area = self.player_2.area

            self.player_1.area = self.get_player_area(self.player_1)
            self.player_2.area = self.get_player_area(self.player_2)

            if self.player_1.perm_hopping_disabled:
                self.player_1.is_hopping = False
            else:
                if self.player_1.area == "D" or \
                    self.player_1.area == "None":
                    self.player_1.is_hopping = True
                else:
                    self.player_1.is_hopping = False
            # lose
            if self.player_1.last_area not in ["B","D_Bridge"] and self.player_1.area=="D" or \
                self.player_1.last_area=="A" and self.player_1.area=="C" or\
                self.player_1.last_area=="D" and self.player_1.area=="None":
                self.toggle_game_state(frame,2)
            else:
                # win
                if self.player_1.last_area=="D" and self.player_1.area=="C":
                    self.toggle_game_state(frame,1)

            # PLAYER 2
            
            if self.player_2.area == "D" or self.player_2.area == "D_Bridge":
                self.player_2.is_hopping = False
            else:
                self.player_2.is_hopping = True

            # player 2 movement
            self.defender_move(self.player_1,self.player_2)

            # crossed bridges, then don't need to hop
            if self.check_path_travelled(["E1","F1","D_Bridge","F2","E2"],self.player_1.crossed_areas):
                self.player_1.perm_hopping_disabled = True
            helper.render_text(frame, f"{str(self.player_1.crossed_areas)}", 100, 50, color=Color.WHITE, font_size=20)
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

            ax,ay = self.player_1.acc
            ay = -1 if self.keys_held[pg.K_w] else 1 if self.keys_held[pg.K_s] else 0
            ax = -1 if self.keys_held[pg.K_a] else 1 if self.keys_held[pg.K_d] else 0
            magnitude = math.hypot(ax,ay)
            if magnitude>0:
                ay /= magnitude
                ax /= magnitude
            
            if self.player_1.is_hopping:
                if self.in_game_frame_count >= self.next_hopping_cooldown:
                    self.player_1.accelerate(ax,ay)
                else:
                    self.player_1.accelerate(0, 0)
            else:
                self.player_1.accelerate(ax, ay)

            self.player_1.render(frame)
            self.player_2.render(frame)

            if self.next_hopping_cooldown==self.in_game_frame_count:
                self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown

            if self.next_attack_cooldown==self.in_game_frame_count:
                if self.player_2.get_other_circle_dist(self.player_1)<25:
                    self.attack_player(self.player_2,self.player_1)
                self.next_attack_cooldown = self.in_game_frame_count + self.attack_cooldown

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
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.player_2.contains(mouse_x,mouse_y):
                if self.player_1.get_other_circle_dist(self.player_2)<=30:
                    self.attack_player(self.player_1,self.player_2)

    def restart_game(self):
        self.in_game_frame_count = 0
        self.game_state = -1

        self.player_1 = Player(90,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=random.randint(0,500))
        self.player_1.is_hopping = True
        self.player_1.perm_hopping_disabled = False
        self.player_1.crossed_areas = []
        self.player_1.area = None
        self.player_1.last_area = "A"
        self.player_2 = Player(WIDTH//2,HEIGHT//2,10,Color.BLACK,max_speed=5,friction=0.15,num_label=random.randint(0,500))
        self.player_2.is_hopping = False
        self.player_2.crossed_areas = []
        self.player_2.area = None
        self.player_2.perm_hopping_disabled = False
        self.player_2.state = "waiting"
        self.player_2.last_area = "D"

        self.hopping_cooldown = 25
        self.next_hopping_cooldown = self.in_game_frame_count + self.hopping_cooldown

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