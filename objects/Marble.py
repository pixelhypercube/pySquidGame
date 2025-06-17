from objects.Circle import Circle
from components.Color import Color
from threading import Timer
import random

class Marble(Circle):
    def __init__(self, x, y, r, color, max_speed=0.5, stroke_color=Color.BLACK,stroke_thickness=1):
        super().__init__(x, y, r, color, max_speed, stroke_color, stroke_thickness)