import pygame as pg
import math
import random
import webbrowser
from threading import Timer

WIDTH = 800
HEIGHT = 600
running = True
currentScreen = "home"
frameCount = 0


# Test colors:
class Color:
    white = (255,255,255)
    grey = (127,127,127)
    dark_grey = (90,90,90)
    squid_purple = (146,31,129)
    squid_purple2 = (147,65,163)
    squid_pink = (217,65,118)
    squid_grey = (35,31,32)
    squid_teal = (55,161,142)
    squid_light_teal = (80,217,192)
    sand = (243,231,179)
    red = (255,40,0)
    yellow = (200,210,0)
    orange = (185,105,0)
    green = (0,127,50)
    blue = (0,50,255)
    purple = (150,30,255)
    black = (0,0,0)
    light_blue = (0,125,255)
    sky_blue = (118,222,245)

# The game
pg.init()
pg.font.init()
frame = pg.display.set_mode([WIDTH,HEIGHT])

mouseX = pg.mouse.get_pos()[0]
mouseY = pg.mouse.get_pos()[1]
mouseIsDown = pg.mouse.get_pressed()[0] == 1

pg.display.set_caption("pySquidGame")

def renderText(content,posX,posY,fontSize=20,color=Color.white):
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

def renderImage(path,posX,posY,size=None):
    image = pg.image.load(path)
    if size is not None:
        image = pg.transform.scale(image,(size[0]*2,size[1]*2))
    imageRect = image.get_rect()
    imageRect.center = (posX,posY)
    frame.blit(image,imageRect)

def playMusic(path):
    pg.mixer.music.load(path)
    pg.mixer.music.play(1)
    # sound = pg.mixer.Sound(path)
    # sound.play()
def playSound(path):
    sound = pg.mixer.Sound(path)
    sound.play()

def set_interval(func,seconds):
    def func_wrapper():
        set_interval(func,seconds)
        func()
    t = Timer(seconds,func_wrapper)
    t.start()
    return t

def time_int_format(time):
    return (str(time//60) if time//60>=10 else "0"+str(time//60))+":"+(str(time%60) if time%60 >= 10 else "0"+str(time%60))

# def open_url(path):
#     webbrowser.open(path)

class Circle:
    def __init__(self,x,y,r,color,is_player,vx=0,vy=0,max_speed=0.5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

        # Acceleration variables
        self.ax = 0
        self.ay = 0

        # Max speed variables
        self.max_speed = max_speed
        
        # Friction variable
        self.friction = 0.05

        self.r = r
        self.color = color

        # Is player
        self.is_player = is_player
    def show(self):
        pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r)+1)
        pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        # pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        # pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r),1)
        if self.is_player:
            pg.draw.polygon(frame,Color.red,((self.x,self.y-15),(self.x-10,self.y-25),(self.x+10,self.y-25)))
            pg.draw.polygon(frame,Color.black,((self.x,self.y-15),(self.x-10,self.y-25),(self.x+10,self.y-25)),1)
    def detectContact(self,xPos,yPos):
        distance = math.sqrt((self.x-xPos)**2+(self.y-yPos)**2)
        return distance<self.r*4
    def update(self):
        self.x+=self.vx
        self.y+=self.vy
        if (abs(self.vx) < self.max_speed):
            self.vx+=self.ax
        if (abs(self.vy) < self.max_speed):
            self.vy+=self.ay
        if self.x-self.r<=10 or self.x+self.r>=WIDTH-10:
            self.vx = -self.vx
            if self.x-self.r<=10:
                self.x = 10+self.r
            elif self.x+self.r>=WIDTH-10:
                self.x = WIDTH-10-self.r
        if self.y-self.r<=10 or self.y+self.r>=HEIGHT-10:
            self.vy = -self.vy
            if self.y-self.r<=10:
                self.y = 10+self.r
            elif self.y+self.r>=HEIGHT-10:
                self.y = HEIGHT-10-self.r
        self.vx/=(1+self.friction)
        self.vy/=(1+self.friction)
    def contactCircle(self,ball):
        distance = math.sqrt((self.x-ball.x)**2+(self.y-ball.y)**2)
        if (distance<ball.r+self.r):
            angle = math.atan2(self.y-ball.y,self.x-ball.x)
            self.vx += math.cos(angle)*0.4
            self.vy += math.sin(angle)*0.4
            ball.vx -= math.cos(angle)*0.4
            ball.vy -= math.sin(angle)*0.4
    def contactBlock(self,block):
        if (self.x+self.r+self.vx>block.x
        and self.x-self.r+self.vx<block.x+block.w
        and self.y+self.r>block.y
        and self.y<block.y+block.h):
            if self.vx<1.5:
                self.vx *= -1.3
            else:
                self.vx *= -0.6
        if (self.x+self.r>block.x
        and self.x<block.x+block.w
        and self.y+self.r+self.vy>block.y
        and self.y-self.r+self.vy<block.y+block.h):
            if self.vy<1.5:
                self.vy *= -1.3
            else:
                self.vy *= -0.6
                # type = 0 - default, 1 - marbles
    def contactForceArea(self,forceArea,type_no=0):
        if type_no==0:
            if (self.x+self.r>forceArea.x and self.x-self.r<forceArea.x+forceArea.w and self.y+self.r>forceArea.y and self.y-self.r<forceArea.y+forceArea.h):
                # print("Force area")
                if forceArea.direction=="left":
                    self.vx-=forceArea.strength
                if forceArea.direction=="right":
                    self.vx+=forceArea.strength
                if forceArea.direction=="up":
                    self.vy-=forceArea.strength
                if forceArea.direction=="down":
                    self.vy+=forceArea.strength
                if forceArea.direction=="radial":
                    angle = math.atan2(self.y-forceArea.y-forceArea.h/2,self.x-forceArea.x-forceArea.w/2)
                    self.vx-=forceArea.strength*math.cos(angle)
                    self.vy-=forceArea.strength*math.sin(angle)
        elif type_no==1:
            distance = math.sqrt((self.x-forceArea.x+forceArea.w/2)**2+(self.y-forceArea.y+forceArea.h/2)**2)
            if (min(forceArea.w,forceArea.h)>distance/1.8):
                if forceArea.direction=="radial":
                    angle = math.atan2(self.y-forceArea.y-forceArea.h/2,self.x-forceArea.x-forceArea.w/2)
                    self.vx-=forceArea.strength*math.cos(angle)
                    self.vy-=forceArea.strength*math.sin(angle)

# Used specifically for the 'Marbles' game

class Marble(Circle):
    def __init__(self, x, y, r, color, is_player, vx=0, vy=0, max_speed=0.5,player=1):
        super().__init__(x, y, r, color, is_player, vx, vy, max_speed)
        self.player = player # 1 - player 1, 2 - player 2

    def show(self):
        pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r)+1)
        pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        pg.draw.circle(frame,(86, 219, 115),(int(self.x+self.r/2-2),int(self.y-self.r/2+2)),int(self.r/2))
        # pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        # pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r),1)
        if self.is_player:
            pg.draw.polygon(frame,Color.red,((self.x,self.y-15),(self.x-10,self.y-25),(self.x+10,self.y-25)))
            pg.draw.polygon(frame,Color.black,((self.x,self.y-15),(self.x-10,self.y-25),(self.x+10,self.y-25)),1)

    # Check if the marble is in the hole
    def isInForceArea(self,forceArea):
        distance = math.sqrt((self.x-forceArea.x+forceArea.w/2)**2+(self.y-forceArea.y+forceArea.h/2)**2)
        return min(forceArea.w,forceArea.h)>distance/1.6
        # return self.x+self.r>forceArea.x+20 and self.x-self.r<forceArea.x+forceArea.w-20 and self.y+self.r>forceArea.y+20 and self.y-self.r<forceArea.y+forceArea.h-20

