from copy import deepcopy, copy
import math
from nis import cat
import numpy as np
import enginev2
import game
from multiprocessing import Pool

from ui import UIBall


class simulation:
    def __init__(self, state, vel : np.ndarray):
        self.state = state
        self.vel = vel

def get_best_move(state):
    pool = Pool()
    results = []
    cueIdx = -1
    
    #find cue ball
    for ball in state.balls:
        if ball.is_cue:
            cueIdx = state.balls.index(ball)

    #put cue ball at pos 0 to speed up simulations
    state.balls[cueIdx], state.balls[0] = state.balls[0], state.balls[cueIdx]
    
    #simulate asyncronously all simulations from 0-200 on the x and y axis
    for x in range(0,200):
        row_results = pool.map_async(simulate, [simulation(state,np.array([x,y])) for y in range(0,200)])
        results.append(row_results)

    #get the top velocity to return
    best_score = -1
    best_vel = (0,0)
    for row in results:
        scores= row.get()
        for score in scores:
            if score> best_score:
                best_vel = (results.index(row), scores.index(score))
                best_score = score
    return best_vel
               
def simulate(simulation):

    #copy the current state as to not mess with the displayed screen
    usable_state = deepcopy(simulation.state)
    old_balls = copy(usable_state.balls)

    
    
    #uses the engine to simulate a turn at a paticular velocity
    print("Starting simulation with velocity: " + str(simulation.vel), flush=True)
    usable_state.balls[0].vel = np.array(simulation.vel)
    while(not game.is_turn_done(usable_state)):
        enginev2.update(1/60, usable_state.balls)
        
    #get a list of the removed balls in order to calculate score
    balls_removed = [ball for ball in old_balls if ball not in usable_state.balls]    
    
    #determine the category of the bot if not already decided
    is_player_stripes = False
    if simulation.state.is_category_decided:
        is_player_stripes = simulation.state.is_player_stripes
    elif len(balls_removed) > 0:
        is_player_stripes = not balls_removed[0].is_stripped
    else:
        return 0

    category_balls = [ball for ball in usable_state.balls if not is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]


    if balls_removed[0] not in category_balls and not balls_removed[0].number == 8:
        return -1

    #calculates the score for the simulation based on the balls scored
    score = 0
    for ball in balls_removed:
        if ball.is_cue or (ball.number == 8 and len(category_balls)>0):
            return -1
        elif ball not in category_balls:
            score -= 1
        else:
            score +=1
    return score 


def getMoves(state):
    velList = []
    if state.is_category_decided:
        category_balls = [ball for ball in state.balls if not state.is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]
    else:
        category_balls = [ball for ball in state.balls if not ball.number == 8 and not ball.is_cue]

    if len(category_balls) == 0:
        category_balls = [ball for ball in state.balls if ball.number == 8]
        if len(category_balls) ==0:
            return (0,0)

    for ball in category_balls:
        
        cue_vel = check_score(state,ball)
        if np.max(np.abs(cue_vel)) > 0:
            velList.append(cue_vel)
    #         if simulate(simulation(state, cueVel)) > 0:
    #             velList.append(cueVel)
    #         else:
    #             velList.append(cueVel)
    return velList

def check_score(state, ball : UIBall) -> np.ndarray:

    print(f"Testing ball {str(ball.number)}")


    for pocket in enginev2.POCKETS:
        #get relevent information about the pocket
        pocket_len = (pocket[1]-pocket[0])
        pocket_len_mag = np.linalg.norm(pocket_len)
        pocket_unit_vec = pocket_len/pocket_len_mag
        pocket_center = pocket[0] + pocket_unit_vec*0.5*pocket_len_mag
        pocket_orthoNormal = np.array([-pocket_unit_vec[1], pocket_unit_vec[0]])

        #determine distance from pocket
        dist_from_center : np.ndarray = pocket_center - ball.pos
        unit_dist = dist_from_center/np.linalg.norm(dist_from_center)

        angle = math.acos(np.cross(dist_from_center, pocket_orthoNormal)) * 180/math.pi

        if abs(angle)<45:

            cue_vel = back_propegate(state, ball, pocket_center, unit_dist * 5)
            if cue_vel[0] > 0 or cue_vel[1] > 0:
                return cue_vel
    return np.ndarray([0,0])

##
# returns the velocity that the cue needs to be hit at in order to send @param ball to @param pos arriving with @param vel from @param state
##
def back_propegate(state, ball : UIBall, pos : np.ndarray, vel : np.ndarray) -> np.ndarray:
    print(f"Attempting to send ball {str(ball.number)} to position: {str(pos)} arriving with velocity {str(vel)}")
    dist = ball.pos - pos
    dist_mag = np.linalg.norm(dist)
    required_vel = getVelForDist(dist_mag, vel)
    possible_velocities = simulate_collisions(required_vel)
    for possible_velocity in possible_velocities:
        unit_vel = np.linalg.norm(possible_velocity)
        for ball in state.balls:
            
    
def simulate_collisions(vel):
    velocities = []
    for x in frange(-1.0,1.0,0.01):
        y = math.sin(math.acos(x))
        unit_dist = np.array([x,y])
        dist = unit_dist * 10
        for theta in frange(0.01,1,.01):
            vel_mag = vel/dist * (10/math.cos(theta))
            found_vel = rotate(unit_dist,theta) * vel_mag
            velocities.append(found_vel)

    return velocities

def getVelForDist(distMag, finalVelMag):
    currentDist = 0
    currentVel = finalVelMag
    while abs(currentDist)<abs(distMag):
        currentDist += .01*currentVel
        currentVel  = currentVel*(1+(1-enginev2.DECELERATION)*.01)
    currentVel = 300 if currentVel>300 else currentVel
    return currentVel


def rotate(vec : np.ndarray, rad: float):
    rot = np.array([[math.cos(rad), -math.sin(rad)], [math.sin(rad), math.cos(rad)]])
    return np.dot(rot, vec)

def frange(start, stop=None, step=None):
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1
