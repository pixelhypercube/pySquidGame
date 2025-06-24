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
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,time_left=120,dalgona_size=150):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.1,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Go back",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]
        self.game_state = -1
        self.dalgona_size = dalgona_size

        self.scrape_color = Color.HONEYCOMB_DARK_YELLOW

        # dalgona
        self.dalgona_shapes = ["circle", "star", "square", "umbrella"]
        self.dalgona = Dalgona(WIDTH//2, HEIGHT//2, self.dalgona_size, Color.HONEYCOMB_YELLOW,self.dalgona_shapes[random.randint(0, len(self.dalgona_shapes) - 1)],stroke_thickness=10)
        self.selected_shape = None

        self.min_points_required = 300

        self.needle_points = []

        self.time_left = time_left*60

    def calc_accuracy(self):
        total_points = len(self.needle_points)
        if total_points==0:
            return 0
        
        accurate_points = 0
        if self.dalgona.shape=="circle":
            self.min_points_required = 350

            cx,cy = self.dalgona.pos
            ideal_radius = self.dalgona.r//2
            tolerance = self.dalgona.stroke_thickness//2
            for point in self.needle_points:
                dx = point[0]-cx
                dy = point[1]-cy
                dist = math.hypot(dx,dy)
                if abs(dist-ideal_radius)<=tolerance:
                    accurate_points+=1
        elif self.dalgona.shape=="square":
            self.min_points_required = 350

            cx,cy = self.dalgona.pos
            half = self.dalgona.r//2
            tolerance = self.dalgona.stroke_thickness//2
            for px,py in self.needle_points:
                left = cx-half
                right = cx+half
                top = cy-half
                bottom = cy+half

                near_x = min(max(px,left),right)
                near_y = min(max(py,top),bottom)

                if (abs(px-near_x)<=tolerance or abs(py-near_y)<=tolerance) and \
                    (abs(px-cx)>half-tolerance or abs(py-cy)>half-tolerance):
                        accurate_points+=1
        elif self.dalgona.shape=="star":
            self.min_points_required = 350

            # regenerate star shape points
            cx, cy = self.dalgona.pos
            points = []
            num_points = 5
            outer_radius = self.dalgona.r * 0.5
            inner_radius = self.dalgona.r * 0.2
            for i in range(num_points * 2):
                angle = i * math.pi / num_points
                radius = outer_radius if i % 2 == 0 else inner_radius
                px = cx + radius * math.cos(angle - math.pi / 2)
                py = cy + radius * math.sin(angle - math.pi / 2)
                points.append((px, py))
            
            edges = [(points[i], points[(i+1)%len(points)]) for i in range(len(points))]

            def point_to_segment_dist(px, py, x1, y1, x2, y2):
            # Calculate the distance from point (px,py) to line segment (x1,y1)-(x2,y2)
                line_mag = math.hypot(x2 - x1, y2 - y1)
                if line_mag == 0:
                    return math.hypot(px - x1, py - y1)
                u = max(0, min(1, ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / line_mag**2))
                ix = x1 + u * (x2 - x1)
                iy = y1 + u * (y2 - y1)
                return math.hypot(px - ix, py - iy)
            
            tolerance = self.dalgona.stroke_thickness
            for px, py in self.needle_points:
                if any(point_to_segment_dist(px, py, x1, y1, x2, y2) <= tolerance for (x1, y1), (x2, y2) in edges):
                    accurate_points += 1
        elif self.dalgona.shape=="umbrella":
            self.min_points_required = 400

            cx, cy = self.dalgona.pos
            r = self.dalgona.r
            top_radius = r * 0.5
            tolerance = 8  # pixels of leeway, you can tweak this
            accurate_points = 0

            # Precompute umbrella elements
            # Top arc bounding box
            top_rect = pg.Rect(cx - top_radius, cy - top_radius, top_radius * 2, top_radius * 2)

            # Bottom webs
            num_webs = 4
            web_radius = top_radius / num_webs

            # Handle shaft and arcs
            shaft_top = cy + top_radius // 2
            shaft_length = top_radius * 0.225
            handle_radius = top_radius * 0.5
            left_shaft_x = cx - web_radius // 2
            right_shaft_x = cx + web_radius // 2

            for px, py in self.needle_points:
                # Check top arc (semicircle)
                dx = px - cx
                dy = py - cy
                dist = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)

                if (
                    abs(dist - top_radius) <= tolerance and
                    0 <= angle <= math.pi
                ):
                    accurate_points += 1
                    continue

                # Check bottom web arcs
                for i in range(num_webs):
                    web_x = cx - top_radius + i * 2 * web_radius
                    web_y = cy
                    dx_web = px - (web_x + web_radius)
                    dy_web = py - web_y
                    dist_web = math.hypot(dx_web, dy_web)
                    if dist_web <= web_radius + tolerance and dist_web >= web_radius - tolerance:
                        accurate_points += 1
                        break  # Only count once

                # Check vertical handle shafts
                if (
                    abs(px - left_shaft_x) <= tolerance and
                    cy - shaft_length <= py <= shaft_top
                ) or (
                    abs(px - right_shaft_x) <= tolerance and
                    cy - shaft_length <= py <= shaft_top
                ):
                    accurate_points += 1
                    continue

                # Check left handle arc
                arc_center_x = left_shaft_x - handle_radius + 2 + handle_radius // 2
                arc_center_y = shaft_top - handle_radius // 2 + handle_radius // 2
                dx_l = px - arc_center_x
                dy_l = py - arc_center_y
                dist_l = math.hypot(dx_l, dy_l)
                if handle_radius - tolerance <= dist_l <= handle_radius + tolerance:
                    accurate_points += 1
                    continue

                # Check right handle arc
                arc_center_x = right_shaft_x - handle_radius * 2 + 2 + handle_radius
                arc_center_y = shaft_top - handle_radius + handle_radius
                dx_r = px - arc_center_x
                dy_r = py - arc_center_y
                dist_r = math.hypot(dx_r, dy_r)
                if handle_radius * 2 - tolerance <= dist_r <= handle_radius * 2 + tolerance:
                    accurate_points += 1
                    continue

                # Bottom handle connecting line
                line_y = shaft_top
                left_line_x = left_shaft_x - handle_radius * 1.5 + 2
                right_line_x = right_shaft_x - handle_radius * 1.5 + 2
                if (
                    abs(py - line_y) <= tolerance and
                    left_line_x <= px <= right_line_x
                ):
                    accurate_points += 1
            
        accuracy_score = (accurate_points/total_points)*100
        return accuracy_score

    def restart_game(self):
        self.game_state = -1
        self.dalgona.reset()

        self.in_game_frame_count = 0
        self.time_left = self.time * 60
        self.preparation_time = 5

        self.needle_points = []

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

    def scrape_needle(self,mouse_x,mouse_y):
        if ((WIDTH//2-mouse_x)**2+(HEIGHT//2-mouse_y)**2<self.dalgona_size**2):
            self.needle_points.append([mouse_x,mouse_y])

    def mousedown_listener(self,event,mouse_x,mouse_y):
        if event.type==pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0]:
                in_preparation = self.preparation_time*60-self.in_game_frame_count>0
                if not in_preparation:
                    self.scrape_needle(mouse_x,mouse_y)
        elif event.type==pg.MOUSEBUTTONUP:
            pass

    def render_needle_points(self,frame):
        for needle_point in self.needle_points:
            pg.draw.circle(frame, Color.BLACK,needle_point, 3)

    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            pg.draw.rect(frame, self.bg_color, (0, 0, WIDTH, HEIGHT))
            self.dalgona.render(frame)
            self.draw_needle(frame,mouse_x,mouse_y)
            self.render_needle_points(frame)

            accuracy = (self.calc_accuracy()*100)//100 
            if len(self.needle_points) >= self.min_points_required:
                if accuracy < 60:
                    self.toggle_game_state(frame, 2)
                elif accuracy >= 90:
                    self.toggle_game_state(frame, 1)

            self.render_timer(10,10,frame,self.time_left)

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            else:
                self.time_left-=1

            # game over:
            if self.time_left<=0:
                self.toggle_game_state(frame,2)

            self.in_game_frame_count+=1
            # for debug
            # helper.render_text(frame,str(accuracy),100,20,font_size=24,color=Color.BLACK)
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
        helper.render_text(frame, "How to play: Honeycomb", WIDTH // 2, 50, color=Color.WHITE, font_size=30)
        helper.render_text(
            frame, "Objective: Carve out the shape without breaking the honeycomb!",
            WIDTH // 2, HEIGHT // 6, font_size=22, color=Color.WHITE
        )
        helper.render_image(
            frame, "./assets/img/honeycomb/demo.png",
            WIDTH // 2, HEIGHT // 2.1, [int(500 / 2.25), int(375 / 2.25)]
        )
        helper.render_text(
            frame, "Click and drag slowly along the outline of the shape.",
            WIDTH // 2, HEIGHT // 1.29, font_size=20, color=Color.WHITE
        )
        helper.render_text(
            frame, "Going too fast or straying off will crack the candy!",
            WIDTH // 2, HEIGHT // 1.22, font_size=20, color=Color.WHITE
        )

        self.help_start_btn.render(frame)
        self.help_back_btn.render(frame)
        self.help_start_btn.function = lambda: self.toggle_game_state(frame,0) 