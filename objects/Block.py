from components.Color import Color
import pygame as pg
class Block:
    def __init__(self,x,y,w,h,color,stroke_thickness=0,stroke_color=Color.BLACK):
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.color = color
        self.stroke_thickness = stroke_thickness
        self.stroke_color = Color.BLACK
    def render(self,frame):
        pg.draw.rect(frame,self.stroke_thickness,(self.pos[0]-self.stroke_thickness, self.pos[1]-self.stroke_thickness, self.dim[0]+self.stroke_thickness*2, self.dim[1]+self.stroke_thickness*2))
        pg.draw.rect(frame,self.color,(self.pos[0], self.pos[1], self.dim[0], self.dim[1]))
    def update(self):
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]
            self.vel[i] *= 0.95