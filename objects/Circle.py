from components.Color import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT
from scipy.spatial import KDTree

class Circle:
    def __init__(self,x,y,r,color,max_speed=0.5,stroke_color=Color.BLACK,stroke_thickness=1,game_state=-1):
        self.pos = [x,y]
        self.color = color
        self.r = r
        self.vel = [0,0]
        self.acc = [0,0]
        self.max_speed = max_speed
        self.friction = 0.05
        self.stroke_color = stroke_color
        self.stroke_thickness = stroke_thickness
        self.game_state = game_state

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

    def detect_nearest_block(self, blocks):
        min_dist = float('inf')
        nearest = None
        cx, cy = self.pos

        for block in blocks:
            block_x, block_y, block_w, block_h = block.pos[0], block.pos[1], block.dim[0], block.dim[1]

            closest_x = max(block_x, min(cx, block_x + block_w))
            closest_y = max(block_y, min(cy, block_y + block_h))

            dx = cx - closest_x
            dy = cy - closest_y
            dist_sq = dx * dx + dy * dy

            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest = block

        return nearest


    def detect_block_contact(self, block):
        block_x, block_y, block_w, block_h = block.pos[0], block.pos[1], block.dim[0], block.dim[1]
        cx, cy = self.pos
        r = self.r

        closest_x = max(block_x, min(cx, block_x + block_w))
        closest_y = max(block_y, min(cy, block_y + block_h))

        dx = cx - closest_x
        dy = cy - closest_y
        return (dx*dx + dy*dy) < r*r
    def detect_circle_contact(self, circle_pos):
        dx = self.pos[0] - circle_pos[0]
        dy = self.pos[1] - circle_pos[1]
        return dx * dx + dy * dy < (self.r * 4) ** 2

    def get_other_circle_dist(self,circle):
        x,y = self.pos
        oc_x,oc_y = circle.pos
        return math.hypot(oc_x-x,oc_y-y)

    def contact_circle(self,circle):
        dx = self.pos[0] - circle.pos[0]
        dy = self.pos[1] - circle.pos[1]
        distance = math.hypot(dx, dy)
        min_dist = self.r + circle.r

        if distance < min_dist and distance != 0:
            overlap = 0.5 * (min_dist - distance)
            norm_dx = dx / distance
            norm_dy = dy / distance
            self.pos[0] += norm_dx * overlap
            self.pos[1] += norm_dy * overlap
            circle.pos[0] -= norm_dx * overlap
            circle.pos[1] -= norm_dy * overlap

            rel_vx = self.vel[0] - circle.vel[0]
            rel_vy = self.vel[1] - circle.vel[1]

            vel_along_normal = rel_vx * norm_dx + rel_vy * norm_dy

            if vel_along_normal > 0:
                return

            restitution = 1  # 1 = perfectly elastic, 0 = inelastic
            impulse = -(1 + restitution) * vel_along_normal
            impulse /= 2 

            impulse_x = impulse * norm_dx
            impulse_y = impulse * norm_dy

            self.vel[0] += impulse_x
            self.vel[1] += impulse_y
            circle.vel[0] -= impulse_x
            circle.vel[1] -= impulse_y
    
    def contact_block(self, block):
        block_x, block_y, block_w, block_h = block.pos[0], block.pos[1], block.dim[0], block.dim[1]
        cx, cy = self.pos

        closest_x = max(block_x, min(cx, block_x + block_w))
        closest_y = max(block_y, min(cy, block_y + block_h))

        dx = cx - closest_x
        dy = cy - closest_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return

        push_strength = 2
        self.vel[0] += (dx / distance) * push_strength
        self.vel[1] += (dy / distance) * push_strength
    
    def contains(self, x, y):
        o_x,o_y = self.pos
        return (o_x-x)**2+(o_y-y)**2<=self.r**2