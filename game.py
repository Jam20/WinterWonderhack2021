import copy
from unicodedata import category
from screeninfo import get_monitors
import ui
from ui import UIBall
import pygame
import math
import time
import botv2
import numpy as np
MAX_VEL = 300

class GameState:
       def __init__(self):
        self.is_player_stripes = False
        self.is_category_decided = False
        self.balls = [
              UIBall(0, (85, 64)),
              
              UIBall(1, (170, 64)),

              UIBall(2, (180, 59)),
              UIBall(3, (180, 69)),

              UIBall(4, (190, 54)),
              UIBall(5, (190, 64)),
              UIBall(6, (190, 74)),

              UIBall(7,  (200, 49)),
              UIBall(8,  (200, 59)),
              UIBall(9,  (200, 69)),
              UIBall(10, (200, 79)),

              UIBall(11,  (210, 44)),
              UIBall(12,  (210, 54)),
              UIBall(13,  (210, 64)),
              UIBall(14,  (210, 74)),
              UIBall(15,  (210, 84)),
        ]     

       def print_state(self):
              print('Ball Information:', flush=True)
              for ball in self.balls:
                     print('Ball ', str(ball.number), ': Pos ', str(ball.pos), ", Vel ", str(ball.vel), end="\r\n", flush=True)
##
# Sets the velocity of the cue ball to @param cue_vel
##
def run_turn(state, cue_vel):
       for ball in state.balls:
              ball.vel = np.array(cue_vel) if ball.is_cue else ball.vel

              while not is_turn_done(state):
                     ui.render(state.balls)
                     #state.printState()

##
# @returns true if the current turn in the @state is complete aka all velocities are zero
##
def is_turn_done(state):
       for ball in state.balls:
              if np.max(np.abs(ball.vel)) > 0:
                     return False
       return True

##
# Handles getting the velocity from the user and rendering the screen while waiting
##
def get_player_vel(state):
       cue_ball = [ball for ball in state.balls if ball.is_cue][0]
       is_left_mouse_pressed = pygame.mouse.get_pressed()[0] == 1
       current_vel = get_unit_vel(cue_ball)
       while not is_left_mouse_pressed:
              current_vel = get_unit_vel(cue_ball)
              ui.render(state.balls, current_vel)
              is_left_mouse_pressed = pygame.mouse.get_pressed()[0] == 1
       
       initTime = time.perf_counter()
       time_elapsed = time.perf_counter()-initTime

       while is_left_mouse_pressed:
              current_vel = get_unit_vel(cue_ball)
              time_elapsed = time.perf_counter()-initTime
              time_elapsed = 3 if time_elapsed>3 else time_elapsed
              power = time_elapsed/3 * MAX_VEL
              current_vel *= power
              
              ui.render(state.balls, current_vel)

              
              is_left_mouse_pressed = pygame.mouse.get_pressed()[0] == 1

       return current_vel

##
# @returns the unit velocity based on the mouse position and the position of the cue ball
##
def get_unit_vel(cue_ball):
       mouse_pos = np.array(pygame.mouse.get_pos())
       dist = cue_ball.pos*ui.cm_to_px - mouse_pos + ui.board_thickness
       dist_mag = np.linalg.norm(dist)
       return dist/dist_mag

##
# Handles the player's turn given @param state @returns 1 if player has won 2 if the bot has won and 0 if the game should continue
##
def play_player_turn(state):
       cue_ball_vel = get_player_vel(state)
       old_balls = copy.copy(state.balls)
       run_turn(state, cue_ball_vel)
       balls_removed = [ball for ball in old_balls if ball not in state.balls]

       if len(balls_removed) > 0:
              #selects a category based on the first ball scored
              if not state.is_category_decided:
                     state.is_player_stripes = balls_removed[0].is_stripped
                     state.is_category_decided = True

              category_balls = [ball for ball in state.balls if state.is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]

              #modifies state based on results of the turn
              for ball in balls_removed:
                     if ball.is_cue:
                            state.balls.append(UIBall(0, (85,64)))
                            
                            return 2 if len(category_balls) == 0 else 0 
                     if ball.number == 8:
                            if len(category_balls) == 0 and balls_removed[-1] == ball:
                                   return 1
                            return 2
              if state.is_player_stripes == balls_removed[0].is_stripped:
                     play_player_turn(state)

def play_bot_turn(state):
       cue_vel = botv2.getMoves(state)
       old_balls = copy.copy(state.balls)
       for vel in cue_vel:
              print("x: ", str(round(vel[0],3)), " y: ", str(round(vel[1],3)))
       print(len(cue_vel))
       ui.reRender(state.balls)
       if len(cue_vel) > 0:
              print("FOUND BOT VELS: " + str(cue_vel[0]))
              run_turn(state, cue_vel[0])
       else:
              print("NO BOT VEL FOUND")
              run_turn(state, (200,0))

       balls_removed = [ball for ball in old_balls if ball not in state.balls]
       
       if len(balls_removed) > 0:

              #selects a category based on the first ball scored
              if not state.is_category_decided:
                     state.is_player_stripes = not balls_removed[0].is_stripped
                     state.is_category_decided = True

              category_balls = [ball for ball in state.balls if not state.is_player_stripes == ball.is_stripped and not ball.number == 8 and not ball.is_cue]

              for ball in balls_removed:
                     if ball.is_cue:
                            state.balls.append(UIBall(0, (85,64)))       
                            return 1 if len(category_balls) == 0 else 0
                     if ball.number == 8:
                            if len(category_balls) == 0 and balls_removed[-1] == ball:
                                   return 2
                            return 1

              if state.is_player_stripes == balls_removed[0].is_stripped:
                     play_bot_turn(state)
       return 0

           

def run_game():
       main_state = GameState()
       winner = 0
       while winner == 0:
              winner = play_player_turn(main_state)
              winner = play_bot_turn(main_state)
       if winner == 1:
              print("YOU WIN GOOD JOB")
       else:
              print("YOU LOSE GET GOOD")


