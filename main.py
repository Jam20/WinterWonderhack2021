import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import random
from screeninfo import get_monitors
import math
import time

import bot
from engine import Ball
import engine

class GameManager:
    # Constructor
    def __init__(self):
        mnum = 1 if len(get_monitors()) > 1 else 0
        self.pixelInch = int((get_monitors()[mnum].width / 100))
        self.bumper = 6 * self.pixelInch
        self.boardWidth = self.pixelInch * 88
        self.boardHeight = self.pixelInch * 44
        self.screenWidth = self.boardWidth + self.bumper
        self.screenHeight = self.boardHeight + self.bumper
        self.ballRadius = 1.125 * self.pixelInch

        self.maxVel = 10000     # The max velocity in inches/second
        self.maxDraw = 22   # The max distance you can pull the poolstick back (in)

        self.screen = pygame.display.set_mode([self.screenWidth, self.screenHeight])
        self.clock = pygame.time.Clock()
        self.poolStick = PoolStick()

        self.numStripes = 7;
        self.numSolids = 7;

        self.balls = []
        self.run = True

        # Init pygame
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        pygame.display.set_caption("Amazing Pool Bot")

    # Game loop
    def runGame(self):
        self.initBalls()

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()


            while True:
                print("Player 1")
                # Player 1 turn - stripes
                (velocity, angle, playerX, playerY) = self.getPlayer()

                frames = engine.movingBall(velocity, angle, self.balls)

                for i in range(len(frames)):
                    if i%10 ==0:
                        frame = frames[i]
                        for ball in frame:
                            ball.pos = (ball.pos[0] / engine.QUARDCONVERT, ball.pos[1] / engine.QUARDCONVERT)

                        self.balls = frame
                        self.updateScreen(False)

                if self.getCue() == None:
                    for ball in self.balls:
                        if ball.id == 8:
                            ballparams = (0,  66, 22,    (255, 255, 255), False)
                            new = Ball(ballparams[0], ballparams[1], ballparams[2], ballparams[3], ballparams[4])
                            self.balls = [new] + self.balls

                    if (self.getCue() == None):
                        exit()
                


        pygame.quit()

    # Utiltiy that grabs the cue ball
    def getCue(self):
        for ball in self.balls:
            if ball.id == 0:
                return ball

            return None

    # Convert x board coordinate to pixel coordinate
    def xToPixel(self, distance):
         return distance * self.pixelInch + ((self.screenWidth - self.boardWidth) // 2)

    # Convert y board coordinate to pixel coordinate
    def yToPixel(self, distance):
        return self.screenHeight - (distance * self.pixelInch) - ((self.screenHeight - self.boardHeight) // 2)

    # Animation to strike ball
    def strike(self, playerX, playerY, angle):
        (cueX, cueY) = self.getCue().pos

        cueX = self.xToPixel(cueX)
        cueY = self.yToPixel(cueY)

        deltaX = int((playerX - cueX) // 10)
        deltaY = int((cueY - playerY) // 10)

        for i in range(10):
            self.screen.fill((255, 255, 255))
            self.drawTable()
            self.drawBalls()
        
            poolStickWidth = self.poolStick.rotCenter(angle).get_width()
            poolStickheight = self.poolStick.rotCenter(angle).get_height()

            if (0 <= angle and angle < 90):
                self.screen.blit(self.poolStick.rotCenter(angle), 
                        (playerX - poolStickWidth, playerY))

            elif (90 <= angle < 180):
                self.screen.blit(self.poolStick.rotCenter(angle), 
                        (playerX - deltaX, playerY))

            elif (180 <= angle < 270):
                self.screen.blit(self.poolStick.rotCenter(angle), 
                        (playerX, playerY - poolStickheight + deltaY))

            else:
                self.screen.blit(self.poolStick.rotCenter(angle), 
                       (playerX - poolStickWidth, playerY - poolStickheight))

            pygame.display.flip()

            playerX = playerX - deltaX
            playerY = playerY + deltaY


    # Gets the players input
    # Returns velocity and angle
    def getPlayer(self):
        hasGone = False

        while not hasGone:
            hasGone = pygame.mouse.get_pressed()[0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            # If the player has gone, calculate angle and velocity
            if(hasGone):
                playerX, playerY = pygame.mouse.get_pos()
                (cueX, cueY) = self.getCue().pos

                cueX = self.xToPixel(cueX)
                cueY = self.yToPixel(cueY)

                # Calc Distance and velocity
                distance =  self.getDistance(playerX, playerY, cueX, cueY)
                velocity = self.maxVel * (distance / (self.maxDraw * self.pixelInch))

                # Calc Angle
                angle = self.getAngle(playerX, playerY)

                return (round(velocity, 3), angle, playerX, playerY)

            self.updateScreen(True)

    # Draws simple cuestick
    def drawPoolStick(self):
        playerX, playerY = pygame.mouse.get_pos()
        (cueX, cueY) = self.getCue().pos

        cueX = self.xToPixel(cueX)
        cueY = self.yToPixel(cueY)

        # Referenc line from ball to tip of pool stick
        pygame.draw.line(self.screen, (0, 0, 0), (playerX, playerY), (cueX, cueY), 3)

        # Line used to aim
        playerXOpp = int(cueX - (playerX - cueX)) 
        playerYOpp = int(cueY - (playerY - cueY))
        pygame.draw.line(self.screen, (0, 0, 0), (cueX, cueY), (playerXOpp, playerYOpp), 3)
        
        # Place the CuestickAt the mouse
        angle = int(self.getAngle(playerX, playerY))

        poolStickWidth = self.poolStick.rotCenter(angle).get_width()
        poolStickheight = self.poolStick.rotCenter(angle).get_height()
        
        if (0 <= angle and angle < 90):
            self.screen.blit(self.poolStick.rotCenter(angle), 
                    (playerX - poolStickWidth, playerY))

        elif (90 <= angle < 180):
            self.screen.blit(self.poolStick.rotCenter(angle), 
                    (playerX, playerY))

        elif (180 <= angle < 270):
            self.screen.blit(self.poolStick.rotCenter(angle), 
                    (playerX, playerY - poolStickheight))

        else:
            self.screen.blit(self.poolStick.rotCenter(angle), 
                    (playerX - poolStickWidth, playerY - poolStickheight))

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

        angle = 0

        # Check if the user x or y is equal with cue x or y
        # If x similar
        if (cueX == userX):
            if (cueY < userY):
                angle = 270
            else:
                angle = 90

        # If y similar
        elif (cueY == userY):
            if (cueX > userX):
                angle = 180
            else:
                angle = 0

        # Check for Quadrant 1
        elif (cueX < userX and cueY > userY):
            angle = math.atan(abs(userY - cueY)/abs(userX - cueX))
            angle = angle * (180 / math.pi)

        # Check for Quadrant 2
        elif (cueX > userX and cueY > userY):
            angle = math.atan(abs(userY - cueY)/abs(userX - cueX))
            angle = angle * (180 / math.pi)
            angle = 90 + (90 - angle)

        # Check for Quadrant 3
        elif (cueX > userX and cueY < userY):
            angle = math.atan(abs(userY - cueY)/abs(userX - cueX))
            angle = angle * (180 / math.pi)
            angle = angle + 180

        # Check for Quadrant 4
        else:
            angle = math.atan(abs(userY - cueY)/abs(userX - cueX))
            angle = angle * (180 / math.pi)
            angle = 270 + (90 - angle)

        # Have to add 180 degrees to reverse direction
        return round((angle + 180) % 360, 3)

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

        cornerPockets = (4.5 * self.pixelInch) // 2
        centerPockets = (5 * self.pixelInch) // 2
        pockets = [(0, 44, cornerPockets), (44, 44, centerPockets), 
                (88, 44, cornerPockets), (0, 0, cornerPockets), 
                (44, 0, centerPockets), (88, 0, cornerPockets)] 

        for pocket in pockets:
            temp = Ball(-1, pocket[0], pocket[1], (0,0,0), False, 0, 0)
            self.balls.append(temp)

    # Updates the screen
    def updateScreen(self, isPlayer):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        self.screen.fill((255, 255, 255))
        self.drawTable()
        self.drawBalls()
        if( isPlayer ):
            if (self.getCue() != None):
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
            # -2 indicates not a playable ball
            self.drawBall(Ball(-2, pocket[0], pocket[1], (0, 0, 0), False), pocket[2])

        # Draw Felt
        pygame.draw.rect(self.screen, (0,255,0), (xOffset, yOffset, self.boardWidth, self.boardHeight))

    # Draws the balls
    # Coordinates are in inches, convert to pixels
    def drawBalls(self):
        for ball in self.balls:
            self.drawBall(ball, self.ballRadius)

    # Made seperate to call for drawing balls and pockets
    def drawBall(self, ball, radius):
        if(ball.id != -1):
            x = self.xToPixel(ball.pos[0])
            y = self.yToPixel(ball.pos[1])

            pygame.draw.circle(self.screen, ball.color, (x, int(y)), int(radius))
            
            # If it is a numbered ball
            if(ball.id > 0):
                # For circle for solids
                if not ball.isStriped:
                    pygame.draw.circle(self.screen, (255,255,255), (x, int(y)), int(radius / 2))

                # Draw crappy striped
                else:
                    pygame.draw.rect(self.screen, (255, 255, 255), (int(x - radius * 0.70), 
                        int(y - radius / 2), int(radius * 1.6), int(radius)))


            # Draw number on ball
            text = self.myfont.render(f"{ball.id}", False, (0, 0, 0))

            textXOffset = text.get_width() // 2
            textYOffset = text.get_height() // 2

            if(ball.id > 0):
                self.screen.blit(text, (x - textXOffset, int(y - textYOffset)))

class PoolStick:
    def __init__(self):
        self.image = pygame.image.load("poolCue.png")
    
    def getWidth(self):
        return self.image.get_width()

    def getHeight(self):
        return self.image.get_height()

    def getImage(self):
        return pygame.transform.scale(self.image, (self.getWidth() * 2, self.getHeight() * 2))

    def rotCenter(self, angle):
        return pygame.transform.rotozoom(self.getImage(), angle, 1)


if __name__ == "__main__":
    game = GameManager()
    game.runGame()







