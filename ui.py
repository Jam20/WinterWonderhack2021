import pygame
import enginev2
import random
from screeninfo import get_monitors
import math

frameTime = pygame.time.get_ticks()

class UIBall(enginev2.Ball):
    def __init__(self, id, pos, vel, number):
        enginev2.Ball.__init__(self, pos, vel)
        self.number = number
        self.isStripped = number>8
        self.isCue = number == 0
        self.isPocketed = False


mnum = 1 if len(get_monitors()) > 1 else 0
cmToPixels = int(get_monitors()[
                 mnum].width / (enginev2.Board().width + 2 * enginev2.Board().thickness))
if get_monitors()[mnum].width>2000:
    cmToPixels = cmToPixels/2

boardWidth = cmToPixels * enginev2.Board().width
boardHeight = cmToPixels * enginev2.Board().height
boardThickness = cmToPixels * enginev2.Board().thickness
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
tableImage = pygame.image.load('assets/table.png')
tableImage = pygame.transform.scale(tableImage, (screenWidth, screenHeight))
cueImage = pygame.image.load('assets/cue.png')
cueImage = pygame.transform.rotate(cueImage, 180)



def drawTable():
    screen.blit(tableImage, (0,0))
    # pocketPositions = [(2.66,4.5, 7.75), (132.25,0,6.75), (265,4.5,7.75), (2.66,138.75, 7.75), (132.25,140,6.75), (265,138.75,7.75)]    
    # for pocketPos in pocketPositions:
    #     pygame.draw.circle(screen, (255,0,0), ((pocketPos[0]-pocketPos[2])*cmToPixels + boardThickness, (pocketPos[1]-pocketPos[2])*cmToPixels + boardThickness), pocketPos[2]*cmToPixels)
    # wallPositions = [[ (-5.3,   4.25  ),   (0,      9.5   ),   (0,     116.7  ),   (-5.3,  122.5   ) ],
    #                  [ (259.5,  4.25  ),   (254.3,  9.5   ),   (254.3, 117    ),   (259.5, 123    ) ],
    #                  [ (8,      -.1   ),   (2.25,   -5.3  ),   (118.2, -5.3   ),   (116,   -.1    ) ],
    #                  [ (134.75, -.1   ),   (132.25, -5.3  ),   (249.5, -5.3   ),   (243.9, -.1    ) ],
    #                  [ (134.75, 127.25),   (132.25, 132.4 ),   (249.5, 132.4  ),   (243.9, 127.25 ) ],
    #                  [ (8.3,    127.25),   (2.75,   132.4 ),   (118.7, 132.4  ),   (116.5, 127.25 ) ]]
    # for wall in wallPositions:
    #     mappedWall = []
    #     for pos in wall:
    #         mappedWall.append((pos[0]*cmToPixels+boardThickness, pos[1]*cmToPixels+boardThickness))
    #     pygame.draw.polygon(screen, (255,0,0), mappedWall)

def drawBalls(balls):
    cueBall = enginev2.Ball((0,0),(0,0))
    for ball in balls:
        screen.blit(images[ball.number], [(ball.pos[0]-ball.radius) * cmToPixels + boardThickness, (ball.pos[1]-ball.radius) * cmToPixels + boardThickness])
        cueBall = ball if ball.isCue else cueBall
    return cueBall

def drawCue(currentVel, ball):
    if currentVel[0] == 0 and currentVel[1] == 0:
        return
    cueTipPos = (ball.pos[0]-.4 + (ball.radius)*currentVel[0],ball.pos[1] + (ball.radius)*currentVel[1])
    cueAngle = math.atan2((currentVel[1]), -currentVel[0])*180/math.pi+180
    if cueAngle > 0 and cueAngle <180:
        cueTipPos = (cueTipPos[0], cueTipPos[1]+(509/cmToPixels)*currentVel[1])
    if cueAngle > 90 and cueAngle < 270: 
        cueTipPos = (cueTipPos[0]+(509/cmToPixels)*currentVel[0], cueTipPos[1])
    angledImg = pygame.transform.rotate(cueImage, cueAngle)
    screen.blit(angledImg, [boardThickness + cueTipPos[0]*cmToPixels, boardThickness + cueTipPos[1]*cmToPixels])


def render(balls, currentVel = (0,0)):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    enginev2.update(clock.tick(300)/1000, balls)

    screen.fill((0, 0, 0))
    drawTable()
    cueBall = drawBalls(balls)
    drawCue(currentVel, cueBall)
    pygame.display.flip()

