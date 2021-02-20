import math
import engine
import concurrent.futures
from engine import Ball
team = 0
boardState = []
#return the touple containing the velocity and angle of the next AI move
def getAIMove(bs):
    boardState = bs
    bestScore = 0
    output = (0,0)

    #loops through each pocket
    for i in range(6):

        #gets the paths possible for the pocket
        paths = getPocketPaths(i)

        #checks each path in the game simulation and chooses the path with the highest score
        for path in paths:
            score = getScore(path[0],path[1])
            if(score>bestScore):
                output = (path[0],path[1])

    return output

#returns a list of balls that can hit the inputted ball and result in velocity v and angle theta
def getPossibleBalls(ball, v, theta):
    output_poolballs = []

    if v <  180:
        projected_abovetan = False
    else:
        projected_abovetan = True

    theta_new = v + 180
    xrad = 2 * math.cos(theta_new  * (math.pi/180))
    yrad = 2 * math.sin(theta_new*(math.pi/180))

    # Check how ball x positions are stored
    xrad_normalized = xrad + ball.x
    yrad_normalized = yrad + ball.y

    # determining the gradient of the radius
    rad_gradient = (yrad_normalized - ball.y)/(xrad_normalized - ball.y)
    tangent_grad = -1/rad_gradient
    

    # Finding all the balls on the correct side of the tangent line
    for poolballs in boardState:
        tan_ypos = tangent_grad * (poolballs.x - xrad_normalized) + yrad_normalized
        
        if tan_ypos > poolballs.y:
            above_tanline = False
        else:
            above_tanline = True

        if projected_abovetan == False:
            if above_tanline == False:
                output_poolballs.append(poolballs)
        else:
            if above_tanline == True:
                output_poolballs.append(poolballs)              
        

    # Determining if a ball is on the path of the possible pool ball to hit
    for ball_cord in output_poolballs:
        slope = (ball_cord.y - yrad_normalized) / (ball_cord.x - xrad_normalized)
        for compareball in output_poolballs:
            if ball_cord != compareball:
                y_onpath = slope*(compareball.x  - xrad_normalized) + yrad_normalized
                
                # Can do better later on. Check to see if its on the line and in between the two balls
                if y_onpath + 2 > compareball.y and y_onpath - 2 < compareball.y:
                    if compareball.x >= xrad_normalized and compareball.x <= ball_cord.x:
                        output_poolballs.remove(ball_cord)
                    elif compareball.x <= xrad_normalized and compareball.x >= ball_cord.x:
                        output_poolballs.remove(ball_cord)
            
    
    

                    



    return

#gets the possible velocity and angle touples for making a ball into a pocket defined by pocketID
def getPocketPaths(pocketID):

    #defines the pocket as a ball 
    pocketBall = Ball(-pocketID, pocketID,0)

    #gets the list of balls and their nessesary trajectories that can hit the pocket
    balls, trajs = getPossibleBalls(pocketBall, 0, 0)
    
    paths = []
    
    #loops through each of the balls 
    for i in range(len(balls)):
        if(balls[i].id != 0 or int(balls[i].id / 8) != team): #if the ball is not the que or an enemy ball
            del balls[i]
            del trajs[i]
    with concurrent.futures.ProcessPoolExecutor as executor:
        results = executor.map(getPaths,balls,trajs)
        for result in results:
            if(results != 0):
                paths.append(result)
    return paths  

#gets the possible velocity and angle touples for making the given ball achive the given trajectory             
def getPaths(ball, traj):

    #base case too long of a path or the ball is the que ball
    if(ball.id == 0):
        return (ball, traj)
    elif(traj[0]> 10):
        return 0

    #gets all of the balls that can hit the current ball and give it the desired trajectory
    balls, trajs = getPossibleBalls(ball, traj[0], traj[1])
    wallBall=getWallBall(ball, traj)
    if wallBall.id !=-1:
        balls.append(wallBall)
        x= traj[0]*math.sin(math.radians(traj[1]))
        y= traj[0]*math.cos(math.radians(traj[1]))
        if wallBall.pos[0] == engine.BALLRADIUS or wallBall.pos[0] == 500-engine.BALLRADIUS:
            x=-x
        else:
            y=-y
        wallBallTheta = math.degrees(math.atan(y/x))
        trajs.append((traj[0], wallBallTheta))
   
    paths = []

    if int(ball.id / 8) != team:
        for i in range(len(balls)):
            if(ball.id == 0):
                del balls[i]
                del trajs[i]
                
    #loops through the balls and calls the function recursivly 
    with concurrent.futures.ProcessPoolExecutor as executor:
        results = executor.map(getPaths,balls,trajs)
        for result in results:
            if(results != 0):
                paths.append(result)
    return paths

