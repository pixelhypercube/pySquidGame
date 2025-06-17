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

helper = Helper()

class RedLightGreenLight(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        self.player = Player(WIDTH/2, HEIGHT/1.1, 7, Color.SQUID_LIGHT_TEAL, max_speed=0.5, stroke_color=Color.SQUID_PINK,stroke_thickness=2)
        self.players = []
        self.time_left = time_left*60
        self.start_y = start_y
        self.finish_y = finish_y
        self.player_size = player_size
        self.wall_thickness = wall_thickness
        self.gen_players(100)

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
        
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.33,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")

        self.max_shot_vel = 0.06
        self.red_light_cooldown = 1 # seconds
        self.cooldown_time = 0

        # fail/success screen
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]


    def restart_game(self):
        self.in_game_frame_count = 0
        self.time_left = self.time * 60
        self.is_red_light = False
        self.interval_duration_left = self.red_green_interval * 60
        self.players.clear()
        self.gen_players(100)
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
        for _ in range(num_players):
            x = random.randint(self.player_size+self.wall_thickness*2, WIDTH-self.player_size-self.wall_thickness*2)
            y = random.randint(self.start_y+self.wall_thickness*2, HEIGHT-self.player_size-self.wall_thickness*2)
            color = Color.get_random_color_from_base(Color.SQUID_TEAL)
            self.players.append(Player(x, y, 7, color, max_speed=0.5, stroke_color=Color.BLACK))

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

    def render(self, frame, mouse_x, mouse_y):
        if not self.paused:
            frame.fill(self.bg_color)

            if self.is_red_light or (self.preparation_time*60-self.in_game_frame_count>0):
                helper.render_image(frame,"./assets/img/rlgl/dollFront.png",WIDTH/2,HEIGHT/12,[40,40])
            else:
                helper.render_image(frame,"./assets/img/rlgl/dollBack.png",WIDTH/2,HEIGHT/12,[40,40])

            # OBJECT RENDERING
            for wall_block in self.wall_blocks:
                wall_block.render(frame)

            for player in self.players:
                player.render(frame)
            
            self.player.render(frame)
            
            pg.draw.line(frame, Color.RED, (0, self.start_y), (WIDTH, self.start_y), 5)
            pg.draw.line(frame, Color.RED, (0, self.finish_y), (WIDTH, self.finish_y), 5)
            
            helper.render_text(frame,f"Time left: {self.time_left // 60}", WIDTH - 100, 20, font_size=20)

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0

            # PLAYER COLLISION DETECTION
            player1 = self.player.detect_nearest_circle(self.players)
            adj_block = self.player.detect_nearest_block(self.wall_blocks)
            if adj_block is not None:
                if self.player.detect_block_contact(adj_block):
                    self.player.contact_block(adj_block)
            if player1 is not None:
                if self.player.detect_circle_contact(player1.pos):
                    self.player.contact_circle(player1)
        
            # OTHER PLAYERS COLLISION DETECTION
            for player in self.players:
                adj_block = player.detect_nearest_block(self.wall_blocks)
                if adj_block is not None:
                    if player.detect_block_contact(adj_block):
                        player.contact_block(adj_block)
                player1 = player.detect_nearest_circle(self.players)
                if player1 is not None:
                    if player.detect_circle_contact(player1.pos):
                        player.contact_circle(player1)
                
                if in_preparation:
                    player.accelerate(0, 0)
                else:
                    if not self.is_red_light:
                        if player.pos[1]<=self.finish_y:
                            player.accelerate(0, 0)
                        else:
                            player.accelerate(random.random()*0.1-0.05,-random.random()*0.1)
                    else:
                        player.accelerate(0, 0)
            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            elif (self.preparation_time*60-self.in_game_frame_count==0):
                self.wall_blocks.remove(self.start_block)
                helper.play_music("./assets/sounds/greenLight.wav")
            else:
                # jitter players
                for player in self.players:
                    if player.pos[1] <= self.finish_y:
                        player.accelerate(0, 0)
                    else:
                        if self.is_red_light:
                            player.accelerate(random.random()*0.04-0.02,random.random()*0.04-0.02)
                            if self.cooldown_time>self.red_light_cooldown*60 and player.get_scalar_vel() > self.max_shot_vel:
                                del self.players[self.players.index(player)]
                                helper.play_sound("./assets/sounds/gunShot.wav")

                # win
                if (self.player.pos[1] <= self.finish_y and not self.is_red_light) or (self.time_left <= 0 and not self.is_red_light):
                    self.toggle_game_state(frame,1)
                # lose
                if self.cooldown_time>self.red_light_cooldown*60 and self.player.get_scalar_vel() > self.max_shot_vel:
                    helper.play_sound("./assets/sounds/gunShotLong.wav")
                    self.toggle_game_state(frame,2)

                self.time_left-=1
                if self.interval_duration_left<=0:
                    self.toggle_light()
                self.interval_duration_left-=1

                if self.is_red_light:
                    self.cooldown_time += 1

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
        helper.render_text(frame,"How to play:",WIDTH/2,HEIGHT/12,font_size=40)
        helper.render_text(frame,"Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,font_size=20)
        helper.render_image(frame,"./assets/img/rlgl/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
        helper.render_text(frame,"When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,font_size=20)
        helper.render_text(frame,"Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,font_size=20)
        helper.render_text(frame,"Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,font_size=20)
        helper.render_text(frame,"Repeatedly press SPACE if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,font_size=20)
        
        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(frame,0) 