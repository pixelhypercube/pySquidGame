import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
import Settings

class Circle:
    def __init__(self,x,y,r,color,max_speed=0.5,stroke_color=Color.black):
        self.pos = [x,y]
        self.color = color
        self.r = r
        self.vel = [0,0]
        self.acc = [0,0]
        self.max_speed = max_speed
    
    def render(self,frame):
        pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r)+1)
        pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))

        # update position
        for i in range(len(self.pos)):
            self.pos[i] = self.pos[i] - self.vel[i] if self.pos[i]-self.r <=10 or self.pos[i]+self.r >= Settings.WIDTH-10 else self.pos[i] + self.vel[i]
            self.vel[i] = max(self.acc[i]+self.vel[i],self.max_speed)

    def detect_contact(self,pos):
        return math.sqrt((self.x-pos[0])**2+(self.y-pos[1])**2)<self.r*4

    def contact_circle(self,circle):
        distance = math.sqrt((self.pos[0]-circle.pos[0])**2+(self.pos[1]-circle.pos[1])**2)
        if (distance<circle.r+self.r):
            angle = math.atan2(self.pos[1]-circle.pos[1],self.pos[0]-circle.pos[0])
            self.vel[0] += math.cos(angle) * 0.4
            self.vel[1] += math.sin(angle) * 0.4
            circle.vel[0] -= math.cos(angle) * 0.4
            circle.vel[1] -= math.sin(angle) * 0.4
            # for i in range(len(self.vel)):
            #     self.vel[i] += math.cos(angle) * 0.4 if i%2==0 else math.sin(angle) * 0.4
            #     circle.vel[i] +-= math.cos(angle) * 0.4 if i%2==0 else math.sin(angle) * 0.4