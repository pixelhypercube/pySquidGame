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
import numpy as np

helper = Helper()

class RedLightGreenLight(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.help_page = 0
        
        self.players = []
        self.time_left = time_left*60
        self.start_y = start_y
        self.finish_y = finish_y
        self.player_size = player_size
        self.wall_thickness = wall_thickness
        self.player = Player(WIDTH/2, HEIGHT/1.1, self.player_size, Color.SQUID_LIGHT_TEAL, max_speed=0.5, stroke_color=Color.DARK_RED,stroke_thickness=3,friction=0.05)
        self.gen_players(50)

        # assets
        self.assets = {
            "doll_front": "assets/img/rlgl/dollFront.png",
            "doll_back": "assets/img/rlgl/dollBack.png",
        }
        self.jitter_counter = 0
        self.eliminated_players = set()

        self.red_green_interval = 4.8
        self.scan_duration_time = 0.7
        self.interval_duration_left = self.red_green_interval * 60
        self.is_red_light = False

        self.start_block = Block(0, start_y, WIDTH, 5, Color.RED)

        self.wall_blocks = [
            Block(0,0,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(0,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            Block(0,HEIGHT-self.wall_thickness,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(WIDTH-self.wall_thickness,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            self.start_block
        ]

        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.05,60,20,content="Start")
        self.help_back_btn = Button(70, HEIGHT / 5, 50, 25, content="Back\nto Levels", next_screen="levels")

        self.max_shot_vel = 0.06
        self.red_light_cooldown = 1 # seconds
        self.cooldown_time = 0

        # fail/success screen
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        
        self.help_next_btn = Button(WIDTH - 80, HEIGHT - 40, 60, 25, content="Next",function=lambda: setattr(self, "help_page", self.help_page + 1 if self.help_page < 3 else 3))
        self.help_prev_btn = Button(80, HEIGHT - 40, 60, 25, content="Back",function=lambda: setattr(self, "help_page", self.help_page - 1 if self.help_page > 0 else 0))

        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn,self.help_next_btn,self.help_prev_btn
        ]


    def restart_game(self):
        self.players = []
        self.jitter_counter = 0
        self.eliminated_players = set()
        self.in_game_frame_count = 0
        self.time_left = self.time * 60
        self.preparation_time = 5
        self.is_red_light = False
        self.interval_duration_left = self.red_green_interval * 60
        self.players.clear()
        self.gen_players(25)
        self.player.set_pos(WIDTH/2, HEIGHT/1.1)
        self.wall_blocks = [
            Block(0,0,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(0,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            Block(0,HEIGHT-self.wall_thickness,WIDTH,self.wall_thickness,Color.SKY_BLUE),
            Block(WIDTH-self.wall_thickness,0,self.wall_thickness,HEIGHT,Color.SKY_BLUE),
            self.start_block
        ]
        self.paused = True
        self.game_state = -1 # help screen
        self.help_back_btn.visible = True
        self.help_start_btn.visible = True
        self.help_prev_btn.visible = True
        self.help_next_btn.visible = True

        self.help_page = 0
        
        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False
        self.cooldown_time = 0
        pg.mixer.music.stop()

    def toggle_paused(self):
        self.paused = not self.paused

        if self.paused:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()

        self.restart_btn.visible = self.paused
        self.exit_btn.visible = self.paused

    def gen_players(self, num_players):
        random_list = random.sample(range(1,501),num_players)
        player_index = random.randint(0,num_players-2)
        np.random.shuffle(random_list)

        placed_positions = []
        
        def is_valid_position(x, y):
            for px, py in placed_positions:
                if math.hypot(x - px, y - py) < self.player_size * 2:
                    return False
            return True

        for i in range(num_players):
            
            for _ in range(100):  # max 100 attempts to prevent infinite loop
                x = random.randint(self.player_size+self.wall_thickness*2, WIDTH-self.player_size-self.wall_thickness*2)
                y = random.randint(self.start_y+self.wall_thickness*2, HEIGHT-self.player_size-self.wall_thickness*2)
                if is_valid_position(x, y):
                    break
            else:
                x = random.randint(self.player_size+self.wall_thickness*2, WIDTH-self.player_size-self.wall_thickness*2)
                y = random.randint(self.start_y+self.wall_thickness*2, HEIGHT-self.player_size-self.wall_thickness*2)
            
            placed_positions.append((x, y))

            color = Color.get_random_color_from_base(Color.SQUID_TEAL)
            if i==player_index:
                self.player.num_label = random_list[i]
                self.players.append(self.player)
                self.player.set_pos(x,y)
            else: self.players.append(Player(x, y, self.player_size, color, max_speed=0.5, stroke_color=Color.BLACK,num_label=random_list[i],friction=0.05))

    def toggle_light(self):
        self.is_red_light = not self.is_red_light

        self.interval_duration_left = self.red_green_interval*60
        if not self.is_red_light:
            helper.play_music("./assets/sounds/greenLight.wav")
            self.cooldown_time = 0
        else:
            helper.play_music("./assets/sounds/changeLight.wav")
            t = Timer(0.5,lambda : helper.play_music("./assets/sounds/scanning.wav"))
            t.start()

    def keydown_listener(self, key):
        if key == pg.K_w:
            self.player.accelerate(self.player.acc[0], -1)  # Move up
        elif key == pg.K_s:
            self.player.accelerate(self.player.acc[0], 1)  # Move down
        elif key == pg.K_a:
            self.player.accelerate(-1, self.player.acc[1])  # Move left
        elif key == pg.K_d:
            self.player.accelerate(1, self.player.acc[1])  # Move right
        elif key == pg.K_SPACE:
            self.player.boost()
        elif key == pg.K_ESCAPE or key == pg.K_p:
            if self.game_state == 0:
                self.toggle_paused()
    
    def keyup_listener(self, key):
        if key == pg.K_w or key == pg.K_s:
            self.player.accelerate(self.player.acc[0], 0)
        elif key == pg.K_a or key == pg.K_d:
            self.player.accelerate(0,self.player.acc[1])
    
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)

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
    
    def attack_player(self,player_1,player_2):
        if self.is_red_light or (self.preparation_time * 60 - self.in_game_frame_count > 0):
            if (player_1 == self.player or player_2 == self.player):
                self.toggle_game_state(2)
                helper.play_sound("./assets/sounds/gunShotLong.wav")
            else:
                self.players.remove(player_1)
                self.players.remove(player_2)


        p1_x,p1_y = player_1.pos
        p2_x,p2_y = player_2.pos
        angle = math.atan2(p2_y-p1_y,p2_x-p1_x)
        vx,vy = math.cos(angle)*10,math.sin(angle)*10
        player_2.move(vx,abs(vy)*3)
        t = Timer(0.08,lambda : player_2.accelerate(0,0))
        t.start()

        helper.play_sound(f"./assets/sounds/fight{random.randint(1,3)}.wav",volume=0.15)

    def mousedown_listener(self,event,mouse_x,mouse_y):
        in_preparation = self.preparation_time*60-self.in_game_frame_count>0
        if event.type==pg.MOUSEBUTTONDOWN:
            if not in_preparation:
                for player in self.players:
                    if player.contains(mouse_x,mouse_y):
                        if player.get_other_circle_dist(self.player)<=30:
                            self.attack_player(self.player,player)

    def render(self, frame, mouse_x, mouse_y):
        if not self.paused:
            frame.fill(self.bg_color)

            helper.render_image(
                frame,
                self.assets["doll_front"] if (self.is_red_light or (self.preparation_time * 60 - self.in_game_frame_count > 0)) else self.assets["doll_back"],
                WIDTH//2,
                50,
                size=(40,40)
            )  
            

            pg.draw.line(frame, Color.RED, (0, self.start_y), (WIDTH, self.start_y), 5)
            pg.draw.line(frame, Color.RED, (0, self.finish_y), (WIDTH, self.finish_y), 5)

            # STATIC ELEMENTS
            for wall_block in self.wall_blocks:
                if wall_block != self.start_block:
                    wall_block.render(frame)

            px,py = self.player.pos
            pg.draw.polygon(frame,Color.RED,[(px-self.player_size,py-self.player_size*2.5),(px+self.player_size,py-self.player_size*2.5),(px,py-self.player_size-7)])
            pg.draw.polygon(frame,Color.BLACK,[(px-self.player_size,py-self.player_size*2.5),(px+self.player_size,py-self.player_size*2.5),(px,py-self.player_size-7)],width=2)
            for player in self.players:
                player.render(frame)
            
            self.render_timer(10,10,frame,self.time_left)

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0

            # PLAYER COLLISION DETECTION
            nearest_player = self.player.detect_nearest_circle(self.players)
            if nearest_player and self.player.detect_circle_contact(nearest_player.pos):
                self.player.contact_circle(nearest_player)
            adj_block = self.player.detect_nearest_block(self.wall_blocks)
            if adj_block and self.player.detect_block_contact(adj_block):
                self.player.contact_block(adj_block)
        
            # OTHER PLAYERS COLLISION DETECTION
            eliminated_indices = []
            for i,player in enumerate(self.players):
                if player is self.player: continue

                # collision with walls
                adj_block = player.detect_nearest_block(self.wall_blocks)
                if adj_block and player.detect_block_contact(adj_block):
                    player.contact_block(adj_block)

                # collision with other players
                nearest_player = player.detect_nearest_circle(self.players)
                if nearest_player and player.detect_circle_contact(nearest_player.pos):
                    player.contact_circle(nearest_player)
                
                # move or freeze
                if in_preparation:
                    player.accelerate(0, 0)
                elif not self.is_red_light:
                    if player.pos[1]<=self.finish_y:
                        player.accelerate(0,0)
                    else:
                        dx = random.uniform(-0.1,0.1)
                        dy = -random.uniform(0.05,0.1)
                        player.accelerate(dx,dy)

                        if random.random()<0.05:
                            player.boost()
                        
                        if random.uniform(0,1)<0.005:
                            if player.get_other_circle_dist(nearest_player)<=30:
                                self.attack_player(player,nearest_player)
                else:
                    player.accelerate(0, 0)

                    if self.jitter_counter%5 == 0 and player.pos[1] > self.finish_y:
                        dx = random.uniform(-0.1,0.1)
                        dy = random.uniform(-0.1,0.1)
                        player.accelerate(dx,dy)

                    if self.cooldown_time > self.red_light_cooldown*60 and player.get_scalar_vel() > self.max_shot_vel:
                        if i not in self.eliminated_players:
                            eliminated_indices.append(i)
                            self.eliminated_players.add(i)
                            helper.play_sound("./assets/sounds/gunShot.wav",volume=1)
            
            for index in sorted(eliminated_indices,reverse=True): del self.players[index]

            # game state transitions

            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            elif (self.preparation_time*60-self.in_game_frame_count==0):
                if self.start_block in self.wall_blocks:
                    self.wall_blocks.remove(self.start_block)
                helper.play_music("./assets/sounds/greenLight.wav")
            else:

                if self.player.pos[1] <= self.finish_y and not self.is_red_light:
                    self.toggle_game_state(1)
                elif self.cooldown_time > self.red_light_cooldown*60 and self.player.get_scalar_vel()>self.max_shot_vel:
                    helper.play_sound("./assets/sounds/gunShotLong.wav")
                    self.toggle_game_state(2)
                
                self.time_left-=1
                if self.interval_duration_left<=0: self.toggle_light()
                self.interval_duration_left -= 1

                if self.is_red_light: self.cooldown_time += 1
                if self.time_left<=0: self.toggle_game_state(2)


            helper.render_text(frame,"Press 'Esc' or 'P' to pause",WIDTH-20,HEIGHT-20,font_size=18,color=Color.BLACK,align="right")

            self.in_game_frame_count += 1
            self.jitter_counter += 1
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
        helper.render_text(frame," by clicking the 'Back to Levels' button! :)",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_success(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Success!",WIDTH/2,HEIGHT/3,font_size=40)
        self.return_lvls_btn.render(frame)
    def render_help(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        if self.help_page==0:
            helper.render_text(frame,"How to play: Red Light, Green Light",WIDTH/2,HEIGHT/12,font_size=40,underline=True)
            helper.render_text(frame,"Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/6.25,font_size=20)
            helper.render_image(frame,"./assets/img/rlgl/demoWithLabels.png",WIDTH/2,HEIGHT/1.9,[int(500/1.85),int(375/1.85)])
        elif self.help_page==1:
            helper.render_text(frame,"Controls:",WIDTH/2,HEIGHT/12,font_size=28,underline=True)

            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3,HEIGHT//2-50,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3-50,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3+50,HEIGHT//2,50,50))
            # pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3+100,HEIGHT//2,50,50))
            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//3.5,HEIGHT//1.35,350,50))
            pg.draw.rect(frame,Color.BLACK,(WIDTH//3,HEIGHT//2-50,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//3-50,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//3,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//3+50,HEIGHT//2,50,50),width=3)
            # pg.draw.rect(frame,Color.BLACK,(WIDTH//3+100,HEIGHT//2,50,50),width=3)
            pg.draw.rect(frame,Color.BLACK,(WIDTH//3.5,HEIGHT//1.35,350,50),width=3)

            pg.draw.rect(frame,Color.DARK_GREY,(WIDTH//1.5,HEIGHT//3,100,180))
            pg.draw.rect(frame,Color.BLACK,(WIDTH//1.5,HEIGHT//3,100,180),width=3)
            pg.draw.line(frame,Color.BLACK,(WIDTH//1.5+50,HEIGHT//3),(WIDTH//1.5+50,HEIGHT//3+80),width=3)
            pg.draw.line(frame,Color.BLACK,(WIDTH//1.5,HEIGHT//3+80),(WIDTH//1.5+100,HEIGHT//3+80),width=3)
            pg.draw.rect(frame,(200,200,200),(WIDTH//1.5+40,HEIGHT//3+20,20,40))

            helper.render_text(frame,"Attack",WIDTH//1.5-50,HEIGHT//3-50,font_size=18)
            pg.draw.line(frame,Color.WHITE,(WIDTH//1.5-5,HEIGHT//3-5),(WIDTH//1.5-40,HEIGHT//3-40),width=3)
            pg.draw.rect(frame,Color.WHITE,(WIDTH//1.5-5,HEIGHT//3-5,60,100),width=3)

            helper.render_text(frame,"Move Buttons",WIDTH//3,HEIGHT//2-80,font_size=18)
            pg.draw.rect(frame,Color.WHITE,(WIDTH//3-60,HEIGHT//2-60,170,120),width=3)

            helper.render_text(frame,"W",WIDTH//3+25,HEIGHT//2-25)
            helper.render_text(frame,"A",WIDTH//3-25,HEIGHT//2+25)
            helper.render_text(frame,"S",WIDTH//3+25,HEIGHT//2+25)
            helper.render_text(frame,"D",WIDTH//3+75,HEIGHT//2+25)
            # helper.render_text(frame,"F",WIDTH//3+125,HEIGHT//2+25)
            helper.render_text(frame,"Space",WIDTH//3.5+175,HEIGHT//1.35+25)

            helper.render_text(frame,"Speed Boost",WIDTH//3.5+175,HEIGHT//1.35+90,font_size=18)
            pg.draw.line(frame,Color.WHITE,(WIDTH//3.5+175,HEIGHT//1.35+50),(WIDTH//3.5+175,HEIGHT//1.35+75),width=3)
        elif self.help_page==2:
            helper.render_text(frame,"More Tips:",WIDTH/2,HEIGHT/12,font_size=28,underline=True)

            helper.render_image(frame,"./assets/img/rlgl/demoTips.png",WIDTH/2,HEIGHT/2.5,[int(500/2.25),int(375/2.25)])

            rules = [
                ("1.","The game ends when time runs out or you reach the goal."),
                ("2.","Click on a nearby player to attack, but they can push back."),
                ("3.","Last-minute movement when the doll is facing you may"),
                ("","still get you caught, and that includes attacking players!")
            ]
            base_y = HEIGHT//1.4
            for i,(pt,rule) in enumerate(rules):
                spacing = i*30
                helper.render_text(frame,pt, WIDTH/10, base_y+spacing, font_size=20,align="left")
                helper.render_text(frame,rule, WIDTH/10+30, base_y+spacing, font_size=20,align="left")
        # helper.render_text(frame,"When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.4,font_size=20)
        # helper.render_text(frame,"Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.33,font_size=20)
        # helper.render_text(frame,"Use the WASD keys to move",WIDTH/2,HEIGHT/1.25,font_size=20)
        # helper.render_text(frame,"Repeatedly press SPACE if you want to boost your speed!",WIDTH/2,HEIGHT/1.15,font_size=20)
        
        self.help_start_btn.visible = self.help_page==2
        self.help_prev_btn.visible = self.help_page>0
        self.help_next_btn.visible = self.help_page<2

        self.help_back_btn.render(frame)
        self.help_prev_btn.render(frame)
        self.help_next_btn.render(frame)
        self.help_start_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(0) 