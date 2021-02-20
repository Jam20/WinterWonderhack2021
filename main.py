import pygame
import sys
from math import *
import random

pygame.init()
width = 1900
height = 950
outerHeight = 400
margin = 30

background = (44, 105, 12)
brown = (122, 80, 3)

display = pygame.display.set_mode((width, height))
pygame.display.set_caption("8 Ball Pool")

clock = pygame.time.Clock()


# Ball Class
class Ball:
    def __init__(self, x, y, speed, color, angle, ballNum):
        self.x = x + radius
        self.y = y + radius
        self.color = color
        self.angle = angle
        self.speed = speed
        self.ballNum = ballNum
        self.font = pygame.font.SysFont("Agency FB", 10)

    # Draws Balls on Display Window
    def draw(self, x, y):
        pygame.draw.ellipse(display, self.color, (x - radius, y - radius, radius*2, radius*2))
        if self.color == black or self.ballNum == "cue":
            ballNo = self.font.render(str(self.ballNum), True, white)
            display.blit(ballNo, (x - 5, y - 5))
        else:
            ballNo = self.font.render(str(self.ballNum), True, black)
            if self.ballNum > 9:
                display.blit(ballNo, (x - 6, y - 5))
            else:
                display.blit(ballNo, (x - 5, y - 5))

# Pocket Class
class Pockets:
    def __init__(self, x, y, color):
        self.r = margin/2
        self.x = x + self.r + 10
        self.y = y + self.r + 10
        self.color = color

    # Draws the Pockets on Pygame Window
    def draw(self):
        pygame.draw.ellipse(display, self.color, (self.x - self.r, self.y - self.r, self.r*2, self.r*2))

def border():
    pygame.draw.rect(display, gray, (0, 0, width, 30))
    pygame.draw.rect(display, gray, (0, 0, 30, height))
    pygame.draw.rect(display, gray, (width - 30, 0, width, height))
    pygame.draw.rect(display, gray, (0, height - 30, width, height))


if __name__ == "__main__":
    display.fill(background)
    Pockets(display)
    pygame.display.update()
