import engine
from engine import ball
import math

boardState = 0

#return the touple containing the velocity and angle of the next AI move
def getAIMove(bs):
    boardState = bs

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
                y_onpath = slope*(compareball.x  - rad_normalized) + yrad_normalized
                
                # Can do better later on. Check to see if its on the line and in between the two balls
                if y_onpath + 2 > compareball.y and y_onpath - 2 < compareball.y:
                    if compareball.x >= xrad_normalized and compareball.x <= ball_cord.x:
                        output_balls.remove(ball_cord)
                    elif compareball.x <= xrad_normalized and compareball.x >= ball_cord.x:
                        output_balls.remove(ball_cord)
            
    
    

                    



# gets the possible velocity and angle touples for making a ball into a pocket defined by pocketID
def getPaths(pocketID):

#gets the score associated with a possible move from the engine simulation
def getScore(v, theta):  
