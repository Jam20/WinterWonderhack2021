class Ball:
    def __init__(self, id, x, y, color, isStriped):
        self.id = id # Ball number (0 = Q)
        self.pos = (x, y)
        self.color = color # RGB values
        self.isStriped = isStriped # True/False
        
