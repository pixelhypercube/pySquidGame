from objects.Circle import Circle
from components.Color import Color
from threading import Timer
import pygame as pg
import random
import math

class Dalgona(Circle):
    def __init__(self, x, y, r, color, shape, max_speed=0.5, stroke_color=Color.HONEYCOMB_DARK_YELLOW,tin_color=Color.DARK_GREY,stroke_thickness=8):
        super().__init__(x, y, r, color, max_speed, stroke_color, stroke_thickness)
        self.shape = shape
        self.tin_color = tin_color
        self.dalgona_shapes = ["circle", "star", "triangle", "umbrella"]
    def draw_star(self, frame, x, y):
        points = []
        num_points = 5
        outer_radius = self.r//2
        inner_radius = self.r//5

        for i in range(num_points*2):
            angle = i*math.pi/num_points
            dist = outer_radius if i%2==0 else inner_radius
            px = x+math.cos(angle-math.pi/2)*dist
            py = y+math.sin(angle-math.pi/2)*dist
            points.append((px,py))
        pg.draw.polygon(frame,self.stroke_color,points,width=self.stroke_thickness//2)
        

    def draw_triangle(self,frame,x,y):
        num_points = 3
        points = []
        for i in range(num_points):
            angle = 2*i*math.pi/num_points
            dist = self.r//1.75
            px = x + math.cos(angle-math.pi/2)*dist
            py = y + math.sin(angle-math.pi/2)*dist
            points.append((px,py))
        pg.draw.polygon(frame,self.stroke_color,points,width=self.stroke_thickness//2)

    # def draw_square(self, frame, x, y):
        # pg.draw.rect(frame,self.stroke_color,pg.Rect(x-self.r//2,y-self.r//2,self.r,self.r),width=self.stroke_thickness//2)

    def draw_umbrella(self, frame, x, y):
        # Top arc (main umbrella)
        top_radius = self.r * 0.5 
        top_rect = pg.Rect(x - top_radius, y - top_radius, top_radius * 2, top_radius * 2)
        pg.draw.arc(frame, self.stroke_color, top_rect, 0, math.pi, width=self.stroke_thickness//2)

        # Bottom semicircle webs
        num_webs = 4
        web_radius = top_radius / num_webs  # So total width matches the top arc

        for i in range(num_webs):
            # Position each semicircle horizontally under the top arc
            web_x = x - top_radius + i * 2 * web_radius
            web_y = y  # Align with the bottom of the top arc
            web_rect = pg.Rect(web_x, web_y-web_radius, web_radius * 2, web_radius * 2)
            if i==1:
                pg.draw.arc(frame, self.stroke_color, web_rect, math.pi/4, math.pi, width=self.stroke_thickness//2)
            elif i==2:
                pg.draw.arc(frame, self.stroke_color, web_rect, 0, 3*math.pi/4, width=self.stroke_thickness//2)
            else:
                pg.draw.arc(frame, self.stroke_color, web_rect, 0, math.pi, width=self.stroke_thickness//2)
        
        # Dimensions for handle
        shaft_top = y + top_radius // 2  # Bottom of the vertical sticks
        shaft_length = top_radius * 0.225
        handle_radius = top_radius * 0.5

        # Positions of the two vertical shafts
        left_shaft_x = x - web_radius // 2
        right_shaft_x = x + web_radius // 2

        # Draw the vertical shafts
        pg.draw.line(frame, self.stroke_color, (left_shaft_x, y - shaft_length), (left_shaft_x, shaft_top), width=self.stroke_thickness // 2)
        pg.draw.line(frame, self.stroke_color, (right_shaft_x, y - shaft_length), (right_shaft_x, shaft_top), width=self.stroke_thickness // 2)

        # left
        left_arc_rect = pg.Rect(
            left_shaft_x - handle_radius+2,
            shaft_top-handle_radius//2,
            handle_radius,
            handle_radius
        )
        pg.draw.arc(
            frame,
            self.stroke_color,
            left_arc_rect,
            math.pi,
            math.pi*2,
            width=self.stroke_thickness // 2
        )

        # right arc
        right_arc_rect = pg.Rect(
            right_shaft_x - handle_radius*2+2,
            shaft_top-handle_radius,
            handle_radius * 2,
            handle_radius * 2
        )
        pg.draw.arc(
            frame,
            self.stroke_color,
            right_arc_rect,
            math.pi,
            math.pi*2,
            width=self.stroke_thickness // 2
        )

        # Connect the bottom of the two arcs with a line to "close" the handle
        pg.draw.line(
            frame,
            self.stroke_color,
            (left_shaft_x-handle_radius*1.5+2, shaft_top),
            (right_shaft_x-handle_radius*1.5+2, shaft_top),
            width=self.stroke_thickness // 2
        )

    def reset(self):
        self.shape = self.dalgona_shapes[random.randint(0,len(self.dalgona_shapes)-1)]

    def render(self,frame):
        x, y = self.pos
        pg.draw.circle(frame, self.tin_color, (int(x), int(y)), int(self.r) + self.stroke_thickness)
        pg.draw.circle(frame, self.color, (int(x), int(y)), int(self.r))
        if (self.shape == "star"):
            self.draw_star(frame, x, y)
        elif (self.shape == "circle"):
            pg.draw.circle(frame, self.stroke_color, (int(x), int(y)), int(self.r//2),width=self.stroke_thickness//2)
        elif (self.shape == "triangle"):
            self.draw_triangle(frame, x, y)
        # elif (self.shape == "square"):
        #     self.draw_square(frame, x, y)
        elif (self.shape == "umbrella"):
            self.draw_umbrella(frame, x, y)