import math
import vector
TIMESTEP = .01
FRIC = -2500
MAXVEL = 10000
XDIMENTION = MAXVEL
YDIMENTION = XDIMENTION/2
BALLRADIUS = 2.25/44*YDIMENTION
QUARDCONVERT = 113.636

class Ball:
    def __init__(self, id, x, y, color, isStriped, velocity=0, theta=0):
        self.id = id # Ball number (0 = Q)
        self.pos = (x, y)
        self.color = color # RGB values
        self.isStriped = isStriped # True/False
        self.velocity = velocity
        self.theta = theta


def movingBall(v,theta, boardState):
    output = [boardState]
    for ball in boardState:
        if ball.id == 0:
            ball.velocity = v
            ball.theta = theta
        ball.pos = (ball.pos[0]*QUARDCONVERT, ball.pos[1]*QUARDCONVERT)    
    done = bool(v==0)
    while not done:
        foundVel= False
        totalVel = 0
        for ball in boardState:
            if ball.velocity>0:
                totalVel += ball.velocity
                foundVel = True
        done = not foundVel
        for ball in boardState:
            if(ball.velocity!=0):
                theta = ball.theta
                initV = ball.velocity
                pos = ball.pos
                currentPos = [pos[0],pos[1]]

                xVel = initV*math.cos(math.radians(theta))
                yVel = initV*math.sin(math.radians(theta))

                deltaY=0
                deltaX=0

                if theta>90 and theta<270 and xVel>0:
                    xVel = -xVel
                if theta>180 and theta<360 and yVel>0:
                    yVel = -yVel

                deltaX = xVel*TIMESTEP+.5*math.copysign(FRIC,-xVel)*math.pow(TIMESTEP,2)
                deltaY = yVel*TIMESTEP+.5*math.copysign(FRIC,-yVel)*math.pow(TIMESTEP,2)

                xVel = xVel + math.copysign(FRIC,-xVel)*TIMESTEP
                yVel = yVel + math.copysign(FRIC,-yVel)*TIMESTEP

                currentPos[0] += deltaX
                currentPos[1] += deltaY

                if currentPos[0]-BALLRADIUS<=0 and xVel<0 or currentPos[0]+BALLRADIUS>=XDIMENTION and xVel>0 :
                    xVel = -xVel
                if currentPos[1]-BALLRADIUS<=0 and yVel<0 or currentPos[1]+BALLRADIUS>=YDIMENTION and yVel>0 :
                    yVel = -yVel

                for cBall in boardState:
                    if cBall != ball:
                        ibX = cBall.pos[0]
                        ibY = cBall.pos[1]
                        dist = math.sqrt(math.pow(ibX-currentPos[0],2)+math.pow(ibY-currentPos[1],2))
                        if dist<2*BALLRADIUS:
                            cBall.theta = math.degrees(math.atan2((ibY-currentPos[1]),(ibX-currentPos[0])))
                            ball.pos = (cBall.pos[0]-math.cos(math.radians(cBall.theta))*2*BALLRADIUS, cBall.pos[1]-math.sin(math.radians(cBall.theta))*2*BALLRADIUS)
                            adjTheta=0
                            inVelMag = math.sqrt(math.pow(xVel,2)+math.pow(yVel,2))
                            if theta>cBall.theta:
                                newTheta = cBall.theta+90
                                adjTheta = cBall.theta-90
                                cBall.velocity = inVelMag*math.sin(math.degrees(adjTheta))
                                ball.velocity = inVelMag*math.cos(math.degrees(adjTheta))
                            elif theta == cBall.theta:
                                cBall.velocity  = inVelMag
                                ball.velocity   = 0
                                newTheta = theta
                            else:
                                newTheta = cBall.theta-90
                                adjTheta = newTheta-90
                                ball.velocity = inVelMag*math.sin(math.degrees(adjTheta))
                                cBall.velocity = inVelMag*math.cos(math.degrees(adjTheta))

                ball.pos = (currentPos[0],currentPos[1])
                ball.velocity = ball.velocity+FRIC*TIMESTEP
                ball.theta = math.degrees(math.atan2(yVel,xVel))
        outState = boardState
        output.append(outState)
    for ball in boardState:
        ball.theta = 0
        ball.velocity = 0
        ball.pos = (ball.pos[0]/QUARDCONVERT, ball.pos[1]/QUARDCONVERT)
    return output

 


            

        
        
