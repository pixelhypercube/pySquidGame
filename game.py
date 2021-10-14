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

class Player:
    def __init__(self,x,y,r,color,is_player,max_speed=0.5):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

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
        pg.draw.circle(frame,self.color,(int(self.x),int(self.y)),int(self.r))
        pg.draw.circle(frame,Color.black,(int(self.x),int(self.y)),int(self.r),1)
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
    def contactPlayer(self,ball):
        distance = math.sqrt((self.x-ball.x)**2+(self.y-ball.y)**2)
        if (distance<ball.r+self.r):
            angle = math.atan2(self.y-ball.y,self.x-ball.x)
            self.vx += math.cos(angle)*0.1
            self.vy += math.sin(angle)*0.1
            ball.vx -= math.cos(angle)*0.1
            ball.vy -= math.sin(angle)*0.1
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
        self.playBtn = Button(WIDTH/2,HEIGHT/1.5,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Start Game!","levels")
        self.backBtn = Button(80,HEIGHT/5,50,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Back","home")
        self.levelBackBtn = Button(80,HEIGHT/8,50,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Back","levels")
        self.startBtn = Button(WIDTH/2,HEIGHT/1.33,100,25,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Start!",currentScreen[:-4])
        self.linkBtn = Button(WIDTH/2,HEIGHT/1.2,90,50,Color.white,Color.white,Color.white,Color.white,"",function=lambda :webbrowser.open("https://github.com/pixelhypercube/pySquidGame"))
        self.returnLvlsBtn = Button(WIDTH/2,HEIGHT/1.6,100,30,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,"Go back","levels")
        self.lvlNumBtns = []
        self.blocks = []
        self.forceAreas = []
        self.balls = []
        self.gameNames = ["Red Light,\n Green Light","Honeycomb \n(Coming Soon!)","Tug Of War \n(Coming Soon!)","Marbles \n(Coming Soon!)","Glass Stepping\n Stones \n(Coming Soon!)","Squid Game \n(Coming Soon!)"]
        self.gameImageNames = ["redLightGreenLight","honeyComb","tugOfWar","marbles","glassSteppingStones","squidGame"]
        for i in range(1,4):
            if i<=1:
                self.lvlNumBtns.append(Button(i*200,(HEIGHT/2)+30,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen=self.gameImageNames[i-1]+"Help",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
            else:
                self.lvlNumBtns.append(Button(i*200,(HEIGHT/2)+30,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen="levels",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
        for i in range(4,7):
            if i<=1:
                self.lvlNumBtns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen=self.gameImageNames[i-1]+"Help",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
            else:
                self.lvlNumBtns.append(Button((i-3)*200,(HEIGHT/2)+160,90,50,Color.squid_purple,Color.squid_purple2,Color.squid_pink,Color.grey,self.gameNames[i-1],screen="levels",function=None,image_path="./assets/img/levels/"+self.gameImageNames[i-1]+".png"))
        self.player = Player(50,HEIGHT/2,8,Color.white,True,max_speed=0.5)
        # self.hole = Hole(550,250,15,Color.black)
        self.lvlTxt = []
        self.strokes = 0
        self.par = 0
        self.currentLevel = 0
        self.paused = False

        self.won = False

        # # Game objects
        # self.redLightGreenLight = RedLightGreenLight(100,5,Color.sand,500,100)
    def showHome(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderImage("./assets/img/titleLogo.png",WIDTH/2,HEIGHT/3)
        # renderText("Py",WIDTH/2,HEIGHT/4,fontSize=40)
        renderText("By PixelHyperCube!",WIDTH/2,HEIGHT/1.9,fontSize=24)
        renderText("Made using pygame!",WIDTH/2,HEIGHT/1.7,fontSize=15)
        if mouseX>=WIDTH/2-90 and mouseX<=WIDTH/2+90 and mouseY>=HEIGHT/1.2-50 and mouseY<=HEIGHT/1.2+50:
            renderImage("./assets/img/invitationBack.png",WIDTH/2,HEIGHT/1.2)
        else:
            renderImage("./assets/img/invitationFront.png",WIDTH/2,HEIGHT/1.2)
        self.playBtn.show()

        # For debugging
        # self.linkBtn.show()
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
        renderText("the next 5 games are currently in progress!",WIDTH/2,HEIGHT/2.1,fontSize=20)
        self.returnLvlsBtn.show()
    def showFailureScreen(self):
        pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
        renderText("Eliminated :(",WIDTH/2,HEIGHT/3,fontSize=40)
        renderText("The good thing is, you can revive yourself",WIDTH/2,HEIGHT/2.4,fontSize=20)
        renderText(" by clicking the 'Go back' button! :)",WIDTH/2,HEIGHT/2.1,fontSize=20)
        self.returnLvlsBtn.show()
    def showHelpScreen(self):
        global currentScreen
        if currentScreen=="redLightGreenLightHelp":
            pg.draw.rect(frame,Color.squid_grey,(0,0,WIDTH,HEIGHT))
            self.levelBackBtn.show()
            renderText("How to play:",WIDTH/2,HEIGHT/12,fontSize=40)
            renderText("Run to the finish line before the time runs out!",WIDTH/2,HEIGHT/7,fontSize=20)
            renderImage("./assets/img/demoWithLabels.png",WIDTH/2,HEIGHT/2.25,[int(500/2.5),int(375/2.5)])
            renderText("When the doll faces you, freeze!",WIDTH/2,HEIGHT/1.21,fontSize=20)
            renderText("Otherwise, you'll be eliminated!",WIDTH/2,HEIGHT/1.16,fontSize=20)
            renderText("Use the WASD keys to move",WIDTH/2,HEIGHT/1.1,fontSize=20)
            renderText("Repeatedly press W if you want to boost your speed!",WIDTH/2,HEIGHT/1.06,fontSize=20)
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
        self.player = Player(random.randint(0,WIDTH),self.start_y+random.randint(0,200),8,Color.squid_light_teal,True,max_speed=0.5)
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
        self.genPlayers(50)

        # Footsteps list
        self.footsteps = []

        # 'Terminal' player max speed
        self.terminalMaxSpeed = 0.35

        # Variable to count the number of times 'W' was pressed
        self.wPressedCount = 0

        self.footstepTimeObj = None


    def genPlayers(self,count):
        for i in range(0,count):
            xPos = random.randint(30,WIDTH-30)
            yPos = self.start_y+random.randint(0,100)
            self.players.append(Player(xPos,yPos,8,Color.squid_teal,False,max_speed=random.random()*0.2+0.15))
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
                        player1.contactPlayer(player)
                    # player.contactPlayer(self.player)
                    player.friction = 10
                    if player.y<=self.start_y:
                        player.y == self.start_y
                    self.player.contactPlayer(player)
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
                            # Players shivering
                            if random.random()<0.025:
                                player.vx = random.random()*0.18-0.09
                                player.vy = random.random()*0.18-0.09
                    for player1 in self.players:
                        # player1.friction = 0.25
                        player1.contactPlayer(player)
                    player.friction = 0.1
                    self.player.contactPlayer(player)
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
    if (currentScreen=="redLightGreenLightHelp"):
        gameScreen.showHelpScreen()
    if (currentScreen=="redLightGreenLight"):
        if type(gameScreen).__name__=="RedLightGreenLight":
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
            if currentScreen=="redLightGreenLightHelp":
                gameScreen.levelBackBtn.click(event)
                gameScreen.startBtn.click(event)
            if currentScreen=="success":
                gameScreen.returnLvlsBtn.click(event)
            if currentScreen=="fail":
                gameScreen.returnLvlsBtn.click(event)
        elif (type(gameScreen).__name__=="RedLightGreenLight"):
            gameScreen.restartBtn.click(event)
            gameScreen.exitBtn.click(event)
        # elif event.type == pg.MOUSEBUTTONDOWN:
        #     print("mouse is down")
        # elif event.type == pg.MOUSEBUTTONUP:
        #     print("mouse is up")
    pg.display.update()
    frameCount+=1