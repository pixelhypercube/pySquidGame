from objects.Circle import Circle
from components.Color import Color
from threading import Timer
import random
import pygame as pg
from components.Helper import Helper

helper = Helper()

class Player(Circle):
    def __init__(self, x, y, r, color, max_speed=0.5,stroke_color=Color.BLACK,friction=0.05,stroke_thickness=1,num_label=""):
        super().__init__(x, y, r, color, max_speed, stroke_color, stroke_thickness)
        self.num_label = num_label
        self.friction = friction

    def render(self,frame):
        x,y = self.pos
        pg.draw.circle(frame,self.stroke_color,(int(x),int(y)),int(self.r)+self.stroke_thickness)
        pg.draw.circle(frame,self.color,(int(x),int(y)),int(self.r))

        helper.render_text(frame,str(self.num_label),x,y,font_size=self.r)

        # update position
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]
            self.vel[i] += self.acc[i]
            self.vel[i] = max(-self.max_speed, min(self.max_speed, self.vel[i]))

            self.vel[i] *= (1 - self.friction)

    def move(self, dx, dy):
        self.vel = [dx * self.max_speed,dy * self.max_speed]

    def accelerate(self, ax, ay):
        self.acc = [ax * self.max_speed, ay * self.max_speed]

    def boost(self):
        self.max_speed = min(1.1, self.max_speed * 1.5)
        Timer(0.5, lambda: setattr(self, 'max_speed', self.max_speed / 1.5)).start()