class Polygon:
    def __init__(self,x,y,w,h,coords,color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.coords = coords
        self.color = color
    def show(self):
        pg.draw.polygon(frame,self.color,self.coords)

class ForceArea:
    def __init__(self,x,y,w,h,strength,direction,shadeColor):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.strength = strength
        self.direction = direction
        self.shadeColor = shadeColor
        self.holePolygons = []
        self.fillHolePolygons(50,no_sides=[4,10])

    def fillHolePolygons(self,iterations,no_sides=[4,10]):
        for i in range(0,iterations):
            sides = random.randint(no_sides[0],no_sides[1])
            self.holePolygons.append(Polygon(self.x,self.y,self.w,self.h,[(math.cos((angle/sides)*2*math.pi*(random.random()*0.01+0.99))*(int(self.w/2)-i)+self.x+int(self.w/2),math.sin((angle/sides)*2*math.pi)*((self.h/2)-i)*(random.random()*0.01+0.99)+self.y+int(self.h/2)) for angle in range(0,sides)],(243-i,231-i,179-i)))


    def showHolePolygon(self):
        for polygon in self.holePolygons:
            polygon.show()
        # pg.draw.polygon(frame,(243-i,231-i,179-i),[(math.cos((angle/no_sides)*2*math.pi)*(self.w-i)+self.x+int(self.w/2),math.sin((angle/no_sides)*2*math.pi)*(self.h-i)+self.y+int(self.h/2)) for angle in range(0,no_sides)])

        # force_area_type prop = 0 - default 1 - hole (used in marbles game)
    def show(self,force_area_type=0):
        if force_area_type==0:
            pg.draw.rect(frame,self.shadeColor,(self.x,self.y,self.w,self.h))
        elif force_area_type==1:
            self.showHolePolygon()
            # for i in range(0,150):
            #     self.showHolePolygon()
                # pg.draw.circle(frame,(243-i,231-i,179-i),(int(self.x+self.w/2),int(self.y+self.h/2)),min(self.w,self.h)-i)
                # pg.draw.rect(frame,(243-i*1,231-i*1,179-i*1),(self.x+i*0.5,self.y+i*0.5,self.w-i*1,self.h-i*1))
        if self.direction=="left":
            # renderText("←",int(self.x+self.w/2),int(self.y+self.h/2),fontSize=50)
            pg.draw.rect(frame,Color.white,(self.x-frameCount%int(self.w/2-10)*2+self.w,self.y,10,self.h))
        elif self.direction=="right":
            # renderText("→",int(self.x+self.w/2),int(self.y+self.h/2),fontSize=50)
            pg.draw.rect(frame,Color.white,(self.x+frameCount%int(self.w/2-10)*2,self.y,10,self.h))
        elif self.direction=="up":
            # renderText("↑",int(self.x+self.w/2),int(self.y+self.h/2),fontSize=50)
            pg.draw.rect(frame,Color.white,(self.x,self.y-frameCount%int(self.h/2-10)*2,self.w,10))
        elif self.direction=="down":
            # renderText("↓",int(self.x+self.w/2),int(self.y+self.h/2),fontSize=50)
            pg.draw.rect(frame,Color.white,(self.x,self.y+frameCount%int(self.h/2-10)*2+self.h,self.w,10))
        elif self.direction=="radial":
            if force_area_type==0:
                pg.draw.circle(frame,Color.white,(int(self.x+self.w/2),int(self.y+self.h/2)),-(frameCount+i*10)%int(self.w/4))
                pg.draw.circle(frame,self.shadeColor,(int(self.x+self.w/2),int(self.y+self.h/2)),-(frameCount+i*10+5)%int(self.w/4))

class FootStep:
    def __init__(self,x,y,r,color,lifespan):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.lifespan = lifespan
    def show(self):
        pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r),1)
        self.lifespan-=1
    def detectLifespanOver(self):
        return self.lifespan<0
class Block:
    def __init__(self,x,y,w,h,color):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.w = w
        self.h = h
        self.color = color
    def show(self):
        pg.draw.rect(frame,self.color,(self.x,self.y,self.w,self.h))
    def update(self):
        self.x+=self.vx
        self.y+=self.vy

