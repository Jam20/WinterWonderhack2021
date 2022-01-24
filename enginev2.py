import math
from operator import indexOf
import time
from xmlrpc.client import MAXINT
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
        self.radius = 7.75

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
    
def wallMax(wall, isX):
    max = -MAXINT
    for point in wall:
        pos = point[0] if isX else point[1]
        max = pos if pos>max else max
    return max

def wallMin(wall, isX):
    min = MAXINT
    for point in wall:
        pos = point[0] if isX else point[1]
        min = pos if pos<min else min
    return min

def isVert(rectLine):
    return rectLine[0][0] == rectLine[1][0]

def checkWallCollisons(ball):
    wallPositions = [[ (-5.3,   4.25  ),   (0,      9.5   ),   (0,     117    ),   (-5.3,  122.5  ) ],
                     [ (254.3,  9.5   ),   (259.5,  4.25  ),   (259.5, 123    ),   (254.3, 117    ) ],
                     [ (8,      -.1   ),   (2.25,   -5.3  ),   (118.2, -5.3   ),   (116,   -.1    ) ],
                     [ (134.75, -.1   ),   (132.25, -5.3  ),   (249.5, -5.3   ),   (243.9, -.1    ) ],
                     [ (134.75, 127.25),   (132.25, 132.4 ),   (249.5, 132.4  ),   (243.9, 127.25 ) ],
                     [ (8.3,    127.25),   (2.75,   132.4 ),   (118.7, 132.4  ),   (116.5, 127.25 ) ]]
    rectLines = [[(0,      9.5   ),   (0,     117    )],
                 [(254.3,  9.5   ),   (254.3, 117    )],
                 [(8,      -.1   ),   (116,   -.1    )],
                 [(134.75, -.1   ),   (243.9, -.1    )],
                 [(134.75, 127.25),   (243.9, 127.25 )],
                 [(8.3,    127.25),   (116.5, 127.25 )]]
    for wall in wallPositions:  
        corners = [(wallMin(wall, True), wallMin(wall, False)), ((wallMax(wall, True), wallMax(wall, False)))]
        collideX = ball.pos[0]+ball.radius>=corners[0][0] and ball.pos[0]-ball.radius<=corners[1][0]
        collideY = ball.pos[1]+ball.radius>=corners[0][1] and ball.pos[1]-ball.radius<=corners[1][1]
        if collideX:
            if collideY:
                idx = indexOf(wallPositions, wall)
                if isVert(rectLines[idx]) and ball.pos[1] >= rectLines[idx][0][1] and ball.pos[1]<= rectLines[idx][1][1]:
                    ball.vel = (-ball.vel[0], ball.vel[1])
                elif (not isVert(rectLines[idx])) and ball.pos[0] >= rectLines[idx][0][0] and ball.pos[0]<= rectLines[idx][1][0]:
                    ball.vel = (ball.vel[0], -ball.vel[1])
                    


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
                
                dist = ((otherBallPos[0] - ballPos[0]),
                    otherBallPos[1] - ballPos[1])

                distMag = (math.sqrt(pow(dist[0], 2) + pow(dist[1], 2)))
            
                normalx = (otherBallPos[0] - ballPos[0])/distMag
                normaly = (otherBallPos[1] - ballPos[1])/distMag
                p = 2 * (ball.vel[0]*normalx + ball.vel[1] * normaly - otherBall.vel[0]* normalx - otherBall.vel[1]*normaly)/4
                ball.vel = (ball.vel[0] - p*2*normalx, ball.vel[1] - p*2*normaly)
                otherBall.vel = (otherBall.vel[0] + p*2*normalx, otherBall.vel[1] + p*2*normaly)
                
                # p = (ball.vel[0]*normal[0]-otherBall.vel[0]*normal[0], ball.vel[1]*normal[1]-otherBall.vel[1]*normal[1])
                # ball.vel = (ball.vel[0] - p[0]*normal[0], ball.vel[1] - p[1]*normal[1])
                # otherBall.vel = (otherBall.vel[0] + p[0] * normal[0], otherBall.vel[1] + p[1]*normal[1])
                
                ball.pos = (ballPos[0] - ball.radius, ballPos[1] - ball.radius)
                otherBall.pos = (otherBallPos[0] - otherBall.radius, otherBallPos[1] - otherBall.radius)


def checkScoredBalls(ball, ballsToRemove):
    pocketPositions = [(2.66,     4.5,     7.75), #(x,y,r)
                       (132.25,   0,       6.75),
                       (265,      4.5,     7.75),
                       (2.66,     38.75,   7.75),
                       (132.25,   140,     6.75),
                       (265,      138.75,  7.75)]
    for pocket in pocketPositions:
        dist = math.sqrt(pow(ball.pos[0]-pocket[0],2) + pow(ball.pos[1]-pocket[1],2))
        if dist<pocket[2]:
            ballsToRemove.append(ball)


def update(dt, balls):
    ballsToRemove = []
    for ball in balls:
        updateBall(dt, ball)
        checkWallCollisons(ball)
        checkBallCollisions(ball, balls)
        checkScoredBalls(ball, ballsToRemove)
    for ball in ballsToRemove:
        balls.remove(ball)
