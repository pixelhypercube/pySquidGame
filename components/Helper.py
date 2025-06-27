from components.Color import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer

class Helper:
    def __init__(self):
        self.sounds = {}
        self.channels = {}
    def render_text(self,frame,content,pos_x,pos_y,font_size=20,color=Color.WHITE,align="center", underline=False):
        font = pg.font.Font("./assets/fonts/Inter-SemiBold.ttf",font_size)
        sentences = content.split("\n")
        x = pos_x
        y = pos_y
        for line in sentences:
            text = font.render(line,True,color)
            text_width,text_height = text.get_size()
            text_rect = text.get_rect()
            
            if align == "center":
                text_rect.center = (x, y - (len(sentences) - 1) * text_height / 2)
            elif align == "left":
                text_rect.midleft = (x, y - (len(sentences) - 1) * text_height / 2)
            elif align == "right":
                text_rect.midright = (x, y - (len(sentences) - 1) * text_height / 2)

            frame.blit(text,text_rect)

            if underline:
                underline_y = text_rect.bottom
                if align == "center":
                    start_x = text_rect.left
                    end_x = text_rect.right
                elif align == "left":
                    start_x = text_rect.left
                    end_x = text_rect.left + text_width
                elif align == "right":
                    start_x = text_rect.right - text_width
                    end_x = text_rect.right
                pg.draw.line(frame, color, (start_x, underline_y), (end_x, underline_y), 2)

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

    def play_sound(self,path,volume=1,continuous=False):
        if path not in self.sounds:
            self.sounds[path] = pg.mixer.Sound(path)
        
        sound = self.sounds[path]
        sound.set_volume(volume)

        if path not in self.channels:
            self.channels[path] = pg.mixer.find_channel()
        
        channel = self.channels[path]

        if channel is None: return

        if not channel.get_busy() or not continuous:
            channel.play(sound)