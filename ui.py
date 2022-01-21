import pygame
import enginev2
import random
from screeninfo import get_monitors
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




def drawTable():
    screen.blit(tableImage, (0,0))
    # pocketPositions = [(2.66,4.5, 7.75), (132.25,0,6.75), (265,4.5,7.75), (2.66,138.75, 7.75), (132.25,140,6.75), (265,138.75,7.75)]    
    # for pocketPos in pocketPositions:
    #     pygame.draw.circle(screen, (255,0,0), ((pocketPos[0]-pocketPos[2])*cmToPixels + boardThickness, (pocketPos[1]-pocketPos[2])*cmToPixels + boardThickness), pocketPos[2]*cmToPixels)
    wallPositions = [[(0,25), (50,50), (100,100), (200,100)]]
    for wall in wallPositions:
        mappedWall = []
        for pos in wall:
            mappedWall.append((pos[0]*cmToPixels+boardThickness, pos[1]*cmToPixels+boardThickness))
        pygame.draw.polygon(screen, (255,0,0), mappedWall)

def drawBalls(balls):
    for ball in balls:
        screen.blit(images[ball.number], [(ball.pos[0]-ball.radius) * cmToPixels + boardThickness, (ball.pos[1]-ball.radius) * cmToPixels + boardThickness])


def render(balls):
    enginev2.update(clock.tick(300)/1000, balls)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    screen.fill((0, 0, 0))
    drawTable()
    drawBalls(balls)
    pygame.display.flip()

