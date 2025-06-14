from objects.Circle import Circle
from components.Color import Color

class Player(Circle):
    def __init__(self, x, y, r, color, max_speed=0.5, stroke_color=Color.BLACK):
        super().__init__(x, y, r, color, max_speed, stroke_color)