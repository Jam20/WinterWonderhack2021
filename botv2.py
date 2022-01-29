from copy import deepcopy
from math import atan2
import math
from turtle import back

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
    results = []
    cueIdx = -1
    
    for ball in state.balls:
        if ball.isCue:
            cueIdx = state.balls.index(ball)
    state.balls[cueIdx], state.balls[0] = state.balls[0], state.balls[cueIdx]
    
    for x in range(0,200):
        rowResults = pool.map_async(simulate, [simulation(state,(x,y)) for y in range(0,200)])
        results.append(rowResults)

    bestScore = -1
    bestVel = (0,0)
    for row in results:
        scores= row.get()
        for score in scores:
            if score> bestScore:
                bestVel = (results.index(row), scores.index(score))
                bestScore = score
    return bestVel
               
def simulate(simulation):
    usableState = deepcopy(simulation.state)
    ballsRemovedThisIteration = []
    print("Starting simulation with velocity: " + str(simulation.vel), flush=True)
    usableState.balls[0].vel = simulation.vel
    
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


def getMove(state):
    velList = []
    for ball in state.balls:
        cueVel = checkScore(state,ball)
        if cueVel[0] >0 or cueVel[1] > 0:
            velList.append(cueVel)
    return velList

def checkScore(state, ball):
    pocketPositions = [(2.66,     4.5,     7.75), #(x,y,r)
                       (132.25,   0,       6.75),
                       (265,      4.5,     7.75),
                       (2.66,     38.75,   7.75),
                       (132.25,   140,     6.75),
                       (265,      138.75,  7.75)
                       ]
    maxAngle = 45
    for pocket in pocketPositions:
        dist = (pocket[0]-ball.pos[0], pocket[1]-ball.pos[1])
        distMag = math.sqrt(dist[0]**2 + dist[1]**2)
        vel = (dist[0]/distMag, dist[1]/distMag)
        vel = (vel[0]*10, vel[1] * 10)
        cueVel = backPropegate(state, ball, (pocket[0], pocket[1]), vel)



def simulateCollisions(vel):
    velocities = []
    for x in range(-1,1,0.01):
        y = math.sin(math.acos(x))
        otherVely = (vel[1]/y - vel[0]/x)/(2*y)
        otherVelx = vel[1]/y - otherVely*y
        velocities.append((otherVelx,otherVely))
    return velocities


def backPropegate(state, ball, pos, vel):
    if ball.isCue:
        return vel
    velocities = simulateCollisions(vel)
    for velocity in velocities:
        velMag = math.sqrt(velocity[0]**2 + velocity[1]**2)
        unitVel = (velocity[0]/velMag, velocity[1]/velMag)
        for otherBall in state.balls:
            dist = (otherBall.pos[0]-ball.pos[0], otherBall.pos[1]-ball.pos[1])
            distMag = math.sqrt(dist[0]**2, dist[1]**2)
            normal = (dist[0]/distMag, dist[1]/distMag)
            diff = (normal[0]-unitVel[0], normal[1]-unitVel[1])
            if abs(diff[0])<.01 and abs(diff[1]<.01):
                