#gets the score associated with a possible move from the engine simulation
def getScore(v, theta):

    bs = engine.simulate(0, v, theta)
    score = 0
    for ball in boardState:
        if not (ball in bs):
            roundScore = 0
            if(int(ball.id / 8) == team):
                roundScore = 1
                if(ball.id == 0):
                    roundScore = -1
                if(ball.id == 8):
                    roundScore = -10
            else:
                roundScore = -1
        score += roundScore
    return score

def getWallBall(ball, traj):
    outputBall = Ball(ball.id,0,0)
    thetaFinal = (traj[1]+180)%360
    thetaOne    = math.degrees(      math.atan((500-engine.BALLRADIUS-ball.pos[1])/(1000-engine.BALLRADIUS-ball.pos[0])))
    thetaTwo    = math.degrees(180 - math.atan((500-engine.BALLRADIUS-ball.pos[1])/(ball.pos[0]-engine.BALLRADIUS)))
    thetaThree  = math.degrees(180 + math.atan((ball.pos[1]-engine.BALLRADIUS)/(ball.pos[0]-engine.BALLRADIUS)))
    thetaFour   = math.degrees(360 - math.atan((ball.pos[1]-engine.BALLRADIUS)/(1000-engine.BALLRADIUS-ball.pos[0])))
    if(thetaFinal>thetaOne and thetaFinal<thetaTwo): #Top wall
        if(thetaFinal<90):
            outputBall = Ball(ball.id, ball.pos[0]+math.tan(math.radians(thetaFinal))/(500-engine.BALLRADIUS-ball.pos[1]),  500-engine.BALLRADIUS)
        else:
            outputBall = Ball(ball.id, ball.pos[0]-math.tan(math.radians(180-thetaFinal))/(500-ball.pos[1]),                500-engine.BALLRADIUS)

    elif(thetaFinal>thetaTwo and thetaFinal<thetaThree): #Left wall
        if(thetaFinal<180):
            outputBall = Ball(ball.id, 0    +engine.BALLRADIUS, ball.pos[1] + math.tan(math.radians(180-thetaFinal))*(ball.pos[0]-engine.BALLRADIUS))
        else:
            outputBall = Ball(ball.id, 0    -engine.BALLRADIUS, ball.pos[1] - math.tan(math.radians(thetaFinal-180))*(ball.pos[0]-engine.BALLRADIUS))

    elif(thetaFinal>thetaThree and thetaFinal<thetaFour): # Bottom wall
        if(thetaFinal<270):
            outputBall = Ball(ball.id,      ball[0]-math.tan(math.radians(thetaFinal-180))/(ball.pos[1]-engine.BALLRADIUS), 0+engine.BALLRADIUS)
        else:
            outputBall = Ball(ball.id,      ball[0]+math.tan(math.radians(360-thetaFinal))/(ball.pos[1]-engine.BALLRADIUS), 0+engine.BALLRADIUS)

    elif(thetaFinal<thetaOne or thetaFinal>thetaFour): #Right wall
        if(thetaFinal<90):
            outputBall = Ball(ball.id, 1000 -engine.BALLRADIUS, ball.pos[1]-math.tan(math.radians(360-thetaFinal))*(ball.pos[0]-engine.BALLRADIUS))
        else:
            outputBall = Ball(ball.id, 1000 +engine.BALLRADIUS, ball.pos[1]-math.tan(math.radians(thetaFinal))*(ball.pos[0]-engine.BALLRADIUS))

    else:
        outputBall = Ball(-1, 0, 0)
    if(outputBall.pos[0]<engine.BALLRADIUS or outputBall.pos[1]<engine.BALLRADIUS or outputBall.pos[0]>1000-engine.BALLRADIUS or outputBall.pos[1]>500-engine.BALLRADIUS):
        outputBall = Ball(-1,0,0)
    return outputBall
