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
    elif(traj[0]> 1000):
        return 0

    #gets all of the balls that can hit the current ball and give it the desired trajectory
    balls, trajs = getPossibleBalls(ball, traj[0], traj[1])
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
