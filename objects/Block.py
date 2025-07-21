from components.Color import Color
import pygame as pg
from components.Helper import Helper

helper = Helper()
class Block:
    def __init__(self,x,y,w,h,color,stroke_thickness=0,stroke_color=Color.BLACK,text_overlay=None):
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.color = color
        self.stroke_thickness = stroke_thickness
        self.stroke_color = stroke_color
        self.text_overlay = text_overlay
    def render(self,frame):
        pg.draw.rect(frame,self.stroke_thickness,(self.pos[0]-self.stroke_thickness, self.pos[1]-self.stroke_thickness, self.dim[0]+self.stroke_thickness*2, self.dim[1]+self.stroke_thickness*2))
        pg.draw.rect(frame,self.color,(self.pos[0], self.pos[1], self.dim[0], self.dim[1]))
        if self.text_overlay:
            helper.render_text(frame,self.text_overlay,self.pos[0]+self.dim[0]//2,self.pos[1]+self.dim[1]//2,color=Color.BLACK,align="center",font_size=18)
    def update(self):
        for i in range(len(self.pos)):
            self.pos[i] += self.vel[i]
            self.vel[i] *= 0.95
    def contains(self, x, y):
        o_x,o_y = self.pos
        w,h = self.dim
        return o_x <= x <= o_x + w and o_y <= y <= o_y + h
    def is_intersect(self,other):
        x,y = self.pos
        w,h = self.dim

        ox,oy = other.pos
        ow,oh = other.dim

        return x<ox+ow and x+w>ox and y<oy+oh and y+h>oy