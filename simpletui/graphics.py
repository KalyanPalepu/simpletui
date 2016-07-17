from subprocess import Popen, PIPE, call
import sys
import copy
from time import sleep, time

DISPLAY_ROWS, DISPLAY_COLS = [int(dim) for dim in Popen('stty size'.split(), stdout=PIPE).communicate()[0].split()]


class Sprite:
    def __init__(self, x=0, y=0, icon='#'):
        self.x = x
        self.y = y
        self.icon = [icon] if isinstance(icon, str) else icon


class World:
    def __init__(self, sprites, rows, cols, background=0):
        self.rows = rows
        self.cols = cols
        self.sprites = [sprites] if isinstance(sprites, Sprite) else sprites
        if background == 0:
            self.background = [[' ' for col in xrange(self.cols)] for row in xrange(self.rows)]
        else:
            self.background = background
        self.screen_data = []

    def draw(self, start_y=0, end_y=DISPLAY_ROWS, start_x=0, end_x=DISPLAY_COLS):
        """ Returns Screen object, which retains metadata as well as pixel data """
        if start_y >= self.rows:
            start_y = self.rows - 1
        if start_x >= self.cols:
            start_x = self.cols - 1

        self.screen_data = [copy.copy(line[start_x:end_x]) for line in self.background[start_y:end_y]]
        for sprite in self.sprites:
            if sprite.x >= self.cols:
                sprite.x = self.cols - 1
            if sprite.y >= self.rows:
                sprite.y = self.rows - 1
            if sprite.x < 0:
                sprite.x = 0
            if sprite.y < 0:
                sprite.y = 0

            if sprite.y < start_y or sprite.y >= end_y or sprite.x < start_x or sprite.x >= end_x:
                continue
            for i in range(len(sprite.icon)):
                for j in range(len(sprite.icon[0])):
                    try:
                        self.screen_data[sprite.y + i][sprite.x + j] = sprite.icon[i][j]
                    except IndexError:
                        self.screen_data[sprite.y + i][sprite.x + j] = ' '
        return Screen(self.screen_data, start_y=start_y, end_y=end_y, start_x=start_x, end_x=end_x)


class Display:
    def __init__(self, rows=0, cols=0, sprites=0):
        if rows == 0 and cols == 0:
            self.rows, self.cols = DISPLAY_ROWS, DISPLAY_COLS
        if rows > DISPLAY_ROWS:
            self.rows = DISPLAY_ROWS
        if cols > DISPLAY_COLS:
            self.cols = DISPLAY_COLS

        if sprites == 0:
            self.sprites = []
        else:
            self.sprites = [sprites] if isinstance(sprites, Sprite) else sprites

        for i in range(self.rows):
            print

    def update(self, screen):
        if screen.rows > self.rows or screen.cols > self.cols:
            print 'Screen Dimensions:'
            print screen.rows, screen.cols
            print 'Display Dimensions:'
            print self.rows, self.cols
            print self.rows, self
            raise ValueError('Screen dimensions do not fit display dimensions')

        for sprite in self.sprites:
            if sprite.y < 0 or sprite.y >= rows or sprite.x < 0 or sprite.x >= rows:
                continue
            for i in range(len(sprite.icon)):
                for j in range(len(sprite.icon[0])):
                    try:
                        screen.data[sprite.y + i][sprite.x + j] = sprite.icon[i][j]
                    except IndexError:
                        screen.data[sprite.y + i][sprite.x + j] = ' '

        call('tput cup 0 0'.split())
        for line in screen.data[:-1]:
            sys.stdout.write('\r\033[K')
            for character in line:
                sys.stdout.write(character)
            sys.stdout.flush()
            sys.stdout.write('\n')
        sys.stdout.write('\r\033[K')
        for character in screen.data[-1]:
            sys.stdout.write(character)
        sys.stdout.flush()


class Screen:
    def __init__(self, data, start_y=0, end_y=0, start_x=0, end_x=0):
        self.data = data
        self.start_y = start_y
        self.end_y = end_y
        self.start_x = start_x
        self.end_x = end_x

        self.rows = len(data)
        if self.rows == 0:
            self.cols = 0
        else:
            self.cols = len(data[0])

    def onscreen(self, sprite):
        if sprite.y < self.start_y or sprite.y >= self.end_y or sprite.x < self.start_x or sprite.x >= self.end_x:
            return False
        return True


def set_fps(fps=-1, max_fps=60, locked=False, estimate=False):
    #specify FPS if you are waiting for user input
    def decorator(function):
        def wrapper():
            before = time()
            print before
            function()
            func_time = time() - before
            if fps == -1:
                frame_time = func_time
            else:
                frame_time = (1.0 / fps)
            min_time = 1.0 / max_fps
            if frame_time < min_time:
                frame_time = min_time
            wait_time = frame_time - func_time
            print frame_time
            while True:
                if estimate:
                    sleep(wait_time)
                    function()
                else:
                    before = time()
                    function()
                    func_time = time() - before
                    wait_time = frame_time - func_time
                    if wait_time > 0:
                        sleep(wait_time)
                    elif locked:
                        raise ValueError('Function took longer than fixed frame time (to stop this exception message set locked=false)')
        return wrapper
    return decorator
