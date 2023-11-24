import pygame as pg
import math
import os
import sys

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils"))
sys.path.insert(0, lib_path)

from vec2 import Vec2
from abc import ABC, abstractmethod

class Block(ABC): # abstract class
    def __init__(self):
        self.pos = Vec2(0.0, 0.0) # position of piece
        self.img = None # image of piece
        self.length = 0 # length of piece
        self.piece = [] # piece drawn with 1s and 0s
        self.isVertical = False

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, screen, tileSize, xo, yo):
        for y in range(0, self.length):
            if self.pos.y + y < 0: # don't render blocks offscreen
                continue
            for x in range(0, self.length):
                if self.piece[x + y * self.length] == 1:
                    screen.blit(pg.transform.scale(self.img, (tileSize, tileSize)), 
                                pg.Rect(xo + (x + self.pos.x) * tileSize, yo + (y + self.pos.y) * tileSize, tileSize, tileSize))

    @abstractmethod
    def rotate(self, clockwise):
        newMatrix = []
        for i in range(0, self.length * self.length):
            newMatrix.append(0)

        for y in range(0, self.length):
            for x in range(0, self.length):
                if clockwise:
                    newMatrix[x + y * self.length] = self.piece[y + (self.length - 1 - x) * self.length]
                else:
                    newMatrix[x + y * self.length] = self.piece[(self.length - 1 - y) + x * self.length]

        return newMatrix



