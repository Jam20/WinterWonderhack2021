from copy import deepcopy, copy
import math
from typing import List
import numpy as np
import engine
import game
from multiprocessing import Pool
from ui import UIBall, reRender
import ui
import time


class simulation:
    def __init__(self, state, vel : np.ndarray):
        self.state = state
        self.vel = vel

class Path:
    def __init__(self, pocket_pos : np.ndarray):
            self.pocket_pos = pocket_pos
            self.path : List[UIBall] = []
            self.final_velocity = np.array([0,0], dtype="f")
    def copy(self):
        new_path = Path(self.pocket_pos)
        for ball in self.get_balls_in_path():
            new_path.add_ball_to_path(ball)
        return new_path
    def add_ball_to_path(self, ball : UIBall):
        self.path.append(ball)
    def get_debug_lines(self):
        points : List[np.ndarray]= []
        for ball in self.path:
            if len(points) == 0:
                points.append(np.array([self.pocket_pos, ball.pos]))
            else:
                points.append(np.array([points[-1][1], ball.pos]))

        return points
    def get_balls_in_path(self):
        return self.path
    def set_final_velocity(self, vel : np.ndarray):
        self.final_velocity = vel
    def get_final_velocity(self):
        return self.final_velocity

               
def simulate(simulation):

    #copy the current state as to not mess with the displayed screen
    usable_state = deepcopy(simulation.state)
    old_balls = copy(usable_state.balls)

    #uses the engine to simulate a turn at a paticular velocity
    print("Starting simulation with velocity: " + str(simulation.vel), flush=True)
    usable_state.balls[0].vel = np.array(simulation.vel)
    while(not game.is_turn_done(usable_state)):
        engine.update(1/60, usable_state.balls)
        
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
        
        cue_vel = []
        if len(cue_vel) > 0:
            vel_list.extend(cue_vel)

    simulations = map(lambda vel : simulation(state,vel), vel_list)
    # with Pool() as pool:
    #     results = pool.map(simulate, simulations)
    # working_vels = []
    # for idx, vel in enumerate(vel_list):
    #     if results[idx] > 0:
    #         working_vels.append(vel)
    
    return vel_list

def get_best_move(state) -> np.ndarray:
    if state.is_category_decided:
        category_balls = [ball for ball in state.balls if not state.is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]
    else:
        category_balls = [ball for ball in state.balls if not ball.number == 8 and not ball.is_cue]
    
    if len(category_balls) == 0:
        category_balls = [ball for ball in state.balls if ball.number == 8]
        if len(category_balls) ==0:
            return np.ndarray([0,0])

    paths : List[Path] = []
    debug_info = []
    for pocket in engine.POCKETS:
        for ball in category_balls:
            #get relevent information about the pocket
            pocket_len = (pocket[0]-pocket[1])
            pocket_len_mag = np.linalg.norm(pocket_len)
            pocket_unit_vec = pocket_len/pocket_len_mag
            pocket_center = pocket[1] + pocket_unit_vec*0.5*pocket_len_mag
            dist_from_center : np.ndarray = pocket_center - ball.pos
            unit_dist = dist_from_center/np.linalg.norm(dist_from_center)
            new_paths = back_propegate(state, ball, pocket_center, unit_dist * 10, Path(pocket_center))
            paths.extend(new_paths)
            for path in new_paths:
                debug_info.extend(path.get_debug_lines())
            ui.reRender(state.balls,debug_info)
            #time.sleep(0.5)
    for path in paths:
        nums = list(map(lambda n: n.number, path.get_balls_in_path()))
        print(nums, " ", path.final_velocity)
    print("Num of paths: ", len(paths))
    if len(paths) == 0:
        return np.array([0,0], dtype="f")
    vel_list = map(lambda p: p.get_final_velocity(), paths)
    simulations = map(lambda vel : simulation(state,vel), vel_list)
    with Pool() as pool:
        results = pool.map(simulate, simulations)
    working_vels = []
    for idx, vel in enumerate(vel_list):
        if results[idx] > 0:
            working_vels.append(vel)

    if len(working_vels) == 0:
        return paths[0].get_final_velocity()
    return working_vels[0]
    

##
# returns the velocity that the cue needs to be hit at in order to send @param ball to @param pos arriving with @param vel from @param state
##
def back_propegate(state, ball, pos, vel, path : Path):
    path.add_ball_to_path(ball)
    paths = [path]

    dist = ball.pos - pos
    dist_mag = np.linalg.norm(dist)
    required_vel = get_vel_for_dist(dist_mag, vel)

    if ball.is_cue:
        path.set_final_velocity(required_vel)
        return paths

    possible_velocities= simulate_collisions(required_vel)
    position = required_vel/np.linalg.norm(required_vel) * 5
    
    debug_info = []
    for posible_vel in possible_velocities:
        unit_vel = posible_vel/np.linalg.norm(posible_vel)
        debug_info.append(np.array([ball.pos - position - unit_vel*10, ball.pos - position]))
    reRender(state.balls, debug_info)    
    
    collidable_balls = [ball for ball in state.balls if ball not in path.get_balls_in_path()]
    for other_ball in collidable_balls:
        for possible_velocity in possible_velocities:
            unit_vel = possible_velocity/np.linalg.norm(possible_velocity)
            required_pos = ball.pos - position

            ball_dist = required_pos - other_ball.pos  
            ball_unit_dist = ball_dist/np.linalg.norm(ball_dist)
            diff = unit_vel.dot(ball_unit_dist)
            ang = math.acos(diff)
            if abs(ang) < 0.1:
                new_paths = back_propegate(state, other_ball, required_pos, possible_velocity, path.copy())
                paths.extend(new_paths)
    paths = [path for path in paths if path.get_balls_in_path()[-1].is_cue]

    return paths
    
    


            
    
def simulate_collisions(vel):
    velocities= []
    unit_vel = vel/np.linalg.norm(vel)
    norm = np.linalg.norm(vel)
    for theta in frange(0,2*math.pi, .01):
        if 0 < math.cos(theta):
            if not np.linalg.norm(norm/math.cos(theta)) > 300:
                velocities.append((norm/math.cos(theta))*rotate(unit_vel,theta))
    return velocities

def get_vel_for_dist(dist_mag, final_vel : np.ndarray) -> np.ndarray:
    current_dist = 0
    current_vel = final_vel
    while abs(current_dist)<abs(dist_mag):
        current_dist += .01*(np.linalg.norm(current_vel))
        current_vel  += current_vel*(1-engine.DECELERATION)*.01
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
