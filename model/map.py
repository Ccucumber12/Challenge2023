import csv
import json
import os

import pygame as pg

import const
import util
import random

from queue import Queue


class Map:

    def __init__(self,
                 size,
                 map_list,
                 portals,
                 images,
                 spawn,
                 ghost_spawn_point,
                 map_dir,
                 connected_component,
                 closest_cell):
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals
        self.spawn = spawn
        self.ghost_spawn_point = ghost_spawn_point
        self.map_dir = map_dir
        self.connected_component = connected_component
        self.closest_cell = closest_cell

    def convert_coordinate(self, position: tuple | pg.Vector2) -> tuple:
        """
        Return the coordinate based on self.size of position.
        position is a coordinate based on const.ARENA_SIZE.
        """
        x = util.clamp(int(position[0] * self.size[0] / const.ARENA_SIZE[0]), 0, self.size[0] - 1)
        y = util.clamp(int(position[1] * self.size[1] / const.ARENA_SIZE[1]), 0, self.size[1] - 1)
        return x, y

    def convert_cell(self, position: tuple | pg.Vector2) -> pg.Vector2:
        """Similar to convert_coordinate(), but is the reverse version."""
        x = util.clamp(position[0] * const.ARENA_SIZE[0] / self.size[0], 0, const.ARENA_SIZE[0] - 1)
        y = util.clamp(position[1] * const.ARENA_SIZE[1] / self.size[1], 0, const.ARENA_SIZE[1] - 1)
        return pg.Vector2(x, y)

    def get_random_pos(self, r: int) -> pg.Vector2:
        ret = pg.Vector2(random.randint(r, const.ARENA_SIZE[0] - r),
                      random.randint(r, const.ARENA_SIZE[1] - r))
        while self.get_type(ret) == const.MAP_OBSTACLE:
            ret = pg.Vector2(random.randint(r, const.ARENA_SIZE[0] - r),
                        random.randint(r, const.ARENA_SIZE[1] - r))
        return ret
            
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

    def in_same_connected_component(self, p1, p2):
        g1 = self.convert_coordinate(p1)
        g2 = self.convert_coordinate(p2)
        return self.connected_component[g1[0]][g1[1]] == self.connected_component[g2[0]][g2[1]]


def load_map(map_dir):
    json_file = os.path.join(map_dir, 'map.json')
    map_file = os.path.join(map_dir, 'map.csv')

    with open(json_file) as f:
        data = json.load(f)
    images = data['images']

    size = (data['width'], data['height'])
    spawn = [tuple(i) for i in data['spawn']]
    portals = [tuple(tuple(j) for j in i) for i in data['portals']]
    ghost_spawn = tuple(data['ghost_spawn'])

    with open(map_file) as f:
        rows = csv.reader(f)

        map_list = [[0] * size[1] for _ in range(0, size[0])]

        y = 0
        for row in rows:
            for x in range(0, size[0]):
                map_list[x][y] = int(row[x])
            y += 1

    # find connected components
    def find_connected_component(sx, sy, ccid):
        q = Queue()
        q.put((sx, sy))
        connected_component[sx][sy] = ccid
        direction = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        while not q.empty():
            tx, ty = q.get()
            for dx, dy in direction:
                nx = tx + dx
                ny = ty + dy
                if not (0 <= nx < size[0] and 0 <= ny < size[1]):
                    continue
                if map_list[nx][ny] == const.MAP_OBSTACLE:
                    continue
                if connected_component[nx][ny] != -1:
                    continue
                connected_component[nx][ny] = ccid
                q.put((nx, ny))

    connected_component = [[-1] * size[1] for _ in range(0, size[0])]
    cnt = 0
    for sx in range(0, size[0]):
        for sy in range(0, size[1]):
            if map_list[sx][sy] == const.MAP_OBSTACLE:
                continue
            if connected_component[sx][sy] != -1:
                continue
            find_connected_component(sx, sy, cnt)
            cnt += 1

    # calculate closest distance
    closest_distance = [[[(-1, -1)] * size[1] for _ in range(0, size[0])] for _ in range(0, cnt)]

    def calculate_closest_distance(ccid):
        q = Queue()
        for i in range(0, size[0]):
            for j in range(0, size[1]):
                if connected_component[i][j] == ccid:
                    q.put((i, j))
                    closest_distance[ccid][i][j] = (i, j)
        while not q.empty():
            tx, ty = q.get()
            direction = [[0, 1], [1, 0], [0, -1], [-1, 0]]
            for dx, dy in direction:
                nx = tx + dx
                ny = ty + dy
                if not (0 <= nx < size[0] and 0 <= ny < size[1]):
                    continue
                if closest_distance[ccid][nx][ny] != (-1, -1):
                    continue
                closest_distance[ccid][nx][ny] = closest_distance[ccid][tx][ty]
                q.put((nx, ny))
    for i in range(0, cnt):
        calculate_closest_distance(i)

    return Map(size, map_list, portals, images, spawn, ghost_spawn, map_dir, connected_component, closest_distance)
