import pygame
import bot


class GameManager:
    # Constructor
    def __init__(self):
        self.pixelInch = 18
        self.screenWidth = 1760;
        self.screenHeight = 880;
        self.boardWidth = self.pixelInch * 88;
        self.boardHeight = self.pixelInch * 44;

    # Game loop
    def run(self):
        run = True;

        screen = pygame.display.set_mode([self.screenWidth, self.screenHeight])

        pygame.init()

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

        pygame.quit()

    # Sets the balls
    def initBalls(self):
        pass

    # Draws the table
    def drawTable(self):
        pass

    # Draws the balls
    def drawBalls(self, balls):
        pass

    # Gets the players input
    def getPlayer(self):
        pass

if __name__ == "__main__":
    game = GameManager()
    game.run()
