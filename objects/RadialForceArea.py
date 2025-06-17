from components.Color import Color
from objects.ForceArea import ForceArea
import pygame as pg

class RadialForceArea(ForceArea):
    def __init__(self,x,y,w,h,color,stroke_thickness=0,stroke_color=Color.BLACK,force_strength=10):
        super().__init__(x,y,w,h,color,stroke_thickness,stroke_color,force_strength)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
    
