import pygame as pg
import os

from level.level import Level

class Tetris(object):
    def __init__(self, **kwargs):
        try:
            pg.init()
        except ex:
            print("Could not initialize PyGame!")

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.display.set_caption("Tetris")

        # initialize variables
        self.running = True
        self.width = 1024
        self.height = 576
        self.color = (18, 18, 28);
        self.screen = pg.display.set_mode([self.width, self.height])
        self.level = Level(self.width, self.height)

    def run(self):
        clock = pg.time.Clock()
        time = 0.0
        frames = 0

        while self.running:
            # event handling
            for event in pg.event.get():
                if event.type == pg.QUIT: self.running = False
                if event.type == pg.KEYDOWN: self.level.key_down(event.key)
                if event.type == pg.KEYUP: self.level.key_up(event.key)
            
            # calc fps
            frames += 1
            clock.tick()
            time += clock.get_time()
            if (time >= 1000.0): # 1 second elapsed
                time -= 1000.0
                print(frames) # print fps
                frames = 0

            # update
            self.level.update(clock.get_time())

            # render
            self.screen.fill(self.color)
            self.level.render(self.screen)
            pg.display.flip()

        pg.font.quit()
        pg.quit()

if __name__ == "__main__":
    Tetris().run()