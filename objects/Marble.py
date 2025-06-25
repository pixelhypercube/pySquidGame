from objects.Circle import Circle
from components.Color import Color
from threading import Timer
import pygame as pg
import random
import math
from Settings import WIDTH,HEIGHT

class Marble(Circle):
    def __init__(self, x, y, r, color,player_tag=1,vx=0,vy=0, max_speed=0.5, stroke_color=Color.BLACK,stroke_thickness=1):
        super().__init__(x, y, r, color, max_speed, stroke_color, stroke_thickness)
        self.player_tag = player_tag # 1 - you, 2 - computer
        self.vel = [vx,vy]
        self.friction = 0.1

        # collision set
        self.colliding_with = set()

    def contact_circle(self, circle):
        dx = self.pos[0] - circle.pos[0]
        dy = self.pos[1] - circle.pos[1]
        distance = math.hypot(dx, dy)
        min_dist = self.r + circle.r

        if distance < min_dist and distance != 0:
            nx = dx / distance
            ny = dy / distance

            dvx = self.vel[0] - circle.vel[0]
            dvy = self.vel[1] - circle.vel[1]

            vn = dvx * nx + dvy * ny

            if vn < 0:
                impulse = -2 * vn / 2

                self.vel[0] += impulse * nx
                self.vel[1] += impulse * ny
                circle.vel[0] -= impulse * nx
                circle.vel[1] -= impulse * ny

            overlap = min_dist - distance
            correction = overlap / 2
            self.pos[0] += nx * correction
            self.pos[1] += ny * correction
            circle.pos[0] -= nx * correction
            circle.pos[1] -= ny * correction

    def render(self,frame):
        x, y = self.pos
        x, y = int(x), int(y)
        r = int(self.r)

        pg.draw.circle(frame, self.stroke_color, (x, y), r + self.stroke_thickness)

        pg.draw.circle(frame, self.color, (x, y), r)

        highlight_radius = int(r * 0.3)
        highlight_offset = int(r * 0.4)
        highlight_color = (255, 255, 255, 100)  # semi-transparent white
        highlight_surface = pg.Surface((highlight_radius * 2, highlight_radius * 2), pg.SRCALPHA)
        pg.draw.circle(highlight_surface, highlight_color, (highlight_radius, highlight_radius), highlight_radius)
        frame.blit(highlight_surface, (x - highlight_radius - highlight_offset, y - highlight_radius - highlight_offset))

        # Update physics
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]
            self.vel[i] += self.acc[i]
            self.vel[i] = max(-self.max_speed, min(self.max_speed, self.vel[i]))
            self.vel[i] *= (1 - self.friction)

        if x - r < 0:
            self.pos[0] = r
            self.vel[0] *= -0.8
        elif x + r > WIDTH:
            self.pos[0] = WIDTH - r
            self.vel[0] *= -0.8

        if y - r < 0:
            self.pos[1] = r
            self.vel[1] *= -0.8
        elif y + r > HEIGHT:
            self.pos[1] = HEIGHT - r
            self.vel[1] *= -0.8
