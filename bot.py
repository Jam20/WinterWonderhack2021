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
    bRadius = 2
    output_poolballs = []
    output_poolballsVelocity = []




    #Cheater method to combat a dividing by zero clause
    if theta == 90 or theta == 270:
        theta +=.00001

    #Flippin the desired output angle to find the Tangent line on the side of the 
    #ball that the other balls will hit
    if theta >= 180:
        theta_new = theta - 180
    else:
        theta_new = theta + 180
    ###################################

    #Turned into np.Array touple. Look so see if this is right
    xyRadPoint = [(2*bRadius) * math.cos(math.radians(theta_new)), (2*bRadius) * math.sin(math.radians(theta_new))]
    
    #Print Function to check
    #print(xyRadPoint)
    ###################################

    #Updating the position of where to hit the q ball, Tangent line on side of ball needed to be hit
    xyRadPoint[0], xyRadPoint[1] = xyRadPoint[0] + ball.pos[0], xyRadPoint[1] + ball.pos[1]

    ####ATANTOO

    #####################################################################################
    #Finding the m of the point slope and the Tangent slope
    #in the form of y = m*(x - x1) + y1

    rad_gradient = (xyRadPoint[1] - ball.pos[1])/(xyRadPoint[0] - ball.pos[0])
    tangent_grad = -1/rad_gradient
    #####################################


    # Finding all the balls on the correct side of the tangent line
    for poolball in boardState:
        tan_ypos = tangent_grad * (poolball.pos[0] - xyRadPoint[0]) + xyRadPoint[1]

        if theta < 180 and tan_ypos > poolball.pos[1]:
            output_poolballs.append(poolball)
        elif theta > 180 and tan_ypos < poolball.pos[1]:
            output_poolballs.append(poolball)
            

    # Determining if a ball is on the path of the possible pool ball to hit
    for ball_cord in output_poolballs:
        #Getting the slope of the balls for the traveling path line
        slope = (ball_cord.pos[1] - xyRadPoint[1]) / (ball_cord.pos[0] - xyRadPoint[0])


        for compareball in output_poolballs:
            if ball_cord != compareball or compareball != ball:
                #Finds the projected traveling path
                y_onpath = slope*(compareball.pos[0]  - xyRadPoint[0]) + xyRadPoint[1]
                
                #############################################################
                #HELP ITS FAILING!! WHY IS THE BALL NOT IN THE LIST ANYMORE!!
                # IF NEEDE YOU CAN CHANGE TO CHECKING IF THE PROJECTED POINT IS +- THE ACTUAL POINT OF THE INTERFERENCE BALL
                #############################################################
                if y_onpath + bRadius >= compareball.pos[1] >= y_onpath - bRadius:
                #Possibility for change
                #############################################################

                    #For loops to set what x/y cordinate of the two balls for the path set on
                    if ball_cord.pos[0] > xyRadPoint[0]:
                        higherx = ball_cord.pos[0]
                        lowerx = xyRadPoint[0]
                    else:
                        higherx = xyRadPoint[0]
                        lowerx = ball_cord.pos[0]
                    
                    if ball_cord.pos[1] > xyRadPoint[1]:
                        highery = ball_cord.pos[1]
                        lowery = xyRadPoint[1]
                    else:
                        highery = xyRadPoint[1]
                        lowery = ball_cord.pos[1]
                    #############################################################
    

                    if lowerx <= compareball.pos[0] <= higherx and lowery <= compareball.pos[1] <= highery:
                        #############################################################
                        #HELP ITS FAILING!! WHY IS THE BALL NOT IN THE LIST ANYMORE!!
                        #############################################################
                        try:
                            output_poolballs.remove(ball_cord)
                        except ValueError:
                            print('Remove from list failed', ball_cord.id, ball_cord.pos[0], ball_cord.pos[1])
                            for i in output_poolballs:
                                print(i.id, i.pos[0], i.pos[1])
                        #############################################################
                        #HELP ITS FAILING!! WHY IS THE BALL NOT IN THE LIST ANYMORE!!
                        #############################################################


    #Math function to find the needed Velocity to hit ball into hole
    for ball_cordhelp in output_poolballs:
        hypotVelocity = v / math.sin(math.atan((xyRadPoint[1] - ball_cordhelp.pos[1])/(xyRadPoint[0] - ball_cordhelp.pos[0])))
        output_poolballsVelocity.append(hypotVelocity)
    
    return output_poolballs, output_poolballsVelocity


#gets the possible velocity and angle touples for making a ball into a pocket defined by pocketID
def getPocketPaths(pocketID):

    #defines the pocket as a ball 
    pocketBall = Ball(-pocketID, pocketID,0)

    #gets the list of balls and their nessesary trajectories that can hit the pocket
    balls, trajs = getPossibleBalls(pocketBall, 0, 0)
    
    paths = []
    
    #loops through each of the balls 
    for i in range(len(balls)):
        if(balls[i].id != 0 or int(balls[i].id / 8) != team): #if the ball is the que or an enemy ball remove it
            del balls[i]
            del trajs[i]
    
    
    with concurrent.futures.ProcessPoolExecutor as executor:
        results = executor.map(getPaths,balls,trajs) #create a thread for each of the balls that appends to a list when it finishes if valid
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

    #gets a virtual ball that can hit the current ball with the trajectory that is tangent to a wall
    wallBall=getWallBall(ball, traj)
    if wallBall.id !=-1: #if it is a valid wall ball
        balls.append(wallBall) #add it to the balls list

        #calculate the angle based of the wall the wallball is on and the desired angle
        x= traj[0]*math.sin(math.radians(traj[1]))
        y= traj[0]*math.cos(math.radians(traj[1])) 
        if wallBall.pos[0] == engine.BALLRADIUS or wallBall.pos[0] == 500-engine.BALLRADIUS:
            x=-x
        else:
            y=-y
        wallBallTheta = math.degrees(math.atan(y/x))
        #add the angle and velocity magnitude to the list
        trajs.append((traj[0], wallBallTheta))
   
    paths = []

    #if the ball is an enemy ball remove the que ball from the possible balls because can't hit enemy ball with que ball first
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

    #simulates the motion using the games physics engine
    bs = engine.simulate(0, v, theta)
    score = 0
    
    #loops through the all the balls in the final board state
    for ball in boardState:

        #looks for which balls are not in the new boards state aka scored
        if not (ball in bs):

            #based on which ball is scored set the score for that ball
            roundScore = 0
            if(int(ball.id / 8) == team):
                roundScore = 1
                if(ball.id == 0):
                    roundScore = -1
                if(ball.id == 8):
                    roundScore = -10
            else:
                roundScore = -1
        #total the score for each ball scored
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
