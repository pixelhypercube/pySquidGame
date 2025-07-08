
import random
class Color:
    WHITE = (255,255,255)
    GREY = (127,127,127)
    LIGHT_GREY = (160,160,160)
    DARK_GREY = (90,90,90)
    DARK_DARK_GREY = (60,60,60)
    SQUID_PURPLE = (146,31,129)
    SQUID_PURPLE2 = (147,65,163)
    SQUID_PINK = (217,65,118)
    SQUID_GREY = (35,31,32)
    SQUID_TEAL = (55,161,142)
    SQUID_LIGHT_TEAL = (80,217,192)
    SAND = (243,231,179)
    SAND_DARK = (110,101,76)
    RED = (255,40,0)
    DARK_RED = (127,20,0)
    YELLOW = (200,210,0)
    ORANGE = (185,105,0)
    GREEN = (0,127,50)
    BLUE = (0,50,255)
    PURPLE = (150,30,255)
    BLACK = (0,0,0)
    LIGHT_BLUE = (0,125,255)
    SKY_BLUE = (118,222,245)
    HONEYCOMB_YELLOW = (255,200,0)
    HONEYCOMB_DARK_YELLOW = (127,100,0)
    STONE = (93,110,118)
    CARD_SAND = (202,170,128)

    def get_color(r,g,b):
        return (r,g,b)
    def get_random_color():
        return (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    def get_random_color_from_base(base_color):
        r = (base_color[0] + random.randint(-20, 20)) % 256
        g = (base_color[1] + random.randint(-20, 20)) % 256
        b = (base_color[2] + random.randint(-20, 20)) % 256
        return (r, g, b)
    def adj_color_brightness(base_color,percentage):
        r = min(255, base_color[0] * percentage)
        g = min(255, base_color[1] * percentage)
        b = min(255, base_color[2] * percentage)
        return (r, g, b)