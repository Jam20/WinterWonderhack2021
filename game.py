from screeninfo import get_monitors
import ui
from ui import UIBall
import enginev2

class GameBall(ui.UIBall):
    def __init__(self, id, pos, vel, number):
        super().__init__(id, pos, vel, number)
        self.isStripped = number>8
        self.isCue = number == 0
        self.isPocketed = False

class GameState:
    def __init__(self):
        constRad = enginev2.Ball((0, 0), (0, 0)).radius
        self.balls = [
            #UIBall(0, (85, 64), (0, 0), 0),
            UIBall(0, (0, 0), (0, 0), 0),

            UIBall(1, (170, 64), (0, 0), 1),

            UIBall(9, (170 + constRad * 2, 64 - constRad),
                   (0, 0), 2),
            UIBall(2, (170 + constRad * 2, 64 + constRad), (0, 0), 3),

            UIBall(10, (170 + constRad * 4, 64 - constRad * 2),
                   (0, 0), 4),
            UIBall(8, (170 + constRad * 4, 64), (0, 0), 5),
            UIBall(3, (170 + constRad * 4, 64 + constRad * 2),
                   (0, 0), 6),

            UIBall(11, (170 + constRad * 6, 64 - constRad * 3),
                   (0, 0), 7),
            UIBall(7, (170 + constRad * 6, 64 - constRad), (0, 0), 8),
            UIBall(14, (170 + constRad * 6, 64 + constRad),
                   (0, 0), 9),
            UIBall(4, (170 + constRad * 6, 64 + constRad * 3),
                   (0, 0), 10),

            UIBall(5, (170 + constRad * 8, 64 - constRad * 4),
                   (0, 0), 11),
            UIBall(13, (170 + constRad * 8, 64 - constRad * 2),
                   (0, 0), 12),
            UIBall(15, (170 + constRad * 8, 64), (0, 0), 13),
            UIBall(6, (170 + constRad * 8, 64 + constRad * 2),
                   (0, 0), 14),
            UIBall(12, (170 + constRad * 8, 64 + constRad * 4),
                   (0, 0), 15),
        ]

def runTurn(state, cueVel):
    for ball in state.balls:
        if(ball.number == 0):
            ball.vel = cueVel
            while abs(ball.vel[0])>5 or abs(ball.vel[1])>5:
                ui.render(state.balls)
