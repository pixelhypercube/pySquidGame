from components.Color import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer

class Helper:
    def __init__(self):
        pass
    def render_text(self,frame,content,pos_x,pos_y,font_size=20,color=Color.WHITE):
        font = pg.font.Font("./assets/fonts/Inter-SemiBold.ttf",font_size)
        sentences = content.split("\n")
        x = pos_x
        y = pos_y
        for line in sentences:
            text = font.render(line,True,color)
            text_width,text_height = text.get_size()
            textRect = text.get_rect()
            textRect.center = (x,y-(len(sentences)-1)*text_height/2)
            frame.blit(text,textRect)
            y+=text_height

    def render_image(self,frame,path,pos_x,pos_y,size=None):
        image = pg.image.load(path)
        if size is not None:
            image = pg.transform.scale(image,(size[0]*2,size[1]*2))
        imageRect = image.get_rect()
        imageRect.center = (pos_x,pos_y)
        frame.blit(image,imageRect)

    def play_music(self,path):
        pg.mixer.music.load(path)
        pg.mixer.music.play(1)

    def play_sound(self,path):
        sound = pg.mixer.Sound(path)
        sound.play()