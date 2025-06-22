from components.Color import Color
from objects.Block import Block
import pygame as pg
class GlassBlock(Block):
    def __init__(self,x,y,w,h,color,stroke_thickness=2,stroke_color=Color.WHITE,breakable=False):
        super().__init__(x,y,w,h,color,stroke_thickness,stroke_color)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
        self.color = color
        self.stroke_thickness = stroke_thickness
        self.stroke_color = stroke_color
        self.breakable = breakable
        self.broken = False
    def render(self, frame):
        x,y = self.pos
        w,h = self.dim

        border_color = (*self.stroke_color[:3],120)
        pg.draw.rect(frame, border_color, pg.Rect(x,y,w,h), width=2, border_radius=0)

        glass_surface = pg.Surface((w,h),pg.SRCALPHA)
        glass_color = (*self.color[:3],100)
        glass_surface.fill(glass_color)
        frame.blit(glass_surface,(x,y))

        highlight_surface = pg.Surface((w,h),pg.SRCALPHA)
        pg.draw.line(highlight_surface,(*Color.WHITE,80),(5,5),(w//2,10),width=3)
        pg.draw.line(highlight_surface,(*Color.WHITE,40),(10,10),(w-10,10),width=1)
        frame.blit(highlight_surface,(x,y))
