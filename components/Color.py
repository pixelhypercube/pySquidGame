
import random
class Color:
    WHITE = (255,255,255)
    GREY = (127,127,127)
    DARK_GREY = (90,90,90)
    SQUID_PURPLE = (146,31,129)
    SQUID_PURPLE2 = (147,65,163)
    SQUID_PINK = (217,65,118)
    SQUID_GREY = (35,31,32)
    SQUID_TEAL = (55,161,142)
    SQUID_LIGHT_TEAL = (80,217,192)
    SAND = (243,231,179)
    RED = (255,40,0)
    YELLOW = (200,210,0)
    ORANGE = (185,105,0)
    GREEN = (0,127,50)
    BLUE = (0,50,255)
    PURPLE = (150,30,255)
    BLACK = (0,0,0)
    LIGHT_BLUE = (0,125,255)
    SKY_BLUE = (118,222,245)
    HONEYCOMB_YELLOW = (255, 200, 0)

    def get_color(r,g,b):
        return (r,g,b)
    def get_random_color():
        return (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    def get_random_color_from_base(base_color):
        r = (base_color[0] + random.randint(-20, 20)) % 256
        g = (base_color[1] + random.randint(-20, 20)) % 256
        b = (base_color[2] + random.randint(-20, 20)) % 256
        return (r, g, b)