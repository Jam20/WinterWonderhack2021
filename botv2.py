from copy import deepcopy

from pygame import init
import enginev2
import game
from multiprocessing import Pool, Manager
from ui import UIBall


class simulation:
    def __init__(self, state, vel):
        self.state = state
        self.vel = vel

def getBestMove(state):
    pool = Pool()
    scores = [[]]
    for x in range(0,300):
        rowScores = pool.map(simulate, [simulation(state,(x,y)) for y in range(0,300)])

            
def simulate(simulation):
    usableState = deepcopy(simulation.state)
    ballsRemovedThisIteration = []
    
    for ball in usableState.balls:
        if ball.isCue:
            ball.vel = simulation.vel
    
    while(not game.isTurnDone(usableState)):
        removed = enginev2.update(0.1, usableState.balls)
        ballsRemovedThisIteration.extend(removed)

    
    isPlayerStripes = False
    if simulation.state.isCategoryDecided:
        isPlayerStripes = simulation.state.isPlayerStripes
    else:
        if len(usableState.balls) > 0:
            isPlayerStripes = not usableState.balls[0].isStripped
        else:
            return 0


    sameCatagoryBallsRemoved = 0
    otherCatagoryBallsRemoved = 0
    scratch = False
    loss = False
    timeForEight = False

    for ball in usableState.balls:
        if not ball.isStripped == isPlayerStripes and not ball.number == 8 and not ball.isCue:
            timeForEight = True

    for ball in ballsRemovedThisIteration:
        scratch = ball.isCue
        loss = ball.number == 8
        loss = False if timeForEight else loss
        if ball.isStripped == isPlayerStripes:
            otherCatagoryBallsRemoved += 1
        else:
            sameCatagoryBallsRemoved += 1

    score = sameCatagoryBallsRemoved-otherCatagoryBallsRemoved
    return score if not scratch and not loss else -1
