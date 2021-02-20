import engine
boardState = 0

#return the touple containing the velocity and angle of the next AI move
def getAIMove(bs):
    boardState = bs

#returns a list of balls that can hit the inputted ball and result in velocity v and angle theta
def getPossibleBalls(ball, v, theta):

#gets the possible velocity and angle touples for making a ball into a pocket defined by pocketID
def getPaths(pocketID):

#gets the score associated with a possible move from the engine simulation
def getScore(v, theta):
