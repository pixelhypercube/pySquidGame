from components.Color import Color
import pygame as pg
from objects.Block import Block
class Ddakji(Block):
    def __init__(self, x, y, w, h, color, stroke_thickness=0, stroke_color=Color.BLACK):
        super().__init__(x, y, w, h, color, stroke_thickness, stroke_color)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.z = 0 # altitude
        self.dz = 0 # velocity of altitude
        self.gravity = 1 

        self.angle = 0
        self.is_grabbing = False

        # self.roll = 0
        # self.yaw = 0
    def render(self,frame):
        w,h = self.dim
        x,y = self.pos

        # shadow
        shadow_surface = pg.Surface((w-self.z//4,h-self.z//4),pg.SRCALPHA)
        shadow_surface.fill((0,0,0,100))
        frame.blit(shadow_surface,(x+self.z,y+self.z))

        pg.draw.rect(frame,self.color,(x-self.z//2,y-self.z//2,w+self.z,h+self.z))
        pg.draw.rect(frame,Color.BLACK,(x-self.z//2,y-self.z//2,w+self.z,h+self.z),width=self.stroke_thickness)
        pg.draw.line(frame,Color.BLACK,(x-self.z//2,y-self.z//2),(x+w+self.z//2,y+h+self.z//2),width=self.stroke_thickness)
        pg.draw.line(frame,Color.BLACK,(x+w+self.z//2,y-self.z//2),(x-self.z//2,y+h+self.z//2),width=self.stroke_thickness)
        
        if not self.is_grabbing:
            if self.z > 0:
                self.z += self.dz
                self.dz -= self.gravity
            else: self.z = 0
        else: self.dz = 0

    def grab(self,mouse_x,mouse_y):
        self.is_grabbing = self.contains(mouse_x,mouse_y)
        if self.is_grabbing:
            self.z = 20
            w,h = self.dim
            self.pos = [mouse_x-w//2,mouse_y-h//2]
    
    def smash(self,ddakji):
        self.is_grabbing = False
        ox,oy = ddakji.pos
        ow,oh = ddakji.dim
        self.z = 0
