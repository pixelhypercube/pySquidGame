from components.Color import Color
from components.Helper import Helper
from objects.Player import Player
from screens.GameHandler import GameHandler
import pygame as pg
import math
import random
import webbrowser
from threading import Timer
from Settings import WIDTH, HEIGHT

helper = Helper()

class RedLightGreenLight(GameHandler):
    def __init__(self, time=60, preparation_time=5, bg_color=Color.SAND,start_y=HEIGHT-100,finish_y=100,time_left=60,player_size=10):
        super().__init__(time, preparation_time, bg_color)
        self.players = []
        self.player = Player(WIDTH/2, HEIGHT/1.1, 10, Color.RED, max_speed=0.5, stroke_color=Color.BLACK)
        self.time_left = time_left*60
        self.start_y = start_y
        self.finish_y = finish_y
        self.player_size = player_size
        self.gen_players(30)
        
    def gen_players(self, num_players):
        for _ in range(num_players):
            x = random.randint(self.player_size, WIDTH-self.player_size)
            y = random.randint(self.start_y, HEIGHT)
            color = Color.get_random_color()
            self.players.append(Player(x, y, 10, color, max_speed=0.5, stroke_color=Color.BLACK))

    def render(self, frame,mouse_x, mouse_y):
        frame.fill(self.bg_color)
        for player in self.players:
            player.render(frame)
        
        self.player.render(frame)
        
        pg.draw.line(frame, Color.BLACK, (0, self.start_y), (WIDTH, self.start_y), 5)
        pg.draw.line(frame, Color.BLACK, (0, self.finish_y), (WIDTH, self.finish_y), 5)
        
        helper.render_text(frame,f"Time left: {self.time_left // 60}", WIDTH - 100, 20, font_size=20)
