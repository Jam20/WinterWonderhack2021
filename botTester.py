import bot
from engine import Ball

tb1 = [Ball(1, 500, 500), Ball(0,250,250)]
tb2 = [Ball(1, 500, 500), Ball(2,500,300), Ball(0,500,100)]
tb3 = [Ball(1, 500, 500), Ball(2,400,400), Ball(3,300,300), Ball(0,200,200)]
tb4 = [Ball(1, 500, 500), Ball(2,400,600), Ball(0,600,400)]
tb5 = [Ball(1, 500, 500), Ball(2,400,400), Ball(0,600,300)]

bot.boardState = tb1
paths = bot.getPaths(Ball(1, 500, 500), (300, 90))
print(*paths)
