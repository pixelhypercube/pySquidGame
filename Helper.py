import Color
import pygame as pg
import math
import random
import webbrowser
from threading import Timer

class Helper:
    def __init__(self):
        pass
    def renderText(frame,content,posX,posY,fontSize=20,color=Color.white):
        font = pg.font.Font("./assets/fonts/Inter-SemiBold.ttf",fontSize)
        sentences = content.split("\n")
        x = posX
        y = posY
        for line in sentences:
            text = font.render(line,True,color)
            text_width,text_height = text.get_size()
            textRect = text.get_rect()
            textRect.center = (x,y-(len(sentences)-1)*text_height/2)
            frame.blit(text,textRect)
            y+=text_height

    def renderImage(frame,path,posX,posY,size=None):
        image = pg.image.load(path)
        if size is not None:
            image = pg.transform.scale(image,(size[0]*2,size[1]*2))
        imageRect = image.get_rect()
        imageRect.center = (posX,posY)
        frame.blit(image,imageRect)

    def playMusic(path):
        pg.mixer.music.load(path)
        pg.mixer.music.play(1)

    def playSound(path):
        sound = pg.mixer.Sound(path)
        sound.play()