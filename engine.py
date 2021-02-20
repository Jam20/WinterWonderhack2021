class Ball:
    def __init__(self, id, x, y, color, isStriped, number):
        self.id = id
        self.pos = (x, y)
        self.color = color # RGB values
        self.isStriped = isStriped # True/False
        self.number = number # The ball number
        
