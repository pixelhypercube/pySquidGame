from components.Color import Color
from objects.ForceArea import ForceArea
import pygame as pg

class LinearForceArea(ForceArea):
    def __init__(self,x,y,w,h,color=Color.SAND_DARK,stroke_thickness=0,stroke_color=Color.PURPLE,force_strength=10,force_direction=0):
        super().__init__(x,y,w,h,color,stroke_thickness,stroke_color,force_strength)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.force_direction = 0
    