from copy import deepcopy, copy
import math
from nis import cat
from typing import List
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
    vel_list = []
    if state.is_category_decided:
        category_balls = [ball for ball in state.balls if not state.is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]
    else:
        category_balls = [ball for ball in state.balls if not ball.number == 8 and not ball.is_cue]

    if len(category_balls) == 0:
        category_balls = [ball for ball in state.balls if ball.number == 8]
        if len(category_balls) ==0:
            return [np.ndarray([0,0])]

    for ball in category_balls:
        
        cue_vel = check_score(state,ball)
        if len(cue_vel) > 0:
            vel_list.extend(cue_vel)
    #         if simulate(simulation(state, cueVel)) > 0:
    #             velList.append(cueVel)
    #         else:
    #             velList.append(cueVel)
    simulations = map(lambda vel : simulation(state,vel), vel_list)
    with Pool() as pool:
        results = pool.map(simulate, simulations)
    working_vels = []
    for idx, vel in enumerate(vel_list):
        if results[idx] > 0:
            working_vels.append(vel)
    
    return working_vels

def check_score(state, ball : UIBall):

    print(f"Testing ball {str(ball.number)}")

    found_vels = []
    for pocket in enginev2.POCKETS:
        usable_state = deepcopy(state)
            
        #get relevent information about the pocket
        pocket_len = (pocket[0]-pocket[1])
        pocket_len_mag = np.linalg.norm(pocket_len)
        pocket_unit_vec = pocket_len/pocket_len_mag
        pocket_center = pocket[0] + pocket_unit_vec*0.5*pocket_len_mag
        pocket_orthoNormal = rotate(pocket_unit_vec,math.pi/2)

        #determine distance from pocket
        dist_from_center : np.ndarray = pocket_center - ball.pos
        unit_dist = dist_from_center/np.linalg.norm(dist_from_center)
        
        dot = dist_from_center.dot(pocket_orthoNormal)/(np.linalg.norm(dist_from_center) * np.linalg.norm(pocket_orthoNormal))
        angle = math.acos(dot) * 180/math.pi

        if abs(angle)<20:
            usable_state.balls = [usable_ball for usable_ball in usable_state.balls if not usable_ball.number == ball.number]
            cue_vels = back_propegate(usable_state, ball, pocket_center, unit_dist * 5)
            if len(cue_vels)>0:
                print(f"Sending ball {str(ball.number)} to pocket at {str(pocket_center)}")
                found_vels.extend(cue_vels)

    return found_vels

##
# returns the velocity that the cue needs to be hit at in order to send @param ball to @param pos arriving with @param vel from @param state
##
def back_propegate(state, ball : UIBall, pos : np.ndarray, vel : np.ndarray):
    dist = ball.pos - pos
    dist_mag = np.linalg.norm(dist)
    required_vel = get_vel_for_dist(dist_mag, vel)

    if ball.is_cue:
        print(f"Sending cue to position {str(pos)} using velocity {str(required_vel)}")
        return [required_vel]

    possible_velocities, possible_positions = simulate_collisions(required_vel)
    found_vels : List[np.ndarray] = []
    for idx, possible_velocity in enumerate(possible_velocities):
        unit_vel = possible_velocity/np.linalg.norm(possible_velocity)
        required_pos = possible_positions[idx] + ball.pos
        for other_ball in state.balls:
            ball_dist = required_pos - other_ball.pos 
            ball_unit_dist = ball_dist/np.linalg.norm(ball_dist)
            diff = unit_vel.dot(ball_unit_dist)
            if abs(diff) < 0.1:
                state.balls = [b for b in state.balls if not b.number == ball.number]
                found = back_propegate(state, other_ball, required_pos, possible_velocity)
                if len(found) > 0:
                    found_vels.extend(found)

    return found_vels
    
    


            
    
def simulate_collisions(vel):
    velocities, positions  = [[],[]]
    unit_vel = vel/np.linalg.norm(vel)
    for x in frange(-1.0,1.0,0.1):
        y = math.sin(math.acos(x))
        unit_dist = np.array([x,y])
        dist = unit_dist * 10
        theta = math.acos(unit_vel.dot(unit_dist))
        velocities.append(vel * math.sin(theta/2))
        positions.append(dist)

    return (velocities, positions)

def get_vel_for_dist(dist_mag, final_vel : np.ndarray) -> np.ndarray:
    current_dist = 0
    current_vel = final_vel
    while abs(current_dist)<abs(dist_mag):
        current_dist += .01*(np.linalg.norm(current_vel))
        current_vel  *= (1+(1-enginev2.DECELERATION)*.01)
    return current_vel


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
