import copy
from screeninfo import get_monitors
import ui
from ui import UIBall
import enginev2
import pygame
import math
import time
MAX_VEL = 300

class GameState:
       def __init__(self):
        self.isPlayerStripes = False
        self.categoryDecided = False
        
        self.balls = [
            UIBall(0, (85, 64)),

            UIBall(1, (170, 64)),

            UIBall(2, (180, 59)),
            UIBall(3, (180, 69)),
            
            UIBall(4, (190, 54)),
            UIBall(5, (190, 64)),
            UIBall(6, (190, 74)),
            
            UIBall(7,  (200, 49)),
            UIBall(8,  (200, 59)),
            UIBall(9,  (200, 69)),
            UIBall(10, (200, 79)),
            
            UIBall(11,  (210, 44)),
            UIBall(12,  (210, 54)),
            UIBall(13,  (210, 64)),
            UIBall(14,  (210, 74)),
            UIBall(15,  (210, 84)),
                        

       #      UIBall(1, (170, 64), (0, 0), 1),

       #      UIBall(9, (170 + constRad * 2, 64 - constRad),
       #             (0, 0), 2),
       #      UIBall(2, (170 + constRad * 2, 64 + constRad), (0, 0), 3),

       #      UIBall(10, (170 + constRad * 4, 64 - constRad * 2),
       #             (0, 0), 4),
       #      UIBall(8, (170 + constRad * 4, 64), (0, 0), 5),
       #      UIBall(3, (170 + constRad * 4, 64 + constRad * 2),
       #             (0, 0), 6),

       #      UIBall(11, (170 + constRad * 6, 64 - constRad * 3),
       #             (0, 0), 7),
       #      UIBall(7, (170 + constRad * 6, 64 - constRad), (0, 0), 8),
       #      UIBall(14, (170 + constRad * 6, 64 + constRad),
       #             (0, 0), 9),
       #      UIBall(4, (170 + constRad * 6, 64 + constRad * 3),
       #             (0, 0), 10),

       #      UIBall(5, (170 + constRad * 8, 64 - constRad * 4),
       #             (0, 0), 11),
       #      UIBall(13, (170 + constRad * 8, 64 - constRad * 2),
       #             (0, 0), 12),
       #      UIBall(15, (170 + constRad * 8, 64), (0, 0), 13),
       #      UIBall(6, (170 + constRad * 8, 64 + constRad * 2),
       #             (0, 0), 14),
       #      UIBall(12, (170 + constRad * 8, 64 + constRad * 4),
       #             (0, 0), 15),
        ]
       def printState(self):
              print('Ball Information:', flush=True)
              for ball in self.balls:
                     print('Ball ', str(ball.number), ': Pos ', str(ball.pos), ", Vel ", str(ball.vel))

def runTurn(state, cueVel):
    for ball in state.balls:
        if(ball.isCue):
            ball.vel = cueVel
            while not isTurnDone(state):
                ui.render(state.balls)
                state.printState()
def isTurnDone(state):
       for ball in state.balls:
              if abs(ball.vel[0]) > 0 or abs(ball.vel[1]) > 0:
                     return False
       return True

def getPlayerVel(state):
       cueBall = [ball for ball in state.balls if ball.isCue][0]
       leftMouse = pygame.mouse.get_pressed()[0] == 1
       while not leftMouse:
              mousePos = pygame.mouse.get_pos()
              mouseDist = (mousePos[0]-(cueBall.pos[0]*ui.cmToPixels+ui.boardThickness), mousePos[1]- (cueBall.pos[1]*ui.cmToPixels + ui.boardThickness))
              distMag = math.sqrt(pow(mouseDist[0], 2) + pow(mouseDist[1], 2))
              currentVel = (mouseDist[0]/distMag, mouseDist[1]/distMag)
              ui.render(state.balls, currentVel)
              leftMouse = pygame.mouse.get_pressed()[0] == 1
       initTime = time.perf_counter()
       timeElapsed = time.perf_counter()-initTime
       while leftMouse:
              mousePos = pygame.mouse.get_pos()
              mouseDist = (mousePos[0]-(cueBall.pos[0]*ui.cmToPixels+ui.boardThickness), mousePos[1]- (cueBall.pos[1]*ui.cmToPixels + ui.boardThickness))
              distMag = math.sqrt(pow(mouseDist[0], 2) + pow(mouseDist[1], 2))
              currentVel = (mouseDist[0]/distMag, mouseDist[1]/distMag)
              power = timeElapsed/3 * MAX_VEL
              currentVel = (currentVel[0] * power, currentVel[1] * power)
              ui.render(state.balls, currentVel)
              timeElapsed = time.perf_counter()-initTime
              timeElapsed = 3 if timeElapsed>3 else timeElapsed
              leftMouse = pygame.mouse.get_pressed()[0] == 1
       currentVel = (currentVel[0]*math.cos(math.pi) - currentVel[1]*math.sin(math.pi)
                    ,currentVel[0]*math.sin(math.pi) + currentVel[1]*math.cos(math.pi))
       return currentVel

def playPlayerTurn(state):
       cueVel = getPlayerVel(state)
       runTurn(state, cueVel)

def playBotTurn(state):
       runTurn(state, (200,0))
           

def runGame():
       mainState = GameState()
       winner = 0
       whoIsStripes = 0
       previousState = copy.deepcopy(mainState)
       while winner == 0:
              playPlayerTurn(mainState)
              playBotTurn(mainState)


