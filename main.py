import pygame
import random
import os
from screeninfo import get_monitors

import bot
from engine import Ball

class GameManager:
    # Constructor
    def __init__(self):
        mnum = 1 if len(get_monitors()) > 1 else 0
        self.pixelInch = int((get_monitors()[mnum].width / 100))
        self.bumper = 6 * self.pixelInch
        self.boardWidth = self.pixelInch * 88;
        self.boardHeight = self.pixelInch * 44;
        self.screenWidth = self.boardWidth + self.bumper
        self.screenHeight = self.boardHeight + self.bumper
        self.ballRadius = 1.125 * self.pixelInch;

        self.maxVel = 5     # The max velocity in inches/second
        self.maxDraw = 22   # The max distance you can pull the poolstick back (in)

        self.screen = pygame.display.set_mode([self.screenWidth, self.screenHeight])
        self.clock = pygame.time.Clock()

        self.balls = []

        # Init pygame
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        pygame.display.set_caption("Amazing Pool Bot")

    # Game loop
    def run(self):
        run = True;

        self.initBalls()

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            self.getPlayer()

            run = False

            self.updateScreen(False)

    pygame.quit()

    # Utiltiy that grabs the cue ball and the possibility of a scratch
    def getCue(self):
        for ball in self.balls:
            if ball.id == 0:
                return ball

    # Convert x board coordinate to pixel coordinate
    def xToPixel(self, distance):
         return distance * self.pixelInch + ((self.screenWidth - self.boardWidth) // 2)

    # Convert y board coordinate to pixel coordinate
    def yToPixel(self, distance):
        return self.screenHeight - (distance * self.pixelInch) - ((self.screenHeight - self.boardHeight) // 2)

    # Gets the players input
    # Returns velocity and angle
    def getPlayer(self):
        hasGone = False

        while not hasGone:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    bashGone = True

            hasGone = pygame.mouse.get_pressed()[0]

            # If the player has gone, calculate angle and velocity
            if(hasGone):
                playerX, playerY = pygame.mouse.get_pos()
                (cueX, cueY) = self.getCue().pos

                cueX = self.xToPixel(cueX)
                cueY = self.yToPixel(cueY)

                # Calc Distance
                distance =  self.getDistance(playerX, playerY, cueX, cueY)
                velocity = self.maxVel * (distance / (self.maxDraw * self.pixelInch))

                # Calc Angle
                angle = self.getAngle(playerX, playerY)

            self.updateScreen(True)

    # Draws simple cuestick
    def drawPoolStick(self):
        playerX, playerY = pygame.mouse.get_pos()
        (cueX, cueY) = self.getCue().pos

        cueX = self.xToPixel(cueX)
        cueY = self.yToPixel(cueY)

        pygame.draw.line(self.screen, (255,25,22), (playerX, playerY), (cueX, cueY), 3)

    # Get distance between two points
    # Will restrict distance if it is past maxDraw, useful for mapping force 
    def getDistance(self, x1, y1, x2, y2):
        maxDistancePixels = self.maxDraw * self.pixelInch

        distance = ((x2 - x1)**2 + (y2 - y1)**2)**.5

        if (distance > maxDistancePixels):
            return maxDistancePixels
        
        else:
            return distance
        

    # Get the angle of the line draw from cue tip to cue ball
    def getAngle(self, userX, userY):
        (cueX, cueY) = self.getCue().pos

        cueX = self.xToPixel(cueX)
        cueY = self.yToPixel(cueY)

        angle = None

        # Check if the user x or y is equal with cue x or y
        # If x similar
        if (cueX == userX):
            pass

        # If y similar
        elif (cueY == userY):
            pass

        print(angle)
        return angle

    # Sets the balls
    def initBalls(self):
        # (id, color, isStriped)
        ballparams = [(0,  66, 22,    (255, 255, 255), False),  # Cue Ball
                      (1,  22, 22,    (242, 230, 0),   False),
                      (2,  20, 23.15, (12, 23, 237),   False), 
                      (3,  20, 20.85, (212, 26, 13),   False), 
                      (4,  18, 24.3,  (117, 33, 219),  False), 
                      (5,  18, 22,    (242, 149, 0),   False), 
                      (6,  18, 19.7,  (27, 117, 2),    False), 
                      (7,  16, 25.45, (179, 30, 70),   False), 
                      (8,  16, 23.15, (0, 0, 0),       False), 
                      (9,  16, 20.85, (242, 230, 0),   True), 
                      (10, 16, 18.55, (12, 23, 237),   True), 
                      (11, 14, 26.6,  (212, 26, 13),   True), 
                      (12, 14, 24.3,  (117, 33, 219),  True), 
                      (13, 14, 22,    (242, 149, 0),   True), 
                      (14, 14, 19.7,  (27, 117, 2),    True), 
                      (15, 14, 17.4,  (179, 30, 70),   True)]

        for param in ballparams:
            temp = Ball(param[0], param[1], param[2], param[3], param[4])
            self.balls.append(temp)

    # Updates the screen
    def updateScreen(self, isPlayer):
        self.screen.fill((255, 255, 255))
        self.drawTable()
        self.drawBalls()
        if( isPlayer ):
            self.drawPoolStick()
        pygame.display.flip()

    # Draws the table
    def drawTable(self):
        xOffset = (self.screenWidth - self.boardWidth) // 2
        yOffset = (self.screenHeight - self.boardHeight) // 2

        # Draw Wood Surrounding
        pygame.draw.rect(self.screen, (210,105,30), 
                (0, 0, self.boardWidth + self.bumper, self.boardHeight + self.bumper))

        # Draw Holes
        # Pocket coords from top right to top left and bottom right to bottom left
        cornerPockets = (4.5 * self.pixelInch) // 2
        centerPockets = (5 * self.pixelInch) // 2
        pockets = [(0, 44, cornerPockets), (44, 44, centerPockets), 
                (88, 44, cornerPockets), (0, 0, cornerPockets), 
                (44, 0, centerPockets), (88, 0, cornerPockets)] 

        for pocket in pockets:
            # -1 indicates not a playable ball
            self.drawBall(Ball(-1, pocket[0], pocket[1], (0, 0, 0), False), pocket[2])

        # Draw Felt
        pygame.draw.rect(self.screen, (0,255,0), (xOffset, yOffset, self.boardWidth, self.boardHeight))

    # Draws the balls
    # Coordinates are in inches, convert to pixels
    def drawBalls(self):
        for ball in self.balls:
            self.drawBall(ball, self.ballRadius)

    # Made seperate to call for drawing balls and pockets
    def drawBall(self, ball, radius):

        x = self.xToPixel(ball.pos[0])
        y = self.yToPixel(ball.pos[1])

        pygame.draw.circle(self.screen, ball.color, (x, y), radius)
        
        # If it is a numbered ball
        if(ball.id > 0):
            # For circle for solids
            if not ball.isStriped:
                pygame.draw.circle(self.screen, (255,255,255), (x, y), radius / 2)

            # Draw crappy striped
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), (x - radius * 0.70, 
                    y - radius / 2, radius * 1.6, radius))


        # Draw number on ball
        text = self.myfont.render(f"{ball.id}", False, (0, 0, 0))

        textXOffset = text.get_width() // 2
        textYOffset = text.get_height() // 2

        self.screen.blit(text, (x - textXOffset, y - textYOffset))


if __name__ == "__main__":
    game = GameManager()
    game.run()







