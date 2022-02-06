from copy import deepcopy
import time
import pygame
import engine
from screeninfo import get_monitors
import math
import numpy as np
import threading

frameTime = pygame.time.get_ticks()

class UIBall(engine.Ball):
    def __init__(self, number, pos, vel = (0,0)):
        engine.Ball.__init__(self, pos, vel)
        self.number = number
        self.is_stripped = number>8
        self.is_cue = number == 0

#gets the correct monitor to determine size
monitors = get_monitors()
monitor_number = 1 if len(get_monitors()) > 1 else 0

#obtain the conversion information between engine position and pixels
engine_width = engine.BOARD_WIDTH + engine.BOARD_THICKNESS * 2
cm_to_px = int(monitors[monitor_number].width/engine_width)

#half the conversion if on a high dpi display
cm_to_px /= 2 if monitors[monitor_number].width > 2000 else 1

#convert engine measurements to measurements usable by the ui
board_width     = cm_to_px * engine.BOARD_WIDTH
board_height    = cm_to_px * engine.BOARD_HEIGHT
board_thickness = cm_to_px * engine.BOARD_THICKNESS
ball_radius     = cm_to_px * engine.Ball((0, 0), (0, 0)).radius

#get screen size based on converted dimensions
screen_width  = board_width  + board_thickness * 2
screen_height = board_height + board_thickness * 2

#initialize screen size
screen = pygame.display.set_mode([screen_width, screen_height])



#initalize pygame and set default values
clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.display.set_caption("Amazing Pool Bot")
font = pygame.font.SysFont("Comic Sans MS", 30)

#get images used for the balls in the game
images = []
for i in range(1,16):
    image = pygame.image.load('assets/ball_' + str(i) + '.png') #load image from assets folder
    image = pygame.transform.scale(image, (ball_radius*2,ball_radius*2)) #set image size based on ball radius
    images.append(image)

#gets the image for the cue ball and inserts it into the begining of the list
cue_ball_image = pygame.image.load('assets/ball_16.png')
cue_ball_image = pygame.transform.scale(cue_ball_image, (ball_radius*2,ball_radius*2))
images.insert(0, cue_ball_image)

#gets the images for the table and the cue from the assets folder and sizes them based on screen size
tableImage = pygame.image.load('assets/table.png').convert() #gets the table as a jpeg as it is faster to load and can be filled with black
tableImage = pygame.transform.scale(tableImage, (screen_width, screen_height))
cue_image = pygame.image.load('assets/cue.png')
cue_image = pygame.transform.rotate(cue_image, 180) #flip pool cue as it is facing the wrong direction

#defines pool for multiprocessing

##
# Displays debug information to enable call in render/reRender function
##
def draw_debug_info(debug_info):
    for wall in engine.WALLS:
        lines= np.array([wall[:2], wall[2:], wall[::2], wall[1::2]])
        for line in lines:
            line_pos = line * cm_to_px + board_thickness
            pygame.draw.line(screen, (255,0,0), line_pos[0],line_pos[1])

    for pocket in engine.POCKETS:
        line_pos = pocket*cm_to_px + board_thickness
        pygame.draw.line(screen, (255,0,0), line_pos[0],line_pos[1])

    for line in debug_info:
        line_pos = line*cm_to_px + board_thickness
        pygame.draw.line(screen, (255,0,0), line_pos[0],line_pos[1])


##
# Draws the table image 
##
def draw_table():
    screen.blit(tableImage, (0,0))

##
# @returns the arguments to draw @param ball on the screen based on the ball number
##
def draw_ball(ball):
    display_pos = ball.pos  * cm_to_px - ball_radius + board_thickness
    return (images[ball.number], [float(display_pos[0]),float(display_pos[1])])

##
# Draws all members of @param balls on the screen
##
def draw_balls(balls):
    blits_args = list(map(draw_ball, balls))
    screen.blits(blits_args)

##
# Draws the cue on the screen around the cue ball if @param currentVel > (0,0)
##
def draw_cue(current_vel : np.ndarray, balls): 
    if  np.max(np.absolute(current_vel)) == 0:
        return
    
    cue_ball = [ ball for ball in balls if ball.is_cue][0]
    vel_mag = np.linalg.norm(current_vel)
    unit_vel = -current_vel / vel_mag

    cue_tip_pos = cue_ball.pos + (cue_ball.radius+vel_mag/10) * unit_vel
    cue_angle = math.atan2(unit_vel[1], -unit_vel[0]) * (180/np.pi) + 180

    cue_tip_pos = cue_tip_pos + np.array([0, 509/cm_to_px])*unit_vel if 0 < cue_angle < 180 else cue_tip_pos
    cue_tip_pos = cue_tip_pos + np.array([509/cm_to_px, 0])*unit_vel if 90 < cue_angle < 270 else cue_tip_pos
    
    angled_img = pygame.transform.rotate(cue_image, cue_angle)
    cue_tip_pos = cue_tip_pos*cm_to_px + board_thickness
    screen.blit(angled_img, [float(cue_tip_pos[0]), float(cue_tip_pos[1])])


##
# Renders a frame and runs the engine on @param balls including drawing the cue using @param currentVel if given
##
def render(balls, currentVel = np.array([0,0])):

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    start_time = time.time()
    frame_time_sec = clock.tick(1000)/1000
    x = threading.Thread(target=engine.update, args=(frame_time_sec, balls))
    x.start()
    screen.fill((0, 0, 0))
    draw_table()
    cueBall = draw_balls(balls)
    
    draw_cue(currentVel, balls)
    #draw_debug_info()
    pygame.display.flip()
    x.join()


##
# Renders a frame with no engine update for use after long period of no engine activity
##
def reRender(balls, debug_info = None):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    clock.tick(1000)
    screen.fill((0, 0, 0))
    draw_table()
    cueBall = draw_balls(balls)
    draw_cue(np.array([0,0]), cueBall)
    if not debug_info == None:
        draw_debug_info(debug_info)

    pygame.display.flip()




