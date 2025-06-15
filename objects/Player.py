from objects.Circle import Circle
from components.Color import Color
from threading import Timer
import random

class Player(Circle):
    def __init__(self, x, y, r, color, max_speed=0.5, stroke_color=Color.BLACK,stroke_thickness=1):
        super().__init__(x, y, r, color, max_speed, stroke_color, stroke_thickness)
    
    def move(self, dx, dy):
        self.vel = [dx * self.max_speed,dy * self.max_speed]
        if (dx<0.1 and dy<0.1):
            self.friction = 0

    def accelerate(self, ax, ay):
        self.acc = [ax * self.max_speed, ay * self.max_speed]
        if (ax<0.1 and ay<0.1):
            self.friction = 0.05
        else:
            self.friction = 0.01

    def boost(self):
        self.max_speed = min(1.1, self.max_speed * 1.5)
        Timer(0.5, lambda: setattr(self, 'max_speed', self.max_speed / 1.5)).start()
