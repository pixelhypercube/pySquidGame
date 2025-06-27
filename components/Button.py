from components.Color import Color
from components.Helper import Helper
import pygame as pg
from Settings import WIDTH, HEIGHT
import time

helper = Helper()

class Button:
    def __init__(self,x,y,w,h,content="",font_size=20,color=Color.SQUID_PURPLE,hover_color=Color.SQUID_PURPLE2,clicked_color=Color.SQUID_PINK,text_color=Color.WHITE,next_screen=None,function=lambda:None,image_path=None,image_mode="fill",visible=True):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.content = content
        self.font_size = font_size

        self.color = color
        self.hover_color = hover_color
        self.clicked_color = clicked_color
        self.text_color = text_color

        self.current_color = self.color

        self.next_screen = next_screen
        self.function = function
        self.image_path = image_path
        self.image_mode = image_mode

        self.visible = visible
        self.last_click_time = 0

        self.prev_mouse_pressed_state = None
    
    def set_visibility(self, visible):
        self.visible = visible

    def on_default(self):
        self.current_color = self.color
    def on_hover(self):
        self.current_color = self.hover_color
    def on_mouseup(self,current_screen):
        now = time.time()
        if now-self.last_click_time>0.1 and self.prev_mouse_pressed_state:
            if self.function:
                self.function()
            self.last_click_time = now
        
        self.prev_mouse_pressed_state = pg.mouse.get_pressed()[0]
        return self.next_screen or current_screen
    def detect_mouseover(self,x,y):
        return x>=self.x-self.w and x<=self.x+self.w and y>=self.y-self.h and y<=self.y+self.h
    def click_listener(self,event,mouse_x,mouse_y,current_screen):
        if event.type==pg.MOUSEBUTTONDOWN:
            if self.detect_mouseover(mouse_x,mouse_y):
                self.prev_mouse_pressed_state = pg.mouse.get_pressed()[0]
                self.current_color = self.clicked_color
        elif event.type==pg.MOUSEBUTTONUP:
            if self.detect_mouseover(mouse_x,mouse_y):
                return self.on_mouseup(current_screen)
        return current_screen
    def render(self,frame):
        if self.visible:
            pg.draw.rect(frame,Color.BLACK,(self.x-self.w-3,self.y-self.h-3,self.w*2+6,self.h*2+6))
            pg.draw.rect(frame,self.current_color,(self.x-self.w,self.y-self.h,self.w*2,self.h*2))
            if self.image_path is not None:
                if self.image_mode=="fill":
                    helper.render_image(frame,self.image_path,self.x,self.y,size=[self.w,self.h])
                elif self.image_mode=="squeeze":
                    img = pg.image.load(self.image_path).convert_alpha()
                    img_rect = img.get_rect()
                    img_w, img_h = img_rect.width, img_rect.height

                    scale_factor = min((self.w*2)/img_w,(self.h*2)/img_h)
                    new_w = int(img_w*scale_factor)
                    new_h = int(img_h*scale_factor)
                    img = pg.transform.smoothscale(img,(new_w,new_h))

                    image_x = self.x-new_w//2
                    image_y = self.y-new_h//2
                    frame.blit(img,(image_x,image_y))
            helper.render_text(frame,self.content,self.x,self.y,font_size=self.font_size,color=self.text_color)
            if self.detect_mouseover(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
                if pg.mouse.get_pressed()[0]:
                    self.current_color = self.clicked_color
                else:
                    self.on_hover()
            else:
                self.on_default()