import math
import time
DECELERATION = .8


class Ball:
    def __init__(self, pos, vel):
        self.radius = 5
        self.pos = pos
        self.vel = vel



class Board:
    def __init__(self):
        self.width = 254
        self.height = 127
        self.thickness = 19


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
    ball.vel = (ball.vel[0] + -ball.vel[0]*DECELERATION*dt ,
                ball.vel[1] + -ball.vel[1]*DECELERATION*dt )
    if(abs(ball.vel[0])<=.1):
        ball.vel = (0, ball.vel[1])
    if(abs(ball.vel[1])<=.1):
        ball.vel = (ball.vel[0], 0)
    



def checkWallCollisons(ball):
    if(ball.pos[0]< 0):
        ball.vel = (abs(ball.vel[0])*.9, ball.vel[1])
        ball.pos = (1, ball.pos[1])

    if(ball.pos[1]< 0):
        ball.vel = (ball.vel[0], abs(ball.vel[1])*.9)
        ball.pos = (ball.pos[0],1)

    if(ball.pos[0] + ball.radius*2 > Board().width):
        ball.vel = (-abs(ball.vel[0])*.9, ball.vel[1])
        ball.pos = (Board().width-ball.radius*2-1, ball.pos[1])

    if(ball.pos[1] + ball.radius*2 > Board().height):
        ball.vel = (ball.vel[0], -abs(ball.vel[1])*.9)
        ball.pos = (ball.pos[0], Board().height-ball.radius*2-1)



def checkBallCollisions(ball, balls):
    for otherBall in balls:
        if(otherBall != ball):
            ballPos = (ball.pos[0]+ball.radius, ball.pos[1]+ball.radius)
            otherBallPos = (otherBall.pos[0] + otherBall.radius, otherBall.pos[1] + otherBall.radius)

            dist = ((otherBallPos[0] - ballPos[0]),
                    otherBallPos[1] - ballPos[1])

            distMag = (math.sqrt(pow(dist[0], 2) + pow(dist[1], 2)))
            if(distMag <= ball.radius*2):
                overlap = ball.radius*2 - distMag
                distNormalized = (dist[0]/distMag, dist[1]/distMag)

                ballPos = (ballPos[0] - (overlap * distNormalized[0] * .5), ballPos[1] - (overlap * distNormalized[1] * .5))
                otherBallPos = (otherBallPos[0] + (overlap * distNormalized[0]* .5), otherBallPos[1] + (overlap * distNormalized[1] * .5))
                
                normal = ((ballPos[0] - otherBallPos[0])/distMag,
                          (ballPos[1] - otherBallPos[1])/distMag)
                
                p = (ball.vel[0]*normal[0]-otherBall.vel[0]*normal[0], ball.vel[1]*normal[1]-otherBall.vel[1]*normal[1])
                ball.vel = (ball.vel[0] - p[0]*normal[0], ball.vel[1] - p[1]*normal[1])
                otherBall.vel = (otherBall.vel[0] + p[0] * normal[0], otherBall.vel[1] + p[1]*normal[1])

                # tangVec = (-normal[1], normal[0])

                # dotProductTangentalOne = ball.vel[0] * \
                #     tangVec[0] + ball.vel[1] * tangVec[1]
                # dotProductTangentalTwo = otherBall.vel[0] * \
                #     tangVec[0] + otherBall.vel[1] * tangVec[1]

                # dotProductNorm1 = ball.vel[0] * \
                #     normal[0] + ball.vel[1] * normal[1]
                # dotProductNorm2 = otherBall.vel[0] * \
                #     normal[0] + otherBall.vel[1] * normal[1]

                # ball.vel = (tangVec[0] * dotProductTangentalOne + normal[0] * dotProductNorm2,
                #             tangVec[1] * dotProductTangentalOne + normal[1] * dotProductNorm2)
                # otherBall.vel = (
                #     tangVec[0] * dotProductTangentalTwo + normal[0] * dotProductNorm1, tangVec[1] * dotProductTangentalTwo + normal[1] * dotProductNorm1)
                
                ball.pos = (ballPos[0] - ball.radius, ballPos[1] - ball.radius)
                otherBall.pos = (otherBallPos[0] - otherBall.radius, otherBallPos[1] - otherBall.radius)


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
