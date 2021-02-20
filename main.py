import pygame
import bot
from engine import Ball


class GameManager:
    # Constructor
    def __init__(self):
        self.pixelInch = 18
        self.bumper = 6 * self.pixelInch
        self.boardWidth = self.pixelInch * 88;
        self.boardHeight = self.pixelInch * 44;
        self.screenWidth = self.boardWidth + self.bumper
        self.screenHeight = self.boardHeight + self.bumper
        self.ballRadius = 1.125 * self.pixelInch;
        self.screen = pygame.display.set_mode([self.screenWidth, self.screenHeight])
        self.balls = []

    # Game loop
    def run(self):
        run = True;

        self.initBalls()

        pygame.init()
        pygame.display.set_caption("Amazing Pool Bot")

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False


            self.updateScreen()

    pygame.quit()

    # Sets the balls
    def initBalls(self):
        self.balls.append(Ball(1, 44, 22, (255, 0, 0), False))

    # Updates the screen
    def updateScreen(self):
        self.screen.fill((255, 255, 255))
        self.drawTable()
        self.drawBalls()
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
            self.drawBall(Ball(0, pocket[0], pocket[1], (0, 0, 0), False), pocket[2])

        # Draw Felt
        pygame.draw.rect(self.screen, (0,255,0), (xOffset, yOffset, self.boardWidth, self.boardHeight))

    # Draws the balls
    # Coordinates are in inches, convert to pixels
    def drawBalls(self):
        for ball in self.balls:
            self.drawBall(ball, self.ballRadius)

    # Made seperate to call for drawing balls and pockets
    def drawBall(self, ball, radius):
        xOffset = (self.screenWidth - self.boardWidth) // 2
        yOffset = (self.screenHeight - self.boardHeight) // 2

        x = (ball.pos[0] * self.pixelInch) + xOffset
        y = self.screenHeight - yOffset - ball.pos[1] * self.pixelInch

        pygame.draw.circle(self.screen, ball.color, (x, y), radius)

    # Gets the players input
    def getPlayer(self):
        pass

if __name__ == "__main__":
    game = GameManager()
    game.run()


















