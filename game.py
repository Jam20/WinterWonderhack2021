import copy
from screeninfo import get_monitors
import ui
from ui import UIBall
import pygame
import math
import time
import botv2
MAX_VEL = 300

class GameState:
       def __init__(self):
        self.isPlayerStripes = False
        self.isCategoryDecided = False
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
        ]
        
       def printState(self):
              print('Ball Information:', flush=True)
              for ball in self.balls:
                     print('Ball ', str(ball.number), ': Pos ', str(ball.pos), ", Vel ", str(ball.vel))

def runTurn(state, cueVel):
       ballsRemovedThisTurn = []
       for ball in state.balls:
              ball.vel = cueVel if ball.isCue else ball.vel

              while not isTurnDone(state):
                     removedBalls = ui.render(state.balls)
                     ballsRemovedThisTurn.extend(removedBalls)
                     state.printState()
       return ballsRemovedThisTurn
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
       ballsRemoved = runTurn(state, cueVel)
       if len(ballsRemoved) > 0:
              if not state.isCategoryDecided:
                     state.isPlayerStripes = ballsRemoved[0].isStripped
                     state.isCategoryDecided = True
              scratch = False
              for ball in ballsRemoved:
                     if ball.isCue:
                            state.balls.append(UIBall(0, (85,64)))
                            scratch = True
                            return 0
                     if ball.number == 8:
                            return 2
              if not scratch and state.isPlayerStripes == ballsRemoved[0].isStripped:
                     playPlayerTurn(state)
       hasWon = True
       if not state.isCategoryDecided:
              return 0
       for ball in state.balls:
              if ball.isStripped == state.isPlayerStripes and not ball.isCue:
                     hasWon = False
              if ball.number == 8:
                     hasWon = False
       return 1 if hasWon else 0

def playBotTurn(state):
       botTurn = botv2.getBestMove(state)
       ballsRemoved = runTurn(state, (200,0))
       if len(ballsRemoved) > 0:
              if not state.isCategoryDecided:
                     state.isPlayerStripes = not ballsRemoved[0].isStripped
                     state.isCategoryDecided = True
              for ball in ballsRemoved:
                     if ball.isCue:
                            state.balls.append(UIBall(0, (85,64)))
                            return
              if not (state.isPlayerStripes == ballsRemoved[0].isStripped):
                     playBotTurn(state)
       hasWon = True
       if not state.isCategoryDecided:
              return 0
       for ball in state.balls:
              if not ball.isStripped == state.isPlayerStripes and not ball.isCue:
                     hasWon = False
              if ball.number == 8:
                     hasWon = False
       return 2 if hasWon else 0
           

def runGame():
       mainState = GameState()
       winner = 0
       whoIsStripes = 0
       previousState = copy.deepcopy(mainState)
       mainState.printState()
       while winner == 0:
              winner = playPlayerTurn(mainState)
              winner = playBotTurn(mainState)
       if winner == 1:
              print("YOU WIN GOOD JOB")
       else:
              print("YOU LOSE GET GOOD")


