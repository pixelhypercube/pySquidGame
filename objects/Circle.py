from components.Color import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from scipy.spatial import KDTree

class Circle:
    def __init__(self,x,y,r,color,max_speed=0.5,stroke_color=Color.BLACK,stroke_thickness=1):
        self.pos = [x,y]
        self.color = color
        self.r = r
        self.vel = [0,0]
        self.acc = [0,0]
        self.max_speed = max_speed
        self.friction = 0.05
        self.stroke_color = stroke_color
        self.stroke_thickness = stroke_thickness

    def render(self,frame):
        x,y = self.pos
        pg.draw.circle(frame,self.stroke_color,(int(x),int(y)),int(self.r)+self.stroke_thickness)
        pg.draw.circle(frame,self.color,(int(x),int(y)),int(self.r))

        # update position
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]
            self.vel[i] += self.acc[i]
            self.vel[i] = max(-self.max_speed, min(self.max_speed, self.vel[i]))

            self.vel[i] *= (1 - self.friction)
    
    def set_pos(self,x,y):
        self.pos = [x,y]

    def get_scalar_vel(self):
        return math.sqrt(self.vel[0]**2 + self.vel[1]**2)

    def detect_nearest_circle(self,circles):
        points = [circle.pos for circle in circles if circle != self]
        if not points:
            return None
        tree = KDTree(points)

        distance, index = tree.query(self.pos)

        filtered_circles = [circle for circle in circles if circle != self]
        return filtered_circles[index]

    def detect_nearest_wall(self, walls):
        min_dist = float('inf')
        nearest = None
        cx, cy = self.pos

        for wall in walls:
            wall_x, wall_y, wall_w, wall_h = wall.pos[0], wall.pos[1], wall.dim[0], wall.dim[1]

            closest_x = max(wall_x, min(cx, wall_x + wall_w))
            closest_y = max(wall_y, min(cy, wall_y + wall_h))

            dx = cx - closest_x
            dy = cy - closest_y
            dist_sq = dx * dx + dy * dy

            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest = wall

        return nearest


    def detect_wall_contact(self, wall):
        wall_x, wall_y, wall_w, wall_h = wall.pos[0], wall.pos[1], wall.dim[0], wall.dim[1]
        cx, cy = self.pos
        r = self.r

        closest_x = max(wall_x, min(cx, wall_x + wall_w))
        closest_y = max(wall_y, min(cy, wall_y + wall_h))

        dx = cx - closest_x
        dy = cy - closest_y
        return (dx*dx + dy*dy) < r*r
    def detect_circle_contact(self, circle_pos):
        dx = self.pos[0] - circle_pos[0]
        dy = self.pos[1] - circle_pos[1]
        return dx * dx + dy * dy < (self.r * 4) ** 2


    def contact_circle(self,circle):
        distance = math.sqrt((self.pos[0]-circle.pos[0])**2+(self.pos[1]-circle.pos[1])**2)
        if (distance<circle.r+self.r):
            angle = math.atan2(self.pos[1]-circle.pos[1],self.pos[0]-circle.pos[0])
            self.vel[0] += math.cos(angle) * 0.4
            self.vel[1] += math.sin(angle) * 0.4
            circle.vel[0] -= math.cos(angle) * 0.4
            circle.vel[1] -= math.sin(angle) * 0.4
    
    def contact_wall(self, wall):
        wall_x, wall_y, wall_w, wall_h = wall.pos[0], wall.pos[1], wall.dim[0], wall.dim[1]
        cx, cy = self.pos

        closest_x = max(wall_x, min(cx, wall_x + wall_w))
        closest_y = max(wall_y, min(cy, wall_y + wall_h))

        dx = cx - closest_x
        dy = cy - closest_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return

        push_strength = 2
        self.vel[0] += (dx / distance) * push_strength
        self.vel[1] += (dy / distance) * push_strength