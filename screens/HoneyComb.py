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
from scipy.spatial import ConvexHull

helper = Helper()

class HoneyComb(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,time_left=120,dalgona_size=150):
        super().__init__(time, preparation_time, bg_color)
        self.help_start_btn = Button(WIDTH/2,HEIGHT/1.1,60,20,content="Start")
        self.help_back_btn = Button(80, HEIGHT / 10, 50, 25, content="Back\nto Levels", next_screen="levels")
        self.restart_btn = Button(WIDTH/2,HEIGHT/2,100,25,content="Restart Game",visible=self.paused,function=lambda:self.restart_game())
        self.exit_btn = Button(WIDTH/2,HEIGHT/2+75,100,25,content="Exit Game",next_screen="levels",visible=self.paused)
        self.return_lvls_btn = Button(WIDTH/2,HEIGHT/1.6,100,30,content="Back to Levels",next_screen="levels",visible=self.paused)
        self.buttons = [
            self.help_start_btn,self.help_back_btn,self.restart_btn,self.exit_btn,self.return_lvls_btn
        ]
        self.game_state = -1
        self.dalgona_size = dalgona_size

        self.scrape_color = Color.HONEYCOMB_DARK_YELLOW

        # dalgona
        self.dalgona_shapes = ["circle", "star", "triangle", "umbrella"]
        self.dalgona = Dalgona(WIDTH//2, HEIGHT//2, self.dalgona_size, Color.HONEYCOMB_YELLOW,self.dalgona_shapes[random.randint(0, len(self.dalgona_shapes) - 1)],stroke_thickness=10)
        self.selected_shape = None

        self.min_points_required = 300

        self.needle_points = []
        # self.accurate_needle_points = [] # for debugging

        self.furthest_needle_point_dist = 0

        #  calculate speed
        self.prev_mouse_pos = None
        self.mouse_speed = 0

        self.time_left = time_left*60


    def point_to_segment_dist(self,px,py,x1,y1,x2,y2):
        line_mag = math.hypot(x2-x1,y2-y1)
        if line_mag==0:
            return math.hypot(px-x1,py-y1)
        u = max(0, min(1, ((px-x1)*(x2-x1) + (py-y1)*(y2-y1)) / (line_mag**2)))
        ix = x1 + u * (x2-x1)
        iy = y1 + u * (y2-y1)
        return math.hypot(px-ix,py-iy)

    def point_on_arc_dist(self, px, py, cx, cy, radius, angle_start, angle_end, angle_slack=0.08):
        dx = px-cx
        dy = py-cy
        dist_to_center = math.hypot(dx, dy)

        angle = math.atan2(dy, dx)
        angle = (angle-math.pi) % (2*math.pi)

        angle_start %= 2*math.pi
        angle_end %= 2*math.pi

        def within(a, start, end):
            if start <= end:
                return (start-angle_slack) <= a <= (end+angle_slack)
            else:
                return a >= (start-angle_slack) or a <= (end+angle_slack)

        if within(angle, angle_start, angle_end):
            return abs(dist_to_center - radius)
        else:
            # Fallback to arc endpoints
            x1 = cx + math.cos(angle_start+math.pi/2)*radius
            y1 = cy + math.sin(angle_start+math.pi/2)*radius
            x2 = cx + math.cos(angle_end+math.pi/2)*radius
            y2 = cy + math.sin(angle_end+math.pi/2)*radius
            return min(math.hypot(px-x1,py-y1), math.hypot(px-x2,py-y2))

    def calc_accuracy(self):
        total_points = len(self.needle_points)
        if total_points==0:
            return 100
        accurate_points = 0
        cx,cy = self.dalgona.pos
        r = self.dalgona.r
        tolerance = self.dalgona.stroke_thickness//2
        if self.dalgona.shape=="circle":
            self.min_points_required = 700

            ideal_radius = r//2
            for point in self.needle_points:
                dx = point[0]-cx
                dy = point[1]-cy
                dist = math.hypot(dx,dy)
                if abs(dist-ideal_radius)<=tolerance:
                    accurate_points+=1
        elif self.dalgona.shape == "triangle":
            self.min_points_required = 700
            num_points = 3
            points = []
            for i in range(num_points):
                angle = 2*i*math.pi/num_points
                dist = r//1.75
                px = cx + math.cos(angle-math.pi/2)*dist
                py = cy + math.sin(angle-math.pi/2)*dist
                points.append((px,py))

            edges = [(points[i],points[(i+1)%len(points)]) for i in range(len(points))]
            tolerance = self.dalgona.stroke_thickness
            for px, py in self.needle_points:
                if any(self.point_to_segment_dist(px,py,x1,y1,x2,y2) <= tolerance for (x1,y1),(x2,y2) in edges):
                    accurate_points += 1
        elif self.dalgona.shape=="star":
            self.min_points_required = 800

            # regenerate star shape points
            points = []
            num_points = 5
            outer_radius = r//2
            inner_radius = r//5

            for i in range(num_points*2):
                angle = i*math.pi/num_points
                dist = outer_radius if i%2==0 else inner_radius
                px = cx+math.cos(angle-math.pi/2)*dist
                py = cy+math.sin(angle-math.pi/2)*dist
                points.append((px,py))
            
            edges = [(points[i], points[(i+1)%len(points)]) for i in range(len(points))]
            
            tolerance = self.dalgona.stroke_thickness
            for px, py in self.needle_points:
                if any(self.point_to_segment_dist(px,py,x1,y1,x2,y2) <= tolerance for (x1,y1),(x2,y2) in edges):
                    accurate_points += 1
        elif self.dalgona.shape=="umbrella":
            self.min_points_required = 1000

            top_radius = self.dalgona.r * 0.5
            tolerance = self.dalgona.stroke_thickness // 2

            num_webs = 4
            web_radius = top_radius / num_webs

            shaft_top = cy + top_radius // 2
            shaft_length = top_radius * 0.225
            handle_radius = top_radius * 0.5

            left_shaft_x = cx - web_radius // 2
            right_shaft_x = cx + web_radius // 2
            shaft_bottom = cy - shaft_length

            left_arc_center_x = left_shaft_x - handle_radius / 2 + 2
            left_arc_center_y = shaft_top - handle_radius / 2 + handle_radius / 2

            right_arc_center_x = right_shaft_x - handle_radius * 2 + 2 + handle_radius
            right_arc_center_y = shaft_top - handle_radius + handle_radius

            left_line_x = left_shaft_x - handle_radius * 1.5 + 2
            right_line_x = right_shaft_x - handle_radius * 1.5 + 2
            line_y = shaft_top

            # self.accurate_needle_points = []

            for px, py in self.needle_points:
                # Top semicircle arc
                if self.point_on_arc_dist(px, py, cx, cy, top_radius, 0, math.pi) <= tolerance:
                    accurate_points += 1
                    # self.accurate_needle_points.append([px,py])
                    continue

                # Bottom web arcs
                matched_web = False
                for i in range(num_webs):
                    web_x = cx - top_radius + i * 2 * web_radius
                    web_cx = web_x + web_radius
                    web_cy = cy

                    if i == 1:
                        angle_start, angle_end = math.pi / 4, math.pi
                    elif i == 2:
                        angle_start, angle_end = 0, 3 * math.pi / 4
                    else:
                        angle_start, angle_end = 0, math.pi

                    if self.point_on_arc_dist(px, py, web_cx, web_cy, web_radius, angle_start, angle_end) <= tolerance:
                        accurate_points += 1
                        # self.accurate_needle_points.append([px,py])
                        matched_web = True
                        break
                if matched_web:
                    continue

                # Vertical shafts
                if self.point_to_segment_dist(px, py, left_shaft_x, shaft_bottom, left_shaft_x, shaft_top) <= tolerance or \
                self.point_to_segment_dist(px, py, right_shaft_x, shaft_bottom, right_shaft_x, shaft_top) <= tolerance:
                    accurate_points += 1
                    # self.accurate_needle_points.append([px,py])
                    continue

                # Left handle arc
                if self.point_on_arc_dist(px, py, left_arc_center_x, left_arc_center_y, handle_radius, math.pi, 2*math.pi) <= tolerance:
                    accurate_points += 1
                    # self.accurate_needle_points.append([px,py])
                    continue

                # Right handle arc
                if self.point_on_arc_dist(px, py, right_arc_center_x, right_arc_center_y, handle_radius*0.5, math.pi, 2*math.pi) <= tolerance:
                    accurate_points += 1
                    # self.accurate_needle_points.append([px,py])
                    continue

                # Connecting line at bottom of handle
                if self.point_to_segment_dist(px, py, left_line_x, line_y, right_line_x, line_y) <= tolerance:
                    accurate_points += 1
                    # self.accurate_needle_points.append([px,py])
        accuracy_score = (accurate_points/total_points)*100
        return accuracy_score


    def restart_game(self):
        self.game_state = -1
        self.dalgona.reset()

        self.in_game_frame_count = 0
        self.time_left = self.time * 60
        self.preparation_time = 5

        self.needle_points = []
        self.furthest_needle_point_dist = 0
        # self.accurate_needle_points = [] # for debugging

        self.prev_mouse_pos = None
        self.mouse_speed = 0

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
        elif state==-1:
            self.paused = True
            self.return_lvls_btn.visible = False

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
            self.needle_points.append((mouse_x,mouse_y))
            helper.play_sound(f"./assets/sounds/scrape{random.randint(1,5)}.wav",volume=0.5,continuous=True)

    def mousedown_listener(self,event,mouse_x,mouse_y):
        if event.type==pg.MOUSEMOTION:
            if pg.mouse.get_pressed()[0]:
                in_preparation = self.preparation_time*60-self.in_game_frame_count>0
                if not in_preparation and not self.paused:
                    self.mouse_speed = 0
                    if self.prev_mouse_pos is not None:
                        prev_mouse_x,prev_mouse_y = self.prev_mouse_pos
                        self.mouse_speed = math.hypot(prev_mouse_x-mouse_x,prev_mouse_y-mouse_y)
                    self.prev_mouse_pos = (mouse_x,mouse_y)
                    self.scrape_needle(mouse_x,mouse_y)
                    self.furthest_needle_point_dist = self.max_distance(self.needle_points)
        elif event.type==pg.MOUSEBUTTONUP:
            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if not in_preparation and not self.paused:
                self.prev_mouse_pos = None
                self.mouse_speed = 0

    def cross(self, o, a, b):
        return (a[0]-o[0]) * (b[1]-o[1]) - (a[1]-o[1]) * (b[0]-o[0])

    def convex_hull(self, points):
        points = sorted(set(points))
        if len(points) <= 1:
            return points

        lower = []
        for p in points:
            while len(lower) >= 2 and self.cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and self.cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]

    def max_distance(self, points) -> float:
        hull = self.convex_hull(points)
        n = len(hull)
        if n==1: return 0.0
        if n==2: return math.dist(hull[0],hull[1])

        max_dist = 0
        j = 1
        for i in range(n):
            while True:
                ni = (i+1) % n
                nj = (j+1) % n
                if abs(self.cross(hull[i],hull[ni],hull[nj])) > abs(self.cross(hull[i],hull[ni],hull[j])):
                    j = nj
                else:
                    break
            max_dist = max(max_dist, math.dist(hull[i],hull[j]))

        return max_dist

    def render_needle_points(self,frame):
        for needle_point in self.needle_points:
            pg.draw.circle(frame, Color.BLACK,needle_point, 2)
        

        # for debugging
        # for needle_point in self.accurate_needle_points:
        #     pg.draw.circle(frame, Color.RED,needle_point, 3)

    def render(self,frame,mouse_x,mouse_y):
        if not self.paused:
            pg.draw.rect(frame, self.bg_color, (0, 0, WIDTH, HEIGHT))
            self.dalgona.render(frame)
            self.draw_needle(frame,mouse_x,mouse_y)
            self.render_needle_points(frame)

            accuracy = (self.calc_accuracy()*100)//100 
            if self.furthest_needle_point_dist>=self.dalgona_size and len(self.needle_points) >= self.min_points_required:
                if accuracy < 60:
                    self.toggle_game_state( 2)
                    helper.play_sound("./assets/sounds/biscuitBreak.wav")
                elif accuracy >= 90:
                    self.toggle_game_state( 1)
                    helper.play_sound("./assets/sounds/biscuitBreak.wav")

            self.render_timer(10,10,frame,self.time_left)

            in_preparation = self.preparation_time*60-self.in_game_frame_count>0
            if (in_preparation):
                self.render_prep_screen(frame,int((self.preparation_time*60-self.in_game_frame_count)/60)+1)
            else:
                self.time_left-=1

            # game over:
            if self.time_left<=0 or self.mouse_speed>=10:
                self.toggle_game_state(2)
                helper.play_sound("./assets/sounds/gunShotLong.wav")

            helper.render_text(frame,"Press 'Esc' or 'P' to pause",WIDTH-20,HEIGHT-20,font_size=18,color=Color.BLACK,align="right")

            self.in_game_frame_count+=1
            # for debug
            # helper.render_text(frame,str(self.furthest_needle_point_dist),WIDTH//2,40,font_size=24,color=Color.BLACK)
            # helper.render_text(frame,str(accuracy),WIDTH//2,20,font_size=24,color=Color.BLACK)
            # helper.render_text(frame,str(self.mouse_speed),WIDTH//2,60,font_size=24,color=Color.BLACK)
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
        helper.render_text(frame, "How to play: Honeycomb", WIDTH // 2, 50, color=Color.WHITE, font_size=40,underline=True)
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
        self.help_start_btn.function = lambda: self.toggle_game_state(0) 