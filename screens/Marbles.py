from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from objects.Block import Block
from screens.GameHandler import GameHandler
import pygame as pg
import math
import numpy as np
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from components.Button import Button
from objects.RadialForceArea import RadialForceArea
from objects.LinearForceArea import LinearForceArea
from objects.Marble import Marble
from noise import pnoise2

helper = Helper()

class Marbles(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10,wall_thickness=10):
        super().__init__(time, preparation_time, bg_color)
        # buttons
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.12,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back\nto Levels", next_screen="levels")

        # fail/success screen
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]

        self.marbles_left = 10
        self.marbles_left_marble = Marble(WIDTH-70,20,8,Color.SQUID_TEAL) # for display purposes

        # cooldown
        self.cooldown = 100
        self.cooldown_frame = -1

        # game state
        self.game_state = -1

        # objects

        self.marble_size = 4
        self.marbles = []
        self.hole = RadialForceArea(WIDTH//2-50,HEIGHT//2-260,100,100,stroke_thickness=3,force_strength=0.25)
        self.force_areas = [
            self.hole
        ]

        self.sand_heightmap = self.generate_sand_heightmap(WIDTH,HEIGHT)

        # self.sand_heightmap = np.zeros((WIDTH,HEIGHT),dtype=float)
        # for x in range(WIDTH):
        #     for y in range(HEIGHT):
        #         self.sand_heightmap[x][y] = 10 * math.sin(x*0.05) + 5 * math.cos(y*0.05)

        # boundaries
        self.shoot_y = HEIGHT-100

        self.time_left = time_left*60

        self.first_mouse_pos = (None,None)

        self.restart_btn.visible = False
        self.exit_btn.visible = False
        self.return_lvls_btn.visible = False

    def generate_sand_heightmap(self,width,height,scale=100.0,octaves=4,persistence=0.5,lacunarity=2.0):
        heightmap = np.zeros((width, height), dtype=float)
        for x in range(width):
            for y in range(height):
                nx = x/scale
                ny = y/scale
                noise_val = pnoise2(nx,ny,octaves=octaves,persistence=persistence,lacunarity=lacunarity,repeatx=width,repeaty=height,base=0)
                heightmap[x][y] = noise_val
        return heightmap

    def render_sand(self,frame):
        heightmap = self.sand_heightmap
        sand_surface = pg.Surface((WIDTH,HEIGHT))
        pixels = pg.surfarray.pixels3d(sand_surface)

        min_h = np.min(heightmap)
        max_h = np.max(heightmap)
        range_h = max_h-min_h if max_h - min_h != 0 else 1

        norm = ((heightmap - min_h) / range_h).clip(0, 1)

        sand_color = np.array(self.bg_color)
        dark_sand = (sand_color * 0.75).astype(np.uint8)

        r = (dark_sand[0] + norm * (sand_color[0] - dark_sand[0])).astype(np.uint8)
        g = (dark_sand[1] + norm * (sand_color[1] - dark_sand[1])).astype(np.uint8)
        b = (dark_sand[2] + norm * (sand_color[2] - dark_sand[2])).astype(np.uint8)


        pixels[:, :, 0] = r
        pixels[:, :, 1] = g
        pixels[:, :, 2] = b

        del pixels

        # Draw it
        frame.blit(sand_surface, (0, 0))

    def get_terrain_force(self,x,y):
        # indices clamping
        ix, iy = int(max(1, min(WIDTH-2, x))), int(max(1, min(HEIGHT-2, y)))

        dz_dx = (self.sand_heightmap[ix+1][iy] - self.sand_heightmap[ix-1][iy]) * 10
        dz_dy = (self.sand_heightmap[ix][iy+1] - self.sand_heightmap[ix][iy-1]) * 10

        max_force = 0.1
        fx, fy = -dz_dx, -dz_dy
        mag = math.hypot(fx, fy)
        if mag > max_force:
            fx *= max_force / mag
            fy *= max_force / mag

        return fx, fy

    def restart_game(self):
        self.game_state = -1
        self.marbles_left = 10
        self.player_marbles_in = 0
        self.computer_marbles_in = 0
        self.cooldown_frame = -1

        self.in_game_frame_count = 0
        self.time_left = self.time * 60
        self.preparation_time = 5

        self.marbles = []

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
        elif state==3:
            self.paused = True
            self.return_lvls_btn.visible = True
        elif state==-1:
            self.paused = True
            self.return_lvls_btn.visible = False
    
    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:

            frame.fill(self.bg_color)

            self.render_sand(frame)

            helper.render_text(frame,"Throw before the line!",120,self.shoot_y-20,font_size=20,color=Color.BLACK)
            pg.draw.line(frame,Color.RED,(0,self.shoot_y),(WIDTH,self.shoot_y),width=5)

            # cooldown
            if self.in_game_frame_count==self.cooldown_frame:
                self.shoot_marble_comp(
                    random.randint(WIDTH//2-75,WIDTH//2+75),
                    random.randint(self.shoot_y,self.shoot_y+50),
                )

            player_marbles_in = 0
            computer_marbles_in = 0

            marble_max_vel = 0

            for force_area in self.force_areas:
                force_area.render(frame)
            for marble in self.marbles:
                marble.render(frame)
                
                vx,vy = marble.vel
                mag = math.hypot(vx,vy)*0.1
                if mag>0.1:
                    helper.play_sound("./assets/sounds/marbleMoving.wav",volume=mag*2,continuous=True)

                fx,fy = self.get_terrain_force(*marble.pos)
                marble.vel[0] += fx
                marble.vel[1] += fy

                nearest_marble = marble.detect_nearest_circle(self.marbles)
                if nearest_marble is not None:
                    is_contact = marble.detect_circle_contact(nearest_marble.pos)
                    pair_id = id(nearest_marble)

                    if is_contact:
                        if pair_id not in marble.colliding_with:
                            vx,vy = marble.vel
                            mag = math.hypot(vx,vy)*0.1

                            helper.play_sound("./assets/sounds/marbleCollide.wav",volume=min(mag,1))
                            marble.colliding_with.add(pair_id)
                        marble.contact_circle(nearest_marble)
                    else:
                        marble.colliding_with.discard(pair_id)

                adj_force_area = marble.detect_nearest_block(self.force_areas)
                if adj_force_area is not None:
                    if marble.detect_block_contact(adj_force_area):
                        obj_name = type(adj_force_area).__name__

                        x,y = marble.pos
                        vx,vy = marble.vel
                        if obj_name=="RadialForceArea":
                            if marble.player_tag==1:
                                player_marbles_in+=1
                            elif marble.player_tag==2:
                                computer_marbles_in+=1

                            w,h = adj_force_area.dim
                            cx = adj_force_area.pos[0]+w//2
                            cy = adj_force_area.pos[1]+h//2
                            angle = math.atan2((cy-y),(cx-x))
                            force_strength = adj_force_area.force_strength
                            dx = math.cos(angle)*force_strength
                            dy = math.sin(angle)*force_strength
                            marble.vel = [vx+dx,vy+dy]
                        elif obj_name=="LinearForceArea":
                            if marble.detect_block_contact(adj_force_area):
                                angle = adj_force_area.direction
                                dx = math.cos(angle)
                                dy = math.sin(angle)
                                marble.vel = [vx+dx,vy+dy]
                    for i in range(len(marble.vel)):
                        if abs(marble.vel[i])<0.2:
                            marble.vel[i] = 0    
                marble_max_vel = max(marble_max_vel,marble.get_scalar_vel())
            if pg.mouse.get_pressed()[0]==1 and \
                self.in_game_frame_count>=self.cooldown_frame and \
                self.marbles_left>0:
                self.aim_marble(frame,mouse_x,mouse_y)

            if self.marbles_left<=0 and marble_max_vel<=0.1 and self.in_game_frame_count>self.cooldown_frame:
                if player_marbles_in>computer_marbles_in:
                    self.toggle_game_state(1)
                elif player_marbles_in==computer_marbles_in:
                    self.toggle_game_state(3)
                else:
                    self.toggle_game_state(2)
                    helper.play_sound("./assets/sounds/gunShotLong.wav")

            self.render_timer(10,10,frame,self.time_left)
            self.marbles_left_marble.render(frame)
            helper.render_text(
                frame,
                f" x {self.marbles_left}",
                WIDTH-35,
                20,
                font_size=20,
                color=Color.BLACK
            )

            
            helper.render_text(
                frame,
                ("Your turn!" if self.marbles_left>0 else "") if self.in_game_frame_count>self.cooldown_frame else "Computer's Turn!",
                WIDTH//2,
                20,
                font_size=24,
                color=Color.BLACK
            )

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            else:
                self.time_left-=1
            
            # game over:
            if self.time_left<=0:
                self.toggle_game_state(2)
                helper.play_sound("./assets/sounds/gunShotLong.wav")
            
            helper.render_text(frame,"Press 'Esc' or 'P' to pause",WIDTH-20,HEIGHT-20,font_size=18,color=Color.BLACK,align="right")
            self.in_game_frame_count+=1
        else:
            if self.game_state == 1:
                self.render_success(frame)
            elif self.game_state == 2:
                self.render_fail(frame)
            elif self.game_state == 3:
                self.render_draw(frame)
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
        if event.type==pg.MOUSEBUTTONDOWN:
            if not self.paused:
                in_preparation = self.preparation_time*60-self.in_game_frame_count>0
                if not in_preparation:
                    if mouse_y>=self.shoot_y:
                        self.first_mouse_pos = (mouse_x,mouse_y)
        if event.type==pg.MOUSEBUTTONUP:
            if not self.paused:
                in_preparation = self.preparation_time*60-self.in_game_frame_count>0
                if not in_preparation:
                    first_mouse_x, first_mouse_y = self.first_mouse_pos
                    if first_mouse_x is not None and first_mouse_y is not None:
                        if self.in_game_frame_count>=self.cooldown_frame and self.marbles_left>0:
                            self.shoot_marble(mouse_x,mouse_y)
                            self.cooldown_frame = self.in_game_frame_count + self.cooldown

    def aim_marble(self,frame,mouse_x,mouse_y):
        first_mouse_x, first_mouse_y = self.first_mouse_pos
        if first_mouse_x is not None and first_mouse_y is not None:
            marble = Marble(first_mouse_x,first_mouse_y,self.marble_size,Color.SQUID_TEAL)
            marble.render(frame)
            pg.draw.line(frame,Color.SQUID_PINK,self.first_mouse_pos,(mouse_x,mouse_y),width=2)

    def shoot_marble(self,mouse_x,mouse_y):
        first_mouse_x, first_mouse_y = self.first_mouse_pos
        if first_mouse_x and first_mouse_y is not None:
            self.marbles_left-=1
            angle = math.atan2((first_mouse_y-mouse_y),(first_mouse_x-mouse_x))
            distance = math.hypot(mouse_x - first_mouse_x, mouse_y - first_mouse_y)
            vx = math.cos(angle)*distance*0.2
            vy = math.sin(angle)*distance*0.2
            self.marbles.append(Marble(first_mouse_x,first_mouse_y,self.marble_size,Color.SQUID_TEAL,player_tag=1,vx=vx,vy=vy,max_speed=100))
        helper.play_sound("./assets/sounds/marbleDrop.wav",volume=0.25,continuous=True)

    def shoot_marble_comp(self,x,y):
        # angle = 1.25*math.pi+random.random()*math.pi//2
        hole_x,hole_y = self.hole.pos
        angle = math.atan2(hole_y-y,hole_x-x)
        distance = random.random()*10+45
        vx,vy = math.cos(angle)*distance, math.sin(angle)*distance
        self.marbles.append(Marble(x,y,self.marble_size,Color.SQUID_PINK,player_tag=2,vx=vx,vy=vy,max_speed=100))
        helper.play_sound("./assets/sounds/marbleDrop.wav",volume=0.25,continuous=True)

    def render_fail(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Eliminated :(",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,font_size=20)
        helper.render_text(frame," by clicking the 'Back to Levels' button! :)",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_draw(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"It's a draw!",WIDTH/2,HEIGHT/3,font_size=40)
        # helper.render_text(frame,"The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,font_size=20)
        # helper.render_text(frame," by clicking the 'Back to Levels' button! :)",WIDTH/2,HEIGHT/2.1,font_size=20)
        self.return_lvls_btn.render(frame)
    def render_success(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"You win!",WIDTH/2,HEIGHT/3,font_size=40)
        self.return_lvls_btn.render(frame)
    def render_help(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame, "How to play: Marbles", WIDTH//2, 50, color=Color.WHITE, font_size=40,underline=True)
        helper.render_text(
            frame, "Objective: Sink more marbles into the large hole than your opponent!",
            WIDTH // 2, HEIGHT // 6, font_size=22, color=Color.WHITE
        )
        helper.render_image(
            frame, "./assets/img/marbles/demoWithLabels.png",
            WIDTH // 2, HEIGHT // 1.95, [int(500 / 2), int(375 / 2)]
        )
        # helper.render_text(
        #     frame, "You control the teal-colored marbles.",
        #     WIDTH // 2, HEIGHT // 1.29, font_size=20, color=Color.WHITE
        # )
        # helper.render_text(
        #     frame, "Click and drag to aim. Release to shoot.",
        #     WIDTH // 2, HEIGHT // 1.22, font_size=20, color=Color.WHITE
        # )
        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(0) 
    def render_paused(self,frame):
        pg.draw.rect(frame,Color.SQUID_GREY,(0,0,WIDTH,HEIGHT))
        helper.render_text(frame,"Paused",WIDTH/2,HEIGHT/3,font_size=40)
        helper.render_text(frame,"Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,font_size=20)
        self.restart_btn.render(frame)
        self.exit_btn.render(frame)