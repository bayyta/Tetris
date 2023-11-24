import math

class Vec2(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set(self, x, y):
        self.x = x
        self.y = y

    def setVec2(self, vec2):
        self.x = vec2.x;
        self.y = vec2.y;

    def add(self, x, y):
        self.x += x;
        self.y += y;

    def addVec2(self, vec2):
        self.x += vec2.x;
        self.y += vec2.y;

    def sub(self, x, y):
        self.x -= x;
        self.y -= y;

    def subVec2(self, vec2):
        self.x -= vec2.x;
        self.y -= vec2.y;

    def mul(self, x, y):
        self.x *= x;
        self.y *= y;

    def mulVec2(self, vec2):
        self.x *= vec2.x;
        self.y *= vec2.y;

