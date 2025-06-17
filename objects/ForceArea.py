from objects.Block import Block
from components.Color import Color
import pygame as pg

class ForceArea(Block):
    def __init__(self,x,y,w,h,color,stroke_thickness=0,stroke_color=Color.BLACK,force_strength=10):
        super().__init__(x,y,w,h,color,stroke_thickness,stroke_color)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.force_strength = force_strength