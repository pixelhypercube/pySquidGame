from components.Color import Color
from objects.ForceArea import ForceArea
import pygame as pg

class RadialForceArea(ForceArea):
    def __init__(self,x,y,w,h,color=Color.SAND_DARK,stroke_thickness=0,stroke_color=Color.SQUID_PURPLE,force_strength=1):
        super().__init__(x,y,w,h,color,stroke_thickness,stroke_color,force_strength)
        self.pos = [x,y]
        self.vel = [0,0]
        self.dim = [w,h]
    
    def render(self,frame):
        w,h = self.dim
        x,y = self.pos
        pg.draw.rect(frame,self.stroke_color,pg.Rect(x,y,w,h),width=self.stroke_thickness)

        gradient_surface = pg.Surface((w,h),pg.SRCALPHA)

        cx,cy = w//2,h//2
        max_radius = min(w,h)

        for r in range(max_radius,0,-1):
            alpha = int(255*(r/max_radius))
            color = (*self.color[:3],alpha)
            pg.draw.circle(gradient_surface,color,(cx,cy),r)
        
        frame.blit(gradient_surface,self.pos)
