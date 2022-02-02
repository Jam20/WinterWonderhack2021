import math
from typing import List
import numpy as np

WALLS: np.ndarray = np.array([
    [[0,      9.5],   [0,     117],   [-5.3,   4.25],   [-5.3,  122.5]],
    [[254.3,  9.5],   [254.3, 117],   [259.5,  4.25],   [259.5, 123]],
    [[8,      -.1],   [116,   -.1],   [2.25,   -5.3],   [118.2, -5.3]],
    [[134.75, -.1],   [243.9, -.1],   [132.25, -5.3],   [249.5, -5.3]],
    [[8.3,    127.25],   [116.5, 127.25],   [2.75,   132.4],   [118.7, 132.4]],
    [[134.75, 127.25],   [243.9, 127.25],   [132.25, 132.4],   [249.5, 132.4]],
])

POCKETS : np.ndarray = np.array([
    [ [-5.3,   4.25], [2.25,   -5.3]  ],
    [ [118.2, -5.3 ], [132.25, -5.3]  ],
    [ [259.5,  4.25], [249.5, -5.3 ]  ],
    [ [-5.3,  122.5], [2.75,   132.4] ],
    [ [118.7, 132.4], [132.25, 132.4] ],
    [ [259.5, 123  ], [249.5, 132.4 ] ],    
])

DECELERATION = .2


class Ball:
    def __init__(self, pos: tuple[float, float], vel: tuple[float, float]):
        self.radius = 5
        self.pos: np.ndarray = np.array(pos, dtype='f')
        self.vel: np.ndarray = np.array(vel, dtype='f')


class Board:
    def __init__(self):
        self.width = 254
        self.height = 127
        self.thickness = 19


class Pocket:
    def __init__(self):
        self.radius = 7.75


def update_ball(dt: float, ball: Ball):
    ball.pos += ball.vel*dt  # Update position based on velocity
    # Calculate deceleration based on current velocity
    decel = ball.vel*(1-DECELERATION)*dt
    ball.vel = ball.vel-decel  # Update velocity based on amount of deceleration
    # Zero out the velocity if low enough
    ball.vel *= 0.0 if np.abs(ball.vel).sum() < 0.1 else 1.0


def isVert(pointA, pointB):
    return pointA[0] == pointB[0]


def check_wall_collisions(ball: Ball):
    for wall in WALLS:
        lines= np.array([wall[:2], wall[2:], wall[::2], wall[1::2]])
        for line in lines:
            if is_colliding_with_line(ball, line):
                respond_to_collision(ball, line)
                return


def respond_to_collision(ball: Ball, line: np.ndarray):
    #gets the unit vector for the line as well as the unit vector perpendicular to the line
    line_unit_vector = (line[1]-line[0])/np.linalg.norm(line[1] - line[0])
    line_unit_orthoNormal = np.array([-line_unit_vector[1], line_unit_vector[0]])

    #updates the velocity by flipping it over the line
    p = 2*ball.vel.dot(line_unit_orthoNormal)
    ball.vel -= p*line_unit_orthoNormal
     

def is_colliding_with_line(ball: Ball, line: np.ndarray):
    #get the line as a vector
    lineVector: np.ndarray = line[1] - line[0]

    #get coefficients for quadratic equation 
    a = lineVector.dot(lineVector)
    b = 2 * lineVector.dot(line[0] - ball.pos)
    c = line[0].dot(line[0]) + ball.pos.dot(ball.pos) - 2 * \
        line[0].dot(ball.pos) - ball.radius**2

    #get discriminant section of quadratic equation if < 0 ball misses completely
    disc = b**2 - 4 * a * c
    if disc < 0:
        return False

    #gets if the section of the line we care about is in the circle
    disc_sqrt = np.sqrt(disc)
    t1 = (-b + disc_sqrt) / (2 * a)
    t2 = (-b - disc_sqrt) / (2 * a)
    if 0 <= t1 <= 1 or 0 <= t2 <= 1:
        return True
    else:
        return False


def check_ball_collisions(ball: Ball, balls: List[Ball]):
    for other_ball in balls:
        if(other_ball != ball):

            dist : np.ndarray = other_ball.pos - ball.pos
            dist_mag = np.linalg.norm(dist).sum()

            if(dist_mag <= ball.radius*2):
                overlap = ball.radius*2 - dist_mag

                unit_dist : np.ndarray = dist/dist_mag
                ball.pos = ball.pos - (overlap * unit_dist * .5)
                other_ball.pos = other_ball.pos +  (overlap * unit_dist * .5)

                dist = other_ball.pos - ball.pos
                dist_mag = np.linalg.norm(dist).sum()

                unit_dist = dist/dist_mag
                p = np.sum(ball.vel * unit_dist) - np.sum(other_ball.vel * unit_dist)

                ball.vel = ball.vel - p * unit_dist
                other_ball.vel = other_ball.vel + p * unit_dist
                

def check_ball_scored(ball, ballsToRemove):
    for pocket in POCKETS:
        if is_colliding_with_line(ball,pocket):
            ballsToRemove.append(ball)


def update(dt, balls):
    ballsToRemove = []
    for ball in balls:
        update_ball(dt, ball)
        check_wall_collisions(ball)
        check_ball_collisions(ball, balls)
        check_ball_scored(ball, ballsToRemove)
    for ball in ballsToRemove:
        balls.remove(ball)
    return ballsToRemove
