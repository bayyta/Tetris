import pygame as pg
import os
import sys
import random
import math
from enum import Enum

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "entity"))
sys.path.insert(0, lib_path)

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils"))
sys.path.insert(0, lib_path)

lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphics"))
sys.path.insert(0, lib_path)

from i_block import I_block
from j_block import J_block
from l_block import L_block
from o_block import O_block
from s_block import S_block
from t_block import T_block
from z_block import Z_block
from vec2 import Vec2
import image
import font as fnt

class GameState(Enum):
    START = 1
    PLAY = 2
    GAMEOVER = 3

class PositionState(Enum):
    FREE = 1
    BLOCKED = 2

class Level(object):
    def __init__(self, windowWidth, windowHeight):
        self.time = 0.0 # time elapsed since start
        self.score = 0.0 # score
        self.isMaxSpeed = False
        self.gameState = GameState.START # current state of the game
        self.windowWidth = windowWidth # window width
        self.windowHeight = windowHeight # window height
        self.speedTimer = 0.0 # starts when holding left or right
        self.speedStart = 0.10 # time until start moving fast sideways when holding
        self.speed = 1.0 # tiles per second
        self.maxSpeed = 18.0 # speed when holding arrows
        self.deltaPos = Vec2(0.0, 0.0) # delta x and y for position of active piece
        self.tileSize = 24 # size of a tile in pixels
        self.mapWidth = 10 # map width in tiles
        self.mapHeight = 20 # map height in tiles
        self.map = [0] * self.mapWidth * self.mapHeight # create map as list of 0s (maybe change to 2d matrix)
        self.xOffset = self.windowWidth / 2 - self.mapWidth * self.tileSize / 2 # offset width in pixels
        self.yOffset = self.windowHeight / 2 - self.mapHeight * self.tileSize / 2 # offset height in pixels
        self.ghostPiece = [] # outline of block at bottom
        self.squareType = [image.yellow_img, image.blue_img, image.cyan_img, image.green_img,
                          image.orange_img, image.purple_img, image.red_img] # store images of blocks
        self.classType = (I_block, J_block, L_block, O_block, S_block, T_block, Z_block) # store piece types
        self.piecesMax = 3 # pieces that will be displayed as 'next' right of map, including active piece
        self.pieces = [] # init pieces
        print("Level initialized!")
        
    def update(self, dt):
        self.time += dt / 1000.0
        if self.gameState == GameState.START:
            pass
        elif self.gameState == GameState.PLAY:
            self.deltaPos.y += dt * self.speed / 1000.0

            dx = int(self.deltaPos.x)
            if dx != 0:
                state = self.next_position(self.pieces[0].piece, self.pieces[0].pos.x + dx, self.pieces[0].pos.y)
                if state == PositionState.FREE:
                    self.pieces[0].pos.add(dx, 0)
                    self.update_ghost_piece()

            dy = int(self.deltaPos.y)
            if dy != 0:
                state = self.next_position(self.pieces[0].piece, self.pieces[0].pos.x, self.pieces[0].pos.y + dy)
                if state == PositionState.FREE:
                    self.pieces[0].pos.add(0, dy)
                    if self.isMaxSpeed:
                        self.score += dy / 2
                elif state == PositionState.BLOCKED:
                    if not self.add_piece_to_map(self.pieces[0].pos.x, self.pieces[0].pos.y):
                        # game over
                        self.gameState = GameState.GAMEOVER
                        return
                    self.add_new_piece()
                    dx = 0
                    dy = 0

            self.deltaPos.sub(dx, dy)

            # get pressed keys
            keys = pg.key.get_pressed()
            if keys[pg.K_DOWN]:
                self.isMaxSpeed = True
                self.deltaPos.y += dt * self.maxSpeed / 1000.0
            else:
                self.isMaxSpeed = False
            if keys[pg.K_LEFT] and self.speedTimer >= self.speedStart:
                self.deltaPos.x -= dt * self.maxSpeed / 1000.0
            if keys[pg.K_RIGHT] and self.speedTimer >= self.speedStart:
                self.deltaPos.x += dt * self.maxSpeed / 1000.0
            if not keys[pg.K_LEFT] and not keys[pg.K_RIGHT]:
                self.speedTimer = 0.0
            else:
                self.speedTimer += dt / 1000.0

        elif self.gameState == GameState.GAMEOVER:
            pass

    def render(self, screen):
        # render background
        screen.fill((8, 8, 12), pg.Rect(self.xOffset, self.yOffset, self.mapWidth * self.tileSize, 
                                         self.mapHeight * self.tileSize))

        # render grid
        for x in range(self.mapWidth + 1):
            screen.fill((24, 24, 65), pg.Rect(self.xOffset + x * self.tileSize, self.yOffset, 1, self.mapHeight * self.tileSize))
        for y in range(self.mapHeight + 1):
            screen.fill((24, 24, 65), pg.Rect(self.xOffset, self.yOffset + y * self.tileSize, self.mapWidth * self.tileSize, 1))

        # render blocks on map
        for y in range(0, self.mapHeight):
            for x in range(0, self.mapWidth):
                rect = pg.Rect(self.xOffset + x * self.tileSize, self.yOffset + y * self.tileSize, 
                                                         self.tileSize - 2,  self.tileSize - 2)
                type = self.map[x + y * self.mapWidth]
                if type == 0: continue
                screen.blit(pg.transform.scale(self.squareType[type - 1], (self.tileSize, self.tileSize)), rect)

        # render ghost piece
        for i in range(len(self.ghostPiece)):
            if self.ghostPiece[i].y < 0: continue
            pg.draw.rect(screen, (160, 160, 160), [self.xOffset + self.ghostPiece[i].x * self.tileSize, 
                                                   self.yOffset + self.ghostPiece[i].y * self.tileSize, 
                                                   self.tileSize, self.tileSize], 1)

        if self.gameState == GameState.START:
            # cycling through colors using time and cos
            self.render_text(screen, "Press 'Enter' to play!", self.windowWidth / 2 + 3, self.windowHeight / 2 + 3,
                            (0, 0, 0), 20, True)
            self.render_text(screen, "Press 'Enter' to play!", self.windowWidth / 2, self.windowHeight / 2,
                            (abs(math.cos(self.time * 2) * 255.0), abs(math.cos(self.time * 2) * 255.0), 255), 20, True)

        elif self.gameState == GameState.PLAY:
            # render pieces and the texts
            self.render_texts(screen)
            self.render_pieces(screen)

        elif self.gameState == GameState.GAMEOVER:
            # render pieces and the texts
            self.render_texts(screen)
            self.render_pieces(screen)

            # render gameover text
            self.render_text(screen, "GAMEOVER!", self.windowWidth / 2 + 3, self.windowHeight / 2 - 20 + 3,
                            (0, 0, 0), 20, True)
            self.render_text(screen, "GAMEOVER!", self.windowWidth / 2, self.windowHeight / 2 - 20,
                            (255, abs(math.cos(self.time * 2) * 255.0), abs(math.cos(self.time * 2) * 255.0)), 20, True)
            self.render_text(screen, "Press 'Enter' to play again!", self.windowWidth / 2 + 3, self.windowHeight / 2 + 20 + 3,
                            (0, 0, 0), 20, True)
            self.render_text(screen, "Press 'Enter' to play again!", self.windowWidth / 2, self.windowHeight / 2 + 20,
                            (255, abs(math.cos(self.time * 2) * 255.0), abs(math.cos(self.time * 2) * 255.0)), 20, True)

    def render_pieces(self, screen):
        for i in range(self.piecesMax):
            self.pieces[i].render(screen, self.tileSize, self.xOffset, self.yOffset)

    def render_texts(self, screen):
        self.render_text(screen, "Next", self.xOffset + (self.mapWidth + 4) * self.tileSize, self.yOffset,
                        (240, 240, 240), 20, True, fnt.light_font)

        self.render_text(screen, "Score: " + str(int(self.score)), self.xOffset - 110, self.windowHeight / 2, 
                            (240, 240, 240), 20, True, fnt.light_font)

    def render_text(self, screen, text, x, y, color, antialias, centered, font = fnt.standard_font):
        surface = font.render(text, antialias, color)
        rect = surface.get_rect()
        rect.x = x
        rect.y = y
        if centered:
            rect.x -= rect.width / 2
            rect.y -= rect.height / 2
        screen.blit(surface, rect)

    def get_bottom_pos(self):
        newPos = Vec2(self.pieces[0].pos.x, self.pieces[0].pos.y)

        while self.next_position(self.pieces[0].piece, newPos.x, newPos.y + 1) == PositionState.FREE:
            newPos.y += 1

        return newPos

    def update_ghost_piece(self):
        l = self.pieces[0].length
        pos = self.get_bottom_pos()
        del self.ghostPiece[:] # clear array of the coordinates
        for y in range(l):
            for x in range(l):
                if self.pieces[0].piece[x + y * l] != 0:
                    self.ghostPiece.append(Vec2(pos.x + x, pos.y + y))

    def restart(self):
        self.score = 0 # reset score
        self.speedTimer = 0.0 # reset speed timer
        self.speed = 1.0 # reset speed
        for i in range(self.mapWidth * self.mapHeight): # reset map to 0s
            self.map[i] = 0
        for i in range(self.piecesMax):
            self.add_new_piece()
        print("Restarted!")

    def add_new_piece(self):
        vertSpace = 4
        if len(self.pieces) == self.piecesMax:
            # remove current piece from list
           self.pieces.pop(0)
           # update next pieces position
           for i in range(1, len(self.pieces)): 
               self.pieces[i].pos.y -= vertSpace 
        p = random.choice(self.classType)()
        self.pieces.append(p) # add random piece
        p.pos.set(self.mapWidth + 4 - p.length / 2, (len(self.pieces) - 1) * vertSpace - 2) # set pos to be right of map
        self.pieces[0].pos.set(random.randint(0, self.mapWidth - self.pieces[0].length - 1), -2) # change pos of new active piece
        self.deltaPos.setVec2(Vec2(0.0, 0.0)) # reset delta pos
        self.update_ghost_piece() # update ghost piece        

    def add_piece_to_map(self, newX, newY):
        tempCoords = [] # blocks above map have to wait
        for y in range(self.pieces[0].length):
            for x in range(self.pieces[0].length):

                # check if it's empty or not
                if self.pieces[0].piece[x + y * self.pieces[0].length] != 0:
                    xc = int(newX + x) # x pos of new x
                    yc = int(newY + y) # y pos of new y

                    if yc < 0: # don't add blocks above the map, instead add to temporary array
                        tempCoords.append(Vec2(xc, yc))
                        continue

                    # add to map
                    self.map[xc + yc * self.mapWidth] = self.squareType.index(self.pieces[0].img) + 1 # start at index 1

        # check for rows to eliminate
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                if self.map[x + y * self.mapWidth] == 0:
                    break
                elif x == self.mapWidth - 1:
                    # row filled with blocks, eliminate and add new empty layer on top
                    for i in range(self.mapWidth):
                        # first add score for every eliminated block
                        self.score += 1 

                        self.map.pop(i + y * self.mapWidth)
                        self.map.insert(0, 0)

                    for i in range(len(tempCoords)):
                        tempCoords[i].y += 1
         
        # add temp coords
        for i in range(len(tempCoords)):
            if tempCoords[i].y >= 0:
                self.map[tempCoords[i].x + tempCoords[i].y * self.mapWidth] = self.squareType.index(self.pieces[0].img)

        # if a block is in row 0 then game over and return false
        for x in range(self.mapWidth):
            if self.map[x] != 0:
                return False

        return True

    def next_position(self, piece, newX, newY):
        # loop through every point on active block to check if colliding
        for y in range(0, self.pieces[0].length):
            for x in range(0, self.pieces[0].length):

                # check if it's empty or not
                if piece[x + y * self.pieces[0].length] != 0:
                    xc = int(newX + x) # x position of current point on piece
                    yc = int(newY + y) # y position of current point on piece

                    # check if it's off screen
                    if xc < 0 or xc >= self.mapWidth:
                        return PositionState.BLOCKED

                    if yc < 0:
                        continue

                    # check if being blocked by another piece
                    if yc >= self.mapHeight or self.map[xc + yc * self.mapWidth] != 0:
                        return PositionState.BLOCKED

        return PositionState.FREE

    def try_rotate(self):
        newRot = self.pieces[0].rotate(True)
        newPos = Vec2(0.0, 0.0)

        if not self.pieces[0].isVertical:
            for y in range(0, self.pieces[0].length):
                for x in range(0, self.pieces[0].length):

                    # check if it's empty or not
                    if newRot[x + y * self.pieces[0].length] != 0:
                        xc = int(self.pieces[0].pos.x + x) # x position of current point on piece
                        yc = int(self.pieces[0].pos.y + y) # y position of current point on piece

                        # check if being blocked by another piece
                        if yc >= self.mapHeight:
                            newPos.y -= 1
                        elif self.map[xc + yc * self.mapWidth] != 0:
                            if y <= int(self.pieces[0].length / 2) - 1:
                                newPos.y += 1
                            else:
                                newPos.y -= 1
                        break
        else:
            for x in range(0, self.pieces[0].length):
                for y in range(0, self.pieces[0].length):

                    # check if it's empty or not
                    if newRot[x + y * self.pieces[0].length] != 0:
                        xc = int(self.pieces[0].pos.x + x) # x position of current point on piece
                        yc = int(self.pieces[0].pos.y + y) # y position of current point on piece

                        # check if being blocked by another piece
                        if xc < 0:
                            newPos.x += 1
                        elif xc >= self.mapWidth:
                            newPos.x -= 1
                        elif self.map[xc + yc * self.mapWidth] != 0:
                            if x <= int(self.pieces[0].length / 2) - 1:
                                newPos.x += 1
                            else:
                                newPos.x -= 1
                        break

        if self.next_position(newRot, self.pieces[0].pos.x + newPos.x, self.pieces[0].pos.y + newPos.y) == PositionState.FREE:
            self.pieces[0].piece = newRot
            self.pieces[0].pos.addVec2(newPos)
            self.pieces[0].isVertical = not self.pieces[0].isVertical   
            self.update_ghost_piece()

    def key_down(self, key):
        if self.gameState == GameState.START:
            if key == pg.K_RETURN:
                self.gameState = GameState.PLAY
                self.restart()
        elif self.gameState == GameState.PLAY:
            keys = pg.key.get_pressed()
            if key == pg.K_UP:
                self.try_rotate()
            if key == pg.K_LEFT:
                if keys[pg.K_RIGHT] == 0: self.deltaPos.x -= 1
            if key == pg.K_RIGHT:
                if keys[pg.K_LEFT] == 0: self.deltaPos.x += 1
            if key == pg.K_SPACE:
                newPos = self.get_bottom_pos()
                self.score += newPos.y - self.pieces[0].pos.y
                if not self.add_piece_to_map(newPos.x, newPos.y):
                    self.gameState = GameState.GAMEOVER
                    return
                self.add_new_piece()
        elif self.gameState == GameState.GAMEOVER:
            if key == pg.K_RETURN:
                self.restart()
                self.gameState = GameState.PLAY

    def key_up(self, key):
        if self.gameState == GameState.START:
            pass
        elif self.gameState == GameState.PLAY:
            if key == pg.K_LEFT:
                self.deltaPos.x = 0.0
            if key == pg.K_RIGHT:
                self.deltaPos.x = 0.0
        elif self.gameState == GameState.GAMEOVER:
            pass