class Ddakji(Block):
    def __init__(self, x, y, w, h, color,rotation):
        super().__init__(x, y, w, h, color)

        self.vx = 0
        self.vy = 0

        self.friction = 0.05

        self.cooldown = 0

        # determines whether the ddakji is facing up or down
        # 0 - up 1 - down
        self.rotation = rotation

        # Changes to true after it's being flipped
        self.flipped = False

    def set_rotation(self,rotation):
        self.flipped = rotation!=self.rotation
        self.rotation = rotation



    def show(self):
        pg.draw.rect(frame,Color.black,(self.x-1,self.y-1,self.w+2,self.h+2))
        pg.draw.rect(frame,self.color,(self.x,self.y,self.w,self.h))
        if self.rotation==0:
            pg.draw.line(frame,Color.black,(self.x,self.y),(self.x+self.w,self.y+self.h))
            pg.draw.line(frame,Color.black,(self.x,self.y+self.h),(self.x+self.w,self.y))
    
    def intersect(self,player):
        return (self.x<player.x-self.w and self.x>player.x+player.w and self.y<player.y-self.h and self.y>player.y+player.h)

    def update(self):
        
        self.vx/=(1+self.friction)
        self.vy/=(1+self.friction)

        if self.cooldown>0:
            self.x+=self.vx
            self.y+=self.vy
            self.cooldown-=1

    # When the player holds a ddakji

    def hold(self,x_pos,y_pos):
        self.x = int(x_pos-self.w/2)
        self.y = int(y_pos-self.h/2)

        # Filling the gradient below
        pg.draw.rect(frame,[50,50,50],(self.x+10,self.y+10,self.w,self.h))
            
        # Then filling the ddakji
        pg.draw.rect(frame,Color.black,(self.x-1,self.y-1,self.w+2,self.h+2))
        pg.draw.rect(frame,self.color,(self.x,self.y,self.w,self.h))

    # When player throws ddakji

    def throw(self,player):
        # detect if self and other player intersect
        if self.x<player.x+player.w and self.x>player.x-self.w and self.y<player.y+player.h and self.y>player.y-self.h:
            
            player.cooldown = 50
            angle = math.atan2((player.y-player.h/2)-(self.y-self.h/2),(player.x-player.w/2)-(self.x-self.w/2))
            distance = math.sqrt(abs((player.y-player.h/2)-(self.y-self.h/2))**2+abs((player.x-player.w/2)-(self.x-self.w/2))**2)

            # Calculates the distance to middle of edge
            # print((random.random()*distance)*1.2/distance)

            player.set_rotation(int((random.random()*distance)*1.2/distance))
            player.vx = math.cos(angle)
            player.vy = math.sin(angle)
        


