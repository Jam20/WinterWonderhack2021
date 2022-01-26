import math
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
    
def isVert(pointA, pointB):
    return pointA[0] == pointB[0]

def checkWallCollisons(ball):
    leftWall        = [ (0,      9.5   ),   (0,     117    ),   (-5.3,   4.25  ),   (-5.3,  122.5  ) ]
    rightWall       = [ (254.3,  9.5   ),   (254.3, 117    ),   (259.5,  4.25  ),   (259.5, 123    ) ]
    topLeftWall     = [ (8,      -.1   ),   (116,   -.1    ),   (2.25,   -5.3  ),   (118.2, -5.3   ) ]
    topRightWall    = [ (134.75, -.1   ),   (243.9, -.1    ),   (132.25, -5.3  ),   (249.5, -5.3   ) ]
    bottomLeftWall  = [ (8.3,    127.25),   (116.5, 127.25 ),   (2.75,   132.4 ),   (118.7, 132.4  ) ] 
    bottomRightWall = [ (134.75, 127.25),   (243.9, 127.25 ),   (132.25, 132.4 ),   (249.5, 132.4  ) ]

    walls = [leftWall, rightWall, topLeftWall, topRightWall, bottomLeftWall, bottomRightWall]


    #Check Rectangular Collisions
    collideLeft        = ball.pos[0] - ball.radius < leftWall[0][0]        and ball.pos[1] >= leftWall[0][1]        and ball.pos[1] <= leftWall[1][1]
    collideRight       = ball.pos[0] + ball.radius > rightWall[0][0]       and ball.pos[1] >= rightWall[0][1]       and ball.pos[1] <= rightWall[1][1]
    collideTopLeft     = ball.pos[1] - ball.radius < topLeftWall[0][1]     and ball.pos[0] >= topLeftWall[0][0]     and ball.pos[0] <= topLeftWall[1][0]
    collideTopRight    = ball.pos[1] - ball.radius < topRightWall[0][1]    and ball.pos[0] >= topRightWall[0][0]    and ball.pos[0] <= topRightWall[1][0]
    collideBottomLeft  = ball.pos[1] + ball.radius > bottomLeftWall[0][1]  and ball.pos[0] >= bottomLeftWall[0][0]  and ball.pos[0] <= bottomLeftWall[1][0]
    collideBottomRight = ball.pos[1] + ball.radius > bottomRightWall[0][1] and ball.pos[0] >= bottomRightWall[0][0] and ball.pos[0] <= bottomRightWall[1][0]
    
    verticalCollision   = collideTopRight or collideTopLeft or collideBottomRight or collideBottomLeft
    horizontalCollision = collideLeft     or collideRight


    #Update Velocity
    ball.vel = (-ball.vel[0], ball.vel[1]) if horizontalCollision else ball.vel
    ball.vel = (ball.vel[0], -ball.vel[1]) if verticalCollision   else ball.vel

    #Update Position
    ball.pos = (leftWall[0][0]  + ball.radius, ball.pos[1]) if collideLeft  else ball.pos
    ball.pos = (rightWall[0][0] - ball.radius, ball.pos[1]) if collideRight else ball.pos
    ball.pos = (ball.pos[0], topLeftWall[0][1] + ball.radius) if collideTopLeft    or collideTopRight    else ball.pos
    ball.pos = (ball.pos[0], bottomLeftWall[0][1] - ball.radius) if collideBottomLeft or collideBottomRight else ball.pos
    
    #Check Triangular Collisions
    for wall in walls:
        c1x = ball.pos[0] - wall[0][0]
        c1y = ball.pos[1] - wall[0][1]

        radiusSqr = pow(ball.radius,2)
        c1sqr = pow(c1x,2) + pow(c1y,2) - radiusSqr
        
        e1x = wall[2][0] - wall[0][0]
        e1y = wall[2][1] - wall[0][1]
        
        k = c1x*e1x + c1y+e1y
        if k>0:
            len = pow(e1x,2) + pow(e1y,2)
            if k<len and c1sqr * len <= pow(k,2):
                ball.vel = (ball.vel[1], ball.vel[0])                
    for wall in walls:
        c1x = ball.pos[0] - wall[1][0]
        c1y = ball.pos[1] - wall[1][1]

        radiusSqr = pow(ball.radius,2)
        c1sqr = pow(c1x,2) + pow(c1y,2) - radiusSqr
        
        e1x = wall[3][0] - wall[1][0]
        e1y = wall[3][1] - wall[1][1]
        
        k = c1x*e1x + c1y+e1y
        if k>0:
            len = pow(e1x,2) + pow(e1y,2)
            if k<len and c1sqr * len <= pow(k,2):
                ball.vel = (ball.vel[1], ball.vel[0])                

    
                    


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
