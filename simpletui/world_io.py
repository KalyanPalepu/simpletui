import json
from graphics import *

def export_icon(icon):
    ret = ''
    for line in icon[:-1]:
        ret += (line + ':')
    ret += icon[-1]
    return ret


def import_icon(string):
    return [str(line) for line in string.split(':')]


def export_world(world):
    background_coords = {}
    for i in range(len(world.background)):
        for j in range(len(world.background[0])):
            if world.background[i][j] != ' ':
                background_coords[world.background[i][j]] = (i, j)
    sprite_coords = {}
    for sprite in world.sprites:
        sprite_coords[export_icon(sprite.icon)] = (sprite.x, sprite.y)
    return json.dumps([sprite_coords, world.rows, world.cols, background_coords])


def import_world(string):
    sprite_coords, rows, cols, background_coords = json.loads(string)
    background = [[' ' for col in xrange(cols)] for row in xrange(rows)]
    for icon, coord in background_coords.iteritems():
        background[coord[0]][coord[1]] = icon

    sprite_list = []
    for icon, coords in sprite_coords.iteritems():
        sprite_list.append(Sprite(x=coords[0], y=coords[1], icon=import_icon(icon)))
    return World(sprite_list, rows, cols, background=background)

