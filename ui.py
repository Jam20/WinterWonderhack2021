from copy import deepcopy
import time
import pygame
import enginev2
import random
from screeninfo import get_monitors
import math
import numpy as np
from multiprocessing import Pool

frameTime = pygame.time.get_ticks()

class UIBall(enginev2.Ball):
    def __init__(self, number, pos, vel = (0,0)):
        enginev2.Ball.__init__(self, pos, vel)
        self.number = number
        self.isStripped = number>8
        self.isCue = number == 0
        self.isPocketed = False


mnum = 1 if len(get_monitors()) > 1 else 0
cmToPixels = int(get_monitors()[
                 mnum].width / (enginev2.BOARD_WIDTH + 2 * enginev2.BOARD_THICKNESS))
if get_monitors()[mnum].width>2000:
    cmToPixels = cmToPixels/2

boardWidth = cmToPixels * enginev2.BOARD_WIDTH
boardHeight = cmToPixels * enginev2.BOARD_HEIGHT
boardThickness = cmToPixels * enginev2.BOARD_THICKNESS
ballRadius = cmToPixels * enginev2.Ball((0, 0), (0, 0)).radius
constRad = enginev2.Ball((0, 0), (0, 0)).radius
screenWidth = boardWidth + boardThickness*2
screenHeight = boardHeight + boardThickness*2

screen = pygame.display.set_mode([screenWidth, screenHeight])
clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.display.set_caption("Amazing Pool Bot")
font = pygame.font.SysFont("Comic Sans MS", 30)
images = []
for i in range(1,16):
    image = pygame.image.load('assets/ball_' + str(i) + '.png')
    image = pygame.transform.scale(image, (constRad*2*cmToPixels,constRad*2*cmToPixels))
    images.append(image)
cueImage = pygame.image.load('assets/ball_16.png')
cueImage = pygame.transform.scale(cueImage, (constRad*2*cmToPixels,constRad*2*cmToPixels))
images.insert(0, cueImage)
tableImage = pygame.image.load('assets/table.png').convert()
tableImage = pygame.transform.scale(tableImage, (screenWidth, screenHeight))
cueImage = pygame.image.load('assets/cue.png')
cueImage = pygame.transform.rotate(cueImage, 180)




def drawTable():
    screen.blit(tableImage, (0,0))
    # for wall in enginev2.WALLS:
    #     lines= np.array([wall[:2], wall[2:], wall[::2], wall[1::2]])
    #     for line in lines:
    #         line_pos = line*cmToPixels+boardThickness
    #         pygame.draw.line(screen, (255,0,0), line_pos[0],line_pos[1])
    # for pocket in enginev2.POCKETS:
    #     line_pos = pocket*cmToPixels+boardThickness
    #     pygame.draw.line(screen, (255,0,0), line_pos[0],line_pos[1])

def draw_ball(ball):
    display_pos = (ball.pos-ball.radius)*cmToPixels+boardThickness
    screen.blit(images[ball.number], [float(display_pos[0]),float(display_pos[1])])


def drawBalls(balls):
    cueBall = enginev2.Ball((0,0),(0,0))
    ui_pool.map(draw_ball, balls)
    for ball in balls:
        cueBall = ball if ball.isCue else cueBall
    
    return cueBall

def drawCue(currentVel, ball):
    if currentVel[0] == 0 and currentVel[1] == 0:
        return
    
    velMag = math.sqrt(pow(currentVel[0],2) + pow(currentVel[1],2))
    velComp = (currentVel[0]/velMag, currentVel[1]/velMag)

    cueTipPos = (ball.pos[0]-.4 + (ball.radius+velMag/10)*velComp[0],ball.pos[1] + (ball.radius+velMag/10)*velComp[1])
    cueAngle = math.atan2((velComp[1]), -velComp[0])*180/math.pi+180
    if cueAngle > 0 and cueAngle <180:
        cueTipPos = (cueTipPos[0], cueTipPos[1]+(509/cmToPixels)*velComp[1])
    if cueAngle > 90 and cueAngle < 270: 
        cueTipPos = (cueTipPos[0]+(509/cmToPixels)*velComp[0], cueTipPos[1])
    
    angledImg = pygame.transform.rotate(cueImage, cueAngle)
    screen.blit(angledImg, [boardThickness + cueTipPos[0]*cmToPixels, boardThickness + cueTipPos[1]*cmToPixels])


def render(balls, currentVel = (0,0)):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    frame_time_sec = clock.tick(1000)/1000
    engine_results = ui_pool.apply_async(enginev2.update,(frame_time_sec, balls))
    
    screen.fill((0, 0, 0))
    drawTable()
    start_time = time.time()
    cueBall = drawBalls(balls)
    total_time = time.time()-start_time
    drawCue(currentVel, cueBall)
    pygame.display.flip()
    
    updated_balls = engine_results.get()
    
    print(f"Frame: {str(clock.get_time())} time: {str(total_time*1000)}", end="\r", flush=True)
    return updated_balls

def reRender(balls):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    clock.tick(1000)
    screen.fill((0, 0, 0))
    drawTable()
    cueBall = drawBalls(balls)
    drawCue((0,0), cueBall)
    pygame.display.flip()

ui_pool = Pool()
