import math
import random
import copy
TIMESTEP = .001
FRIC = -1000
MAXVEL = 10000
XDIMENTION = MAXVEL
YDIMENTION = XDIMENTION/2
BALLRADIUS = 113.636*2.1
QUARDCONVERT = 113.636


class Ball:
    def __init__(self, id, pos, color=(0, 0, 0), isStriped=False, vel=(0, 0), theta=0):
        self.id = id  # Ball number (0 = Q)
        self.pos = pos
        self.vel = vel
        self.isStriped = isStriped  # True/False


class BoardState:
    def __init__(self, balls):
        self.balls = balls


class Simulation:
    def __init__(self, boardStates):
        self.boardStates = boardStates


def isFinished(boardState):
    output = True
    for ball in boardState.balls:
        if(ball.vel[0] != 0 or ball.vel[1] != 0):
            output = False
    return output


def getQueBall(balls):
    for ball in balls:
        if ball.id == 0:
            return ball


def getBallNextState(ball):
    posx = ball.pos[0] + ball.vel[0] * TIMESTEP
    posy = ball.pos[1] + ball.vel[1] * TIMESTEP
    velx = ball.vel[0] - FRIC * TIMESTEP
    vely = ball.vel[1] - FRIC * TIMESTEP
    return Ball(ball.id, (posx, posy), ball.color, ball.isStriped, (velx, vely))


def isColliding(currentBalls):
    for ball in currentBalls:
        dx = ball.pos[0]


def getNextState(currentBoardState):
    preCollisionBalls = []
    for ball in currentBoardState:
        preCollisionBalls.append(getBallNextState(ball))


def simulate(vel, currentBoardState):
    time = 0
    startingBalls = copy.deepcopy(currentBoardState.balls)
    getQueBall(startingBalls).vel = vel
    boardStates = [BoardState(startingBalls)]

    while not isFinished(boardStates[time]):
        currentBoardState = boardStates[time]
        boardStates.append(getNextState(currentBoardState))
        time += 1


def movingBall(v, theta, boardState):
    output = [boardState]
    for ball in boardState:
        if ball.id == 0:
            ball.velocity = v
            ball.theta = theta
        ball.pos = (ball.pos[0]*QUARDCONVERT, ball.pos[1]*QUARDCONVERT)
    done = bool(v == 0)
    while not done:
        foundVel = False
        totalVel = 0
        for ball in boardState:
            if ball.velocity > 0:
                totalVel += ball.velocity
                foundVel = True
        done = not foundVel
        newBoardState = []
        for ball in boardState:
            if(ball.velocity != 0):
                theta = ball.theta
                initV = ball.velocity
                pos = ball.pos
                currentPos = [pos[0], pos[1]]

                xVel = initV*math.cos(math.radians(theta))
                yVel = initV*math.sin(math.radians(theta))

                deltaY = 0
                deltaX = 0

                if theta > 90 and theta < 270 and xVel > 0:
                    xVel = -xVel
                if theta > 180 and theta < 360 and yVel > 0:
                    yVel = -yVel

                deltaX = xVel*TIMESTEP+.5 * \
                    math.copysign(FRIC, -xVel)*math.pow(TIMESTEP, 2)
                deltaY = yVel*TIMESTEP+.5 * \
                    math.copysign(FRIC, -yVel)*math.pow(TIMESTEP, 2)

                #xVel = xVel + math.copysign(FRIC,-xVel)*TIMESTEP
                #yVel = yVel + math.copysign(FRIC,-yVel)*TIMESTEP

                currentPos[0] += deltaX
                currentPos[1] += deltaY

                if currentPos[0]-BALLRADIUS <= 0 and xVel < 0 or currentPos[0]+BALLRADIUS >= XDIMENTION and xVel > 0:
                    xVel = -xVel
                if currentPos[1]-BALLRADIUS <= 0 and yVel < 0 or currentPos[1]+BALLRADIUS >= YDIMENTION and yVel > 0:
                    yVel = -yVel
                velocity = 0
                collided = False
                newTheta = 0
                deleteBall = False
                for cBall in boardState:
                    if cBall != ball:
                        ibX = cBall.pos[0]
                        ibY = cBall.pos[1]
                        dist = math.sqrt(
                            math.pow(ibX-currentPos[0], 2)+math.pow(ibY-currentPos[1], 2))
                        if(cBall.id < 0 and dist < BALLRADIUS*2):
                            deleteBall = True
                            break
                        if dist < BALLRADIUS:
                            collided = True
                            cBall.theta = (math.degrees(math.atan2(
                                (ibY-currentPos[1]), (ibX-currentPos[0])))+360) % 360
                            currentPos[0], currentPos[1] = (cBall.pos[0]-math.cos(math.radians(
                                cBall.theta))*BALLRADIUS*1, cBall.pos[1]-math.sin(math.radians(cBall.theta))*BALLRADIUS*1)
                            #radiusincrese = 0
                            # while willCollide(currentPos[0],currentPos[1], ball,boardState) and radiusincrese<.5:
                            #    testang = -10
                            #    while willCollide(currentPos[0],currentPos[1], ball,boardState) and testang<10:
                            #        currentPos[0],currentPos[1] = (cBall.pos[0]-math.cos(math.radians(cBall.theta+testang))*BALLRADIUS*radiusincrese, cBall.pos[1]-math.sin(math.radians(cBall.theta+testang))*BALLRADIUS*radiusincrese)
                            #        testang+=.25
                            #    radiusincrese+=.1

                            inVelMag = math.sqrt(
                                math.pow(xVel, 2)+math.pow(yVel, 2))
                            if theta > cBall.theta:
                                newTheta = cBall.theta+90
                                velocity = abs(
                                    inVelMag*math.sin(math.degrees(theta-cBall.theta)))
                                cBall.velocity = abs(
                                    inVelMag*math.cos(math.degrees(theta-cBall.theta)))
                            elif theta == cBall.theta:
                                cBall.velocity = inVelMag
                                ball.velocity = 0
                                newTheta = theta
                            else:
                                newTheta = cBall.theta-90
                                velocity = abs(
                                    inVelMag*math.sin(math.degrees(theta+(cBall.theta))))
                                cBall.velocity = abs(
                                    inVelMag*math.cos(math.degrees(theta+(cBall.theta))))
                if not deleteBall:
                    if not collided:
                        velocity = math.sqrt(
                            math.pow(xVel, 2)+math.pow(yVel, 2))
                        angle = math.degrees(math.atan2(yVel, xVel))
                    else:
                        angle = newTheta
                    velocity = velocity+FRIC*TIMESTEP
                    newBall = Ball(
                        ball.id, (currentPos[0], currentPos[1]), ball.color, ball.isStriped, velocity)
                    newBoardState.append(newBall)
            else:
                newBall = Ball(
                    ball.id, (ball.pos[0], ball.pos[1]), ball.color, ball.isStriped, ball.velocity)
                newBoardState.append(newBall)
        output.append(newBoardState)
        boardState = newBoardState
    return output


def willCollide(x, y, ball, bs):
    for cBall in bs:
        if cBall != ball:
            ibX = cBall.pos[0]
            ibY = cBall.pos[1]
            dist = math.sqrt(math.pow(ibX-x, 2)+math.pow(ibY-y, 2))
            if dist < BALLRADIUS*1:
                return True
    return False
