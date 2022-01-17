import math
import time
ACCELERATION = (-10, -10)


class Ball:
    def __init__(self, pos, vel):
        self.radius = 5
        self.pos = pos
        self.vel = vel


class Board:
    def __init__(self):
        self.width = 254
        self.height = 132
        self.thickness = 13


class Pocket:
    def __init__(self):
        self.radius = 12

def sign(num):
    if num >= 0:
        return 1
    else:
        return -1

def updateBall(dt, ball):
    ball.pos = (ball.pos[0] + ball.vel[0]*dt, ball.pos[1] + ball.vel[1]*dt)
    ball.vel = (ball.vel[0] + sign(ball.vel[0])*ACCELERATION[0]*dt,
                ball.vel[1] + sign(ball.vel[1])*ACCELERATION[1] * dt)


def checkWallCollisons(ball):
    if(ball.pos[0] - ball.radius <= 0):
        ball.vel = (abs(ball.vel[0]), ball.vel[1])
    if(ball.pos[1] - ball.radius <= 0):
        ball.vel = (ball.vel[0], abs(ball.vel[1]))
    if(ball.pos[0] + ball.radius >= Board().width):
        ball.vel = (-abs(ball.vel[0]), ball.vel[1])
    if(ball.pos[1] + ball.radius >= Board().height):
        ball.vel = (ball.vel[0], -abs(ball.vel[1]))


def checkBallCollisions(ball, balls):
    for otherBall in balls:
        if(otherBall != ball):
            dist = ((otherBall.pos[0] - ball.pos[0]),
                    otherBall.pos[1] - ball.pos[1])
            distMag = (math.sqrt(pow(dist[0], 2) + pow(dist[1], 2)))
            if(distMag <= ball.radius*2):
                overlap = ball.radius*2 - distMag
                distNormalized = (dist[0]/distMag, dist[1]/distMag)

                ball.pos = (ball.pos[0] - (overlap * .5 * distNormalized[0]),
                            ball.pos[1] - (overlap * .5 * distNormalized[1]))
                otherBall.pos = (otherBall.pos[0] + (overlap * .5 * distNormalized[0]),
                                 otherBall.pos[1] + (overlap * .5 * distNormalized[1]))

                normal = ((ball.pos[0] - otherBall.pos[0])/distMag,
                          (ball.pos[1] - otherBall.pos[1])/distMag)
                tangVec = (-normal[1], normal[0])

                dotProductTangentalOne = ball.vel[0] * \
                    tangVec[0] + ball.vel[1] * tangVec[1]
                dotProductTangentalTwo = otherBall.vel[0] * \
                    tangVec[0] + otherBall.vel[1] * tangVec[1]

                dotProductNorm1 = ball.vel[0] * \
                    normal[0] + ball.vel[1] * normal[1]
                dotProductNorm2 = otherBall.vel[0] * \
                    normal[0] + otherBall.vel[1] * normal[1]

                ball.vel = (tangVec[0] * dotProductTangentalOne + normal[0] * dotProductNorm2,
                            tangVec[1] * dotProductTangentalOne + normal[1] * dotProductNorm2)
                otherBall.vel = (
                    tangVec[0] * dotProductTangentalTwo + normal[0] * dotProductNorm1, tangVec[1] * dotProductTangentalTwo + normal[1] * dotProductNorm1)


def checkScoredBalls(ball, ballsToRemove):
    if ball.pos[0] <= Pocket().radius or ball.pos[0] >= Board().width - Pocket().radius or (ball.pos[0] >= (Board().width/2) - Pocket().radius and ball.pos[0] <= (Board().width/2) + Pocket().radius):
        if(ball.pos[1] <= Pocket().radius or ball.pos[1] >= Board().height - Pocket().radius):
            ballsToRemove.append(ball)


def update(dt, balls):
    ballsToRemove = []
    for ball in balls:
        updateBall(dt, ball)
        checkWallCollisons(ball)
        checkBallCollisions(ball, balls)
        #checkScoredBalls(ball, ballsToRemove)
    for ball in ballsToRemove:
        balls.remove(ball)
