import csv
import json
import os
import re

import pygame as pg

import const
import utl


class Map:

    def __init__(self, size, map_list, portals, images, spawn, ghost_spawn_point, map_dir):
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals
        self.spawn = spawn
        self.ghost_spawn_point = ghost_spawn_point
        self.map_dir = map_dir

    def convert_coordinate(self, position: tuple | pg.Vector2) -> tuple:
        """
        Return the coordinate based on self.size of position.
        position is a coordinate based on const.ARENA_SIZE.
        """
        x = utl.clamp(int(position[0] * self.size[0] / const.ARENA_SIZE[0]), 0, self.size[0] - 1)
        y = utl.clamp(int(position[1] * self.size[1] / const.ARENA_SIZE[1]), 0, self.size[1] - 1)
        return x, y

    def convert_cell(self, position: tuple | pg.Vector2) -> pg.Vector2:
        """Similar to convert_coordinate(), but is the reverse version."""
        x = utl.clamp(position[0] * const.ARENA_SIZE[0] / self.size[0], 0, const.ARENA_SIZE[0] - 1)
        y = utl.clamp(position[1] * const.ARENA_SIZE[1] / self.size[1], 0, const.ARENA_SIZE[1] - 1)
        return pg.Vector2(x, y)

    def get_type(self, position: pg.Vector2) -> int:
        x, y = self.convert_coordinate(position)
        return self.map[x][y]

    def get_portal(self, position):
        x, y = self.convert_coordinate(position)
        for i in self.portals:
            if (i[0], i[1]) == (x, y):
                return i[2], i[3]
        return None

    def get_spawn_point(self, num):
        x, y = self.spawn[num]
        return self.convert_cell((x, y))
    
    def get_ghost_spawn_point(self):
        x, y = self.ghost_spawn_point
        return self.convert_cell((x, y))

def load_map(map_dir):
    json_file = os.path.join(map_dir, 'map.json')
    map_file = os.path.join(map_dir, 'map.csv')

    with open(json_file) as f:
        data = json.load(f)
    images = data['images']

    size = tuple(map(int, [data['width'], data['height']]))
    spawn = [tuple(map(int, i.split(','))) for i in data['spawn']]
    portals = [tuple(map(int, re.split('[, ]', i))) for i in data['portals']]
    print(data)
    ghost_spawn = tuple(map(int, data['ghost_spawn'].split(',')))
    print(ghost_spawn)

    with open(map_file) as f:
        rows = csv.reader(f)

        map_list = [[0] * size[1] for _ in range(0, size[0])]

        y = 0
        for row in rows:
            for x in range(0, size[0]):
                map_list[x][y] = int(row[x])
            y += 1

    """ Feature: Add "thickness" to the walls so it doesn't look like the character is in the walls"
    new_map_list = [[0] * size[0] for _ in range(0, size[1])]
    for y in range(size[1]):
        for x in range(size[0]):
            if map_list[x][y] == Const.MAP_OBSTACLE:
                for dx in range(-1, 2): 
                    for dy in range(-1, 2):
                        if 0 <= x + dx < size[0] and 0 <= y + dy < size[1]:
                            new_map_list[x+dx][y+dy] = Const.MAP_OBSTACLE
    print(new_map_list)
    map_list = new_map_list
    """
    return Map(size, map_list, portals, images, spawn, ghost_spawn, map_dir)
