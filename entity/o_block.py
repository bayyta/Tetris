from block import Block
import pygame as pg
import random
import os
import sys

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphics"))
sys.path.insert(0, lib_path)

import image

class O_block(Block):
    def __init__(self):
        super().__init__()
        self.img = image.yellow_img
        self.length = 2
        self.piece = [1, 1,
                      1, 1]
    
    def render(self, screen, tileSize, xo, yo):
        return super().render(screen, tileSize, xo, yo)

    def update(self, dt):
        return super().update(dt)

    def rotate(self, clockwise):
        return super().rotate(clockwise)