class Button:
    def __init__(self,x,y,w,h,color,hoverColor,clickedColor,textColor,content,screen=None,function=None,image_path=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.hoverColor = hoverColor
        self.clickedColor = clickedColor
        self.textColor = Color.white
        self.currentColor = self.color
        self.content = content
        self.screen = screen
        self.function = function
        self.image_path = image_path
        self.visible = False
    def onDefault(self):
        self.currentColor = self.color
    def onHover(self):
        self.currentColor = self.hoverColor
    def onClick(self):
        global currentScreen
        global gameScreen
        # self.currentColor = self.clickedColor
        if self.screen!=None:
            currentScreen = self.screen
            if (currentScreen=="redLightGreenLight"):
                gameScreen = RedLightGreenLight(100,5,Color.sand,500,100)
            elif currentScreen=="marbles":
                gameScreen = MarblesGame(100,5,Color.sand,100)
            elif currentScreen=="ddakji":
                gameScreen = DdakjiGame(100,5,Color.sand,100)
            else:
                gameScreen = GameScreen()
        else:
            self.function()
        # for i in range(1,11):
        #     if (self.screen=="level"+str(i)):
        #         gameScreen.setLevel(i)
    def setVisibility(self,visible):
        self.visible = visible
    def detect_mouseover(self,x,y):
        return x>=self.x-self.w and x<=self.x+self.w and y>=self.y-self.h and y<=self.y+self.h
    def click(self,event):
        global mouseIsDown
        global mouseX
        global mouseY
        if event.type==pg.MOUSEBUTTONDOWN:
            if self.detect_mouseover(mouseX,mouseY):
                self.currentColor = self.clickedColor
        elif event.type==pg.MOUSEBUTTONUP:
            if self.detect_mouseover(mouseX,mouseY):
                self.onClick()
        # else:
        #     self.onDefault()
    def show(self):
        self.setVisibility(True)
        if self.visible==True:
            pg.draw.rect(frame,Color.black,(self.x-self.w-3,self.y-self.h-3,self.w*2+6,self.h*2+6))
            pg.draw.rect(frame,self.currentColor,(self.x-self.w,self.y-self.h,self.w*2,self.h*2))
            if self.image_path is not None:
                renderImage(self.image_path,self.x,self.y,size=[self.w,self.h])
            renderText(self.content,self.x,self.y)
            if self.detect_mouseover(mouseX,mouseY):
                if pg.mouse.get_pressed()[0]:
                    self.currentColor = self.clickedColor
                else:
                    self.onHover()
            else:
                self.onDefault()
                
                # for event in pg.event.get():
                #     if event.type == pg.MOUSEBUTTONDOWN:
                #         self.onClick()
                #     else:
                #         self.onHover()
                    
                    # Old method

                    # if event.type == pg.MOUSEBUTTONUP:
                    #     self.onClick()
                    # elif event.type == pg.MOUSEBUTTONDOWN:
                    #     self.currentColor = self.clickedColor
                    # else:
                    #     self.onHover()

                # if (mouseIsDown):
                #     self.onClick()
                # else:
                #     self.onHover()
            

class GameScreen:
    def __init__(self):
        global currentScreen
        # self.playBtn = Button(WIDTH/2,HEIGHT/1.5,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Start Game!","levels")
        self.playBtn = Button(WIDTH/2,HEIGHT/1.35,90,50,Color.white,Color.white,Color.white,Color.white,"",screen="levels")
        self.backBtn = Button(80,HEIGHT/5,50,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Back","home")
        self.levelBackBtn = Button(80,HEIGHT/8,50,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Back","levels")
        self.startBtn = Button(WIDTH/2,HEIGHT/1.33,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Start!",currentScreen[:-4])
        self.linkBtn = Button(WIDTH/2,HEIGHT/1.1,120,30,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Github Link!\n(Opens new window)",function=lambda :webbrowser.open("https://github.com/pixelhypercube/pySquidGame"))
        self.returnLvlsBtn = Button(WIDTH/2,HEIGHT/1.6,100,30,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Go back","levels")
        self.lvlNumBtns = []
        self.blocks = []
        self.forceAreas = []
        self.balls = []
        self.gameNames = ["Red Light,\n Green Light","Honeycomb \n(Coming Soon!)","Tug Of War \n(Coming Soon!)","Marbles \n(Coming Soon!)","Glass Stepping\n Stones \n(Coming Soon!)","Squid Game \n(Coming Soon!)"]
        self.gameImageNames = ["redLightGreenLight","honeyComb","tugOfWar","marbles","glassSteppingStones","squidGame"]
        for i in range(1,4):
            if i==1:
                self.lvlNumBtns.append(Button(i*200,(HEIGHT/2)+30,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen=self.gameImageNames[i-1]+"Help",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
            else:
                self.lvlNumBtns.append(Button(i*200,(HEIGHT/2)+30,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen="levels",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
        for i in range(4,7):
            if i==4:
                self.lvlNumBtns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen=self.gameImageNames[i-1]+"Help",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
            else:
                self.lvlNumBtns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen="levels",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
        self.lvlNumBtns.append(Button(WIDTH-100,(HEIGHT/4),40,20,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Ddakji",screen="ddakjiHelp",function=None))
        self.player = Circle(50,HEIGHT/2,8,Color.white,True,max_speed=0.5)
        # self.hole = Hole(550,250,15,Color.black)
        self.lvlTxt = []
        # self.strokes = 0
        # self.par = 0
        # self.currentLevel = 0
        self.paused = False

        self.won = False

        # # Game objects
        # self.redLightGreenLight = RedLightGreenLight(100,5,Color.sand,500,100)
    def showHome(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderImage("./assets/img/titleLogo.png",WIDTH/2,HEIGHT/3)
        # renderText("Py",WIDTH/2,HEIGHT/4,fontSize=40)
        renderText("(beta)",WIDTH/3.5,HEIGHT/2.5,fontSize=32)
        renderText("By PixelHyperCube!",WIDTH/2,HEIGHT/1.9,fontSize=24)
        renderText("Made using pygame!",WIDTH/2,HEIGHT/1.7,fontSize=15)
        if mouseX>=WIDTH/2-90 and mouseX<=WIDTH/2+90 and mouseY>=HEIGHT/1.35-50 and mouseY<=HEIGHT/1.35+50:
            renderImage("./assets/img/invitationBack1.png",WIDTH/2,HEIGHT/1.35)
        else:
            renderImage("./assets/img/invitationFront.png",WIDTH/2,HEIGHT/1.35)
        # self.playBtn.show()

        # For debugging
        self.linkBtn.show()
    def showLevelScreen(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderText("Choose a stage!",WIDTH/2,HEIGHT/5,fontSize=40)
        # renderText("Left-click the mouse and drag to adjust strength",WIDTH/2,180,fontSize=15)
        # renderText("Then release it to hit the ball!",WIDTH/2,200,fontSize=15)
        renderText("Press 'Esc' or 'P' to pause",WIDTH/2,220,fontSize=15)
        self.backBtn.show()
        for btn in self.lvlNumBtns:
            btn.show()
    def showSuccessScreen(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderText("Success!",WIDTH/2,HEIGHT/3,fontSize=40)
        renderText("Thanks a lot for playing! Since this program is in beta,",WIDTH/2,HEIGHT/2.4,fontSize=20)
        renderText("there are 4 games are currently in progress!",WIDTH/2,HEIGHT/2.1,fontSize=20)
        self.returnLvlsBtn.show()
    def showFailureScreen(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderText("Eliminated :(",WIDTH/2,HEIGHT/3,fontSize=40)
        renderText("The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,fontSize=20)
        renderText(" by clicking the 'Go back' button! :)",WIDTH/2,HEIGHT/2.1,fontSize=20)
        self.returnLvlsBtn.show()
    def showHelpScreen(self):
        global currentScreen
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        if currentScreen=="redLightGreenLightHelp":
            renderText("How to play:",WIDTH/2,HEIGHT/12,fontSize=40)
            renderText("Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,fontSize=20)
            renderImage("./assets/img/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
            renderText("When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,fontSize=20)
            renderText("Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,fontSize=20)
            renderText("Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,fontSize=20)
            renderText("Repeatedly press W if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,fontSize=20)
        elif currentScreen=="marblesHelp":
            # Change these
            renderText("How to play:",WIDTH/2,HEIGHT/12,fontSize=40)
            renderText("Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,fontSize=20)
            renderImage("./assets/img/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
            renderText("When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,fontSize=20)
            renderText("Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,fontSize=20)
            renderText("Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,fontSize=20)
            renderText("Repeatedly press W if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,fontSize=20)
        elif currentScreen=="ddakjiHelp":
            # Change these
            renderText("How to play:",WIDTH/2,HEIGHT/12,fontSize=40)
            renderText("Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,fontSize=20)
            renderImage("./assets/img/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
            renderText("When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,fontSize=20)
            renderText("Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,fontSize=20)
            renderText("Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,fontSize=20)
            renderText("Repeatedly press W if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,fontSize=20)
        self.levelBackBtn.show()
        self.startBtn.show()
    # def showRedLightGreenLightScreen(self):
        # gameScreen = RedLightGreenLight()
        # pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        # self.redLightGreenLight.show()

class Game:
    def __init__(self,time,preparation_time,bg_color):
        self.time = time
        self.preparation_time = preparation_time
        self.bg_color = bg_color
        self.inGameFrameCount = 0
    def showPrepScreen(self,timeLeft):
        pg.draw.rect(frame,Color.squid_grey,(WIDTH/2-80,HEIGHT/4-30,160,80))
        renderText("Get ready in",WIDTH/2,HEIGHT/4-10,fontSize=20)
        renderText(str(timeLeft),WIDTH/2,HEIGHT/4+20,fontSize=30)



class RedLightGreenLight(Game):
    def __init__(self,time,preparation_time,bg_color,start_y,finish_y,timeLeft=60):
        super().__init__(time,preparation_time,bg_color)
        self.timeLeft = timeLeft*60
        self.paused = False
        self.players = []
        self.start_y = start_y
        self.finish_y = finish_y
        self.player = Circle(random.randint(0,WIDTH),self.start_y+random.randint(0,200),8,Color.squid_light_teal,True,max_speed=0.5)
        self.redGreenInterval = 4.8
        self.scanDurationTime = 0.7
        self.intervalDurationLeft = self.redGreenInterval*60
        self.isRedLight = False
        self.wall_blocks = [
            Block(0,0,WIDTH,8,Color.sky_blue),
            Block(0,0,10,HEIGHT,Color.sky_blue),
            Block(0,HEIGHT-10,WIDTH,8,Color.sky_blue),
            Block(WIDTH-10,0,10,HEIGHT,Color.sky_blue),
        ]
        # self.resumeBtn = Button(WIDTH/2,HEIGHT/2,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Resume Game",screen=None,function=self.togglePause(not self.paused))
        self.restartBtn = Button(WIDTH/2,HEIGHT/2,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Restart Game",screen="redLightGreenLight")
        self.exitBtn = Button(WIDTH/2,HEIGHT/2+75,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Exit Game",screen="levels")
        self.genCircles(50)

        # Footsteps list
        self.footsteps = []

        # 'Terminal' player max speed
        self.terminalMaxSpeed = 0.35

        # Variable to count the number of times 'W' was pressed
        self.wPressedCount = 0

        self.footstepTimeObj = None


    def genCircles(self,count):
        for i in range(0,count):
            xPos = random.randint(30,WIDTH-30)
            yPos = self.start_y+random.randint(0,100)
            self.players.append(Circle(xPos,yPos,8,Color.squid_teal,False,max_speed=random.random()*0.2+0.15))
    def accelerate_player(self,player,ax,ay):
        player.ax = ax
        player.ay = ay
    def toggle_light(self):
        self.isRedLight = not self.isRedLight
        self.intervalDurationLeft = self.redGreenInterval*60
        if not self.isRedLight:
            playMusic("./assets/sounds/greenLight.wav")
        else:
            playMusic("./assets/sounds/changeLight.wav")
            t = Timer(0.5,lambda : playMusic("./assets/sounds/scanning.wav"))
            t.start()
    
    # def generate_footstep(self,player):
    #     self.footsteps.append(FootStep(int(player.x),int(player.y),int(player.r/4),Color.black,40))

    def show(self):
        global running
        global gameScreen
        global currentScreen
        if not self.paused:
            pg.draw.rect(frame,self.bg_color,(0,0,WIDTH,HEIGHT))
            renderText(time_int_format(int(self.timeLeft/60)),WIDTH/2,HEIGHT/2,fontSize=50,color=Color.black)
            if self.timeLeft<0:
                gameScreen = GameScreen()
                currentScreen="fail"
                pg.mixer.music.stop()
                playMusic("./assets/sounds/gunShotLong.wav")
            pg.draw.rect(frame,Color.red,(0,self.start_y,WIDTH,10))
            pg.draw.rect(frame,Color.red,(0,self.finish_y,WIDTH,10))
            if self.isRedLight or (self.preparation_time*60-self.inGameFrameCount>0):
                renderImage("./assets/img/dollFront.png",WIDTH/2,HEIGHT/12,[40,40])
            else:
                renderImage("./assets/img/dollBack.png",WIDTH/2,HEIGHT/12,[40,40])
            for wall_block in self.wall_blocks:
                wall_block.show()
            if (self.preparation_time*60-self.inGameFrameCount>0):
                self.showPrepScreen(int((self.preparation_time*60-self.inGameFrameCount)/60)+1)
                for player in self.players:
                    for player1 in self.players:
                        player1.friction=10
                        player1.contactCircle(player)
                    # player.contactCircle(self.player)
                    player.friction = 10
                    if player.y<=self.start_y:
                        player.y == self.start_y
                    self.player.contactCircle(player)
                # self.player.friction = 10
                if self.player.y<=self.start_y:
                    self.player.y = self.start_y
            elif (self.preparation_time*60-self.inGameFrameCount==0):
                playMusic("./assets/sounds/greenLight.wav")
            else:
                self.timeLeft -= 1
                for player in self.players:
                    velocity = math.sqrt(abs(player.vx)**2+abs(player.vy)**2)
                    if not self.isRedLight:
                        if player.y<=self.finish_y:
                            self.accelerate_player(player,0,0)
                        else:
                            self.accelerate_player(player,random.random()*0.1-0.05,-random.random()*0.5)
                    else:
                        if self.footstepTimeObj != None:
                            self.footstepTimeObj.cancel()

                        # Reset player's max speed
                        self.player.max_speed = 0.25
                        if velocity>0.099999 and player.y>=self.finish_y and self.intervalDurationLeft<=self.redGreenInterval*60-self.scanDurationTime*60:
                            self.players.remove(player)
                            playSound("./assets/sounds/gunShot.wav")
                        if player.y>=self.finish_y:
                            self.accelerate_player(player,0,0)
                            # Circles shivering
                            if random.random()<0.025:
                                player.vx = random.random()*0.18-0.09
                                player.vy = random.random()*0.18-0.09
                    for player1 in self.players:
                        # player1.friction = 0.25
                        player1.contactCircle(player)
                    player.friction = 0.1
                    self.player.contactCircle(player)
                self.player.friction = 0.1
                self.intervalDurationLeft-=1
                player_velocity = math.sqrt(abs(self.player.vx)**2+abs(self.player.vy)**2)
                if self.isRedLight and player_velocity>0.099999 and self.intervalDurationLeft<=self.redGreenInterval*60-self.scanDurationTime*60:
                    gameScreen = GameScreen()
                    currentScreen="fail"
                    pg.mixer.music.stop()
                    playMusic("./assets/sounds/gunShotLong.wav")
                if self.player.y<self.finish_y:
                    gameScreen = GameScreen()
                    pg.mixer.music.stop()
                    currentScreen="success"
            if self.intervalDurationLeft<=0:
                self.toggle_light()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    # self.footstepTimeObj.cancel()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        self.player.ay = -random.random()*0.25
                        # self.wPressedCount+=1
                        # if self.wPressedCount==2:
                        #     self.footstepTimeObj = set_interval(lambda: self.footsteps.append(FootStep(int(self.player.x+random.random()*0.1-0.05),int(self.player.y),int(self.player.r/3),Color.black,40)),0.25)
                        if self.player.max_speed<self.terminalMaxSpeed:
                            self.player.max_speed += 0.005
                    elif event.key == pg.K_a:
                        self.player.ax = -random.random()*0.25
                    elif event.key == pg.K_s:
                        self.player.ay = random.random()*0.25
                    elif event.key == pg.K_d:
                        self.player.ax = random.random()*0.25
                    elif event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            pg.mixer.music.pause()
                        self.player.ax = 0
                        self.player.ay = 0
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_w:
                        self.player.ay = 0
                    elif event.key == pg.K_a:
                        self.player.ax = 0
                    elif event.key == pg.K_s:
                        self.player.ay = 0
                    elif event.key == pg.K_d:
                        self.player.ax = 0

            # for footstep in self.footsteps:
            #     footstep.show()
            #     if footstep.detectLifespanOver():
            #         self.footsteps.remove(footstep)
            for player in self.players:
                player.show()
                player.update()
            self.player.show()
            self.player.update()
            self.inGameFrameCount += 1
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    print("Quitting game...")
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        pg.mixer.music.unpause()
            pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
            renderText("Paused",WIDTH/2,HEIGHT/3,fontSize=40)
            renderText("Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,fontSize=20)
            self.restartBtn.show()
            self.exitBtn.show()

class MarblesGame(Game):
    def __init__(self, time, preparation_time, bg_color,timeLeft=60):
        super().__init__(time, preparation_time, bg_color)
        self.timeLeft = timeLeft*60
        self.blocks = []
        self.wallBlocks = [
            Block(0,0,WIDTH,10,Color.grey),
            Block(0,0,10,HEIGHT,Color.grey),
            Block(0,HEIGHT-10,WIDTH,10,Color.grey),
            Block(WIDTH-10,0,10,HEIGHT,Color.grey),
        ]
        self.forceAreas = [
            ForceArea(WIDTH/2-75,HEIGHT/3.5-50,150,150,0.5,"radial",Color.squid_light_teal)
        ]
        self.marbles = []
        self.lvlTxt = []
        self.tempMarble = Marble(WIDTH/2,HEIGHT/1.2,10,Color.green,False,max_speed=10)
        # self.strokes = 0
        # self.par = 0
        # self.currentLevel = 0
        self.paused = False
        self.restartBtn = Button(WIDTH/2,HEIGHT/2,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Restart Game",screen="redLightGreenLight")
        self.exitBtn = Button(WIDTH/2,HEIGHT/2+75,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Exit Game",screen="levels")
    
        self.player_turn = 1 # 1 - player's turn 2 - CPU's turn

    # def checkMarblesMoving(self):
    #     self.moving = [abs(marble.vx)<0.1 and abs(marble.vy)<0.1 for marble in self.marbles]
    #     return all(self.moving)

    # Relative to self.tempMarble's position

    def getXPosList(self,distance,angle):
        return distance*math.cos(angle)
    
    def getYPosList(self,distance,angle):
        return distance*math.sin(angle)

    def shootCPUPlayer(self):

        # Special usage of all of the marbles in the selected area (making it smarter)

        # x_min = 1
        # x_max = 2
        # y_min = 2
        # y_max = 2

        # distances = list(map(lambda marble:0.1*math.sqrt((marble.x-self.tempMarble.x)**2+(marble.y-self.tempMarble.y)**2),self.marbles))
        # angles = list(map(lambda marble:math.atan2(marble.y-self.tempMarble.y,marble.x-self.tempMarble.x),self.marbles))

        if len(self.marbles)>0:
            # x_positions = list(map(lambda marble:self.getXPosList(0.1*math.sqrt((marble.x-self.tempMarble.x)**2+(marble.y-self.tempMarble.y)**2),math.atan2(marble.y-self.tempMarble.y,marble.x-self.tempMarble.x)),self.marbles))
            # y_positions = list(map(lambda marble:self.getYPosList(0.1*math.sqrt((marble.x-self.tempMarble.x)**2+(marble.y-self.tempMarble.y)**2),math.atan2(marble.y-self.tempMarble.y,marble.x-self.tempMarble.x)),self.marbles))

            # print(x_positions)
            # print(y_positions)

            # x_min = min(x_positions)*0.25
            # x_max = max(x_positions)*0.25
            # y_min = min(y_positions)*0.25
            # y_max = max(y_positions)*0.25

            # self.marbles.append(Marble(self.tempMarble.x,self.tempMarble.y,self.tempMarble.r,self.tempMarble.color,False,vx=random.random()*(x_max-x_min if len(x_positions)>1 else x_max),vy=random.random()*(y_max-y_min if len(y_positions)>1 else y_max),max_speed=10,player=2))
            self.marbles.append(Marble(self.tempMarble.x,self.tempMarble.y,self.tempMarble.r,(0+random.randint(0,60),127+random.randint(-30,30),50+random.randint(-30,30)),False,vx=random.random()*4-2,vy=-random.random()*8-2,max_speed=10,player=2))

    def showType1(self):
        global running
        global currentScreen
        global gameScreen
        if not self.paused:
            pg.draw.rect(frame,self.bg_color,(0,0,WIDTH,HEIGHT))
            for forceArea in self.forceAreas:
                forceArea.show(force_area_type=1)
                for marble in self.marbles:
                    marble.contactForceArea(forceArea,type_no=1)

                    if marble.isInForceArea(forceArea) and marble.vx<0.05 and marble.vy<0.05:
                        if marble.player==1:
                            gameScreen = GameScreen()
                            pg.mixer.music.stop()
                            currentScreen="success"
                        elif marble.player==2:
                            gameScreen = GameScreen()
                            currentScreen="fail"
                            pg.mixer.music.stop()
                            playMusic("./assets/sounds/gunShotLong.wav")
                    
            if self.player_turn==1:
                renderText("Your turn!",WIDTH//2,HEIGHT-25,fontSize=20,color=Color.black)
            elif self.player_turn==2:
                renderText("CPU's turn!",WIDTH//2,HEIGHT-25,fontSize=20,color=Color.black)
            
            for marble in self.marbles:
                marble.show()
                marble.update()
                for marble1 in self.marbles:
                    marble.contactCircle(marble1)
            self.tempMarble.show()

            # Check if all the marbles are not moving
            if all([abs(marble.vx)<0.1 and abs(marble.vy)<0.1 for marble in self.marbles]):
                if self.player_turn==2:   
                    self.shootCPUPlayer()
                    self.player_turn = 1

            if mouseIsDown and self.player_turn==1:
                distance = 0.1*math.sqrt((mouseX-self.tempMarble.x)**2+(mouseY-self.tempMarble.y)**2)
                if distance<10:
                    pg.draw.line(frame,[55+int(distance*20),250-int(distance*25),0],(self.tempMarble.x,self.tempMarble.y),(mouseX,mouseY),int(distance/2)+1)
                else:
                    angle = math.atan2(self.tempMarble.y-mouseY,self.tempMarble.x-mouseX)
                    pg.draw.line(frame,[255,0,0],(self.tempMarble.x,self.tempMarble.y),(self.tempMarble.x-100*math.cos(angle),self.tempMarble.y-100*math.sin(angle)),6)
            for event in pg.event.get():
                if event.type==pg.QUIT:
                    print("Quitting game...")
                    running = False
                if event.type==pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            pg.mixer.music.pause()
                elif event.type==pg.MOUSEBUTTONUP:
                    if self.player_turn==1:
                        distance = 0.1*math.sqrt((mouseX-self.tempMarble.x)**2+(mouseY-self.tempMarble.y)**2)
                        angle = math.atan2(self.tempMarble.y-mouseY,self.tempMarble.x-mouseX)
                        vx = 0
                        vy = 0
                        if distance<10:
                            vx = distance*math.cos(angle)
                            vy = distance*math.sin(angle)
                        else:
                            vx = 10*math.cos(angle)
                            vy = 10*math.sin(angle)
                        self.marbles.append(Marble(self.tempMarble.x,self.tempMarble.y,self.tempMarble.r,(0+random.randint(0,60),127+random.randint(-30,30),50+random.randint(-30,30)),False,vx=vx,vy=vy,max_speed=10,player=1))
                        
                        self.player_turn = 2
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    print("Quitting game...")
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        pg.mixer.music.unpause()
            pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
            renderText("Paused",WIDTH/2,HEIGHT/3,fontSize=40)
            renderText("Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,fontSize=20)
            self.restartBtn.show()
            self.exitBtn.show()

class DdakjiGame(Game):
    def __init__(self,time,preparation_time,bg_color,timeLeft=60):
        super().__init__(time,preparation_time,bg_color)
        self.paused = False
        self.timeLeft = timeLeft*60
        self.restartBtn = Button(WIDTH/2,HEIGHT/2,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Restart Game",screen="redLightGreenLight")
        self.exitBtn = Button(WIDTH/2,HEIGHT/2+75,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Exit Game",screen="levels")

        self.player = Ddakji(WIDTH/2,HEIGHT/2,50,50,Color.blue,0)
        self.cpu = Ddakji(WIDTH/2+100,HEIGHT/2+100,50,50,Color.red,0)

        # 1 - player, 2 - cpu, 0 - waiting
        self.player_turn = 1

    def show(self):
        global running
        global currentScreen
        global gameScreen
        global mouseX
        global mouseY
        if not self.paused:
            pg.draw.rect(frame,self.bg_color,(0,0,WIDTH,HEIGHT))

            if self.player_turn==1:
                self.cpu.show()
                self.player.show()
            elif self.player_turn==2:
                self.player.show()
                self.cpu.show()
            elif self.player_turn==0:
                if self.player.cooldown>0:
                    self.player.show()
                    self.cpu.show()
                elif self.cpu.cooldown>0:
                    self.cpu.show()
                    self.player.show()

            self.player.update()
            self.cpu.update()

            next_player = 0

            if self.player_turn==1:
                self.player.hold(mouseX,mouseY)
            elif self.player_turn==2:

                if self.cpu.flipped:
                    gameScreen = GameScreen()
                    pg.mixer.music.stop()
                    currentScreen="success"

                self.cpu.x = random.randint(self.player.x,self.player.x+self.player.w)
                self.cpu.y = random.randint(self.player.y,self.player.y+self.player.h)
                self.cpu.throw(self.player)
                self.player_turn = 0
            elif self.player_turn==0:
                if self.cpu.cooldown==1:
                    self.player_turn = 2
                elif self.player.cooldown==2:
                    self.player_turn = 1


            # Check if both cooldowns are 0

            if self.cpu.cooldown<=0 and self.player.cooldown<=0:
                if self.cpu.flipped:
                    gameScreen = GameScreen()
                    pg.mixer.music.stop()
                    currentScreen="success"
                elif self.player.flipped:
                    gameScreen = GameScreen()
                    currentScreen="fail"
                    pg.mixer.music.stop()
                    playMusic("./assets/sounds/gunShotLong.wav")

                # if self.cpu.cooldown<=0 and self.player.cooldown<=0:
                #     self.player_turn = next_player

            # if self.:
            #     gameScreen = GameScreen()
            #     currentScreen="fail"
            #     pg.mixer.music.stop()
            #     playMusic("./assets/sounds/gunShotLong.wav")
            # if :
            #     gameScreen = GameScreen()
            #     pg.mixer.music.stop()
            #     currentScreen="success"

            # if self.player_turn==1:
            #     self.player.hold(mouseX,mouseY)
            # elif self.player_turn==0:
            #     if self.cpu.cooldown>=0:
            #         next_player = 1
            #     elif self.player.cooldown>=0:
            #         next_player = 2
            #     if self.cpu.cooldown<=0 and self.player.cooldown<=0:
            #         self.player_turn = next_player
            # elif self.player_turn==2:
            #     self.cpu.throw(self.player)
            #     self.player_turn=0

            for event in pg.event.get():
                if event.type==pg.QUIT:
                    print("Quitting game...")
                    running = False
                if event.type==pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            pg.mixer.music.pause()
                elif event.type==pg.MOUSEBUTTONDOWN:
                    if self.player_turn==1:
                        self.player.throw(self.cpu)
                        self.player_turn=0

                # elif event.type==pg.MOUSEBUTTONUP:
                #     if self.player_turn==1:
                #         distance = 0.1*math.sqrt((mouseX-self.tempMarble.x)**2+(mouseY-self.tempMarble.y)**2)
                #         angle = math.atan2(self.tempMarble.y-mouseY,self.tempMarble.x-mouseX)
                #         vx = 0
                #         vy = 0
                #         if distance<10:
                #             vx = distance*math.cos(angle)
                #             vy = distance*math.sin(angle)
                #         else:
                #             vx = 10*math.cos(angle)
                #             vy = 10*math.sin(angle)
                #         self.marbles.append(Marble(self.tempMarble.x,self.tempMarble.y,self.tempMarble.r,(0+random.randint(0,60),127+random.randint(-30,30),50+random.randint(-30,30)),False,vx=vx,vy=vy,max_speed=10,player=1))
                        
                #         self.player_turn = 2
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    print("Quitting game...")
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE or event.key == pg.K_p:
                        self.paused = not self.paused
                        pg.mixer.music.unpause()
            pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
            renderText("Paused",WIDTH/2,HEIGHT/3,fontSize=40)
            renderText("Press 'Esc' or 'P' to resume game!",WIDTH/2,HEIGHT/2.5,fontSize=20)
            self.restartBtn.show()
            self.exitBtn.show()
    
gameScreen = GameScreen()

clock = pg.time.Clock()

while running:
    clock.tick(60)
    # print(clock.get_fps())
    mouseX = pg.mouse.get_pos()[0]
    mouseY = pg.mouse.get_pos()[1]
    mouseIsDown = pg.mouse.get_pressed()[0] == 1
    if (currentScreen=="home"):
        gameScreen.showHome()
    if (currentScreen=="levels"):
        gameScreen.showLevelScreen()
    if (currentScreen=="success"):
        gameScreen.showSuccessScreen()
    if (currentScreen=="fail"):
        gameScreen.showFailureScreen()
    if (currentScreen=="redLightGreenLightHelp" 
    or currentScreen=="marblesHelp" or currentScreen=="ddakjiHelp"):
        gameScreen.showHelpScreen()
    if (currentScreen=="redLightGreenLight"):
        if type(gameScreen).__name__=="RedLightGreenLight":
            gameScreen.show()
    if (currentScreen=="marbles"):
        if type(gameScreen).__name__=="MarblesGame":
            # Leaving type1 at the moment - will add in more styles!
            gameScreen.showType1()
    if (currentScreen=="ddakji"):
        if type(gameScreen).__name__=="DdakjiGame":
            gameScreen.show()
        # gameScreen.showRedLightGreenLightScreen()
    for i in range(1,11):
        if (currentScreen=="level"+str(i)):
            gameScreen.showLevel()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            print("Quitting game...")
            running = False
        if (type(gameScreen).__name__=="GameScreen"):
            if currentScreen=="home":
                gameScreen.playBtn.click(event)
                gameScreen.linkBtn.click(event)
            if currentScreen=="levels":
                gameScreen.backBtn.click(event)
                for lvlBtn in gameScreen.lvlNumBtns:
                    lvlBtn.click(event)
            if currentScreen=="redLightGreenLightHelp" or currentScreen=="marblesHelp" or currentScreen=="ddakjiHelp":
                gameScreen.levelBackBtn.click(event)
                gameScreen.startBtn.click(event)
            if currentScreen=="success":
                gameScreen.returnLvlsBtn.click(event)
            if currentScreen=="fail":
                gameScreen.returnLvlsBtn.click(event)
        elif (type(gameScreen).__name__=="RedLightGreenLight" or type(gameScreen).__name__=="MarblesGame" or type(gameScreen).__name__=="DdakjiGame"):
            gameScreen.restartBtn.click(event)
            gameScreen.exitBtn.click(event)
        # elif (type(gameScreen).__name__=="MarblesGame"):
            
        # elif event.type == pg.MOUSEBUTTONDOWN:
        #     print("mouse is down") 
        # elif event.type == pg.MOUSEBUTTONUP:
        #     print("mouse is up")
    pg.display.update()
    frameCount+=1