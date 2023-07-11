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
                 name,
                 size,
                 map_list,
                 portals,
                 images,
                 spawn,
                 ghost_spawn_point,
                 map_dir,
                 portkey_map):
        self.name = name
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals
        self.spawn = spawn
        self.ghost_spawn_point = ghost_spawn_point
        self.map_dir = map_dir
        self.connected_component = dict()
        self.closest_cell = dict()
        self.number_of_connected_components = dict()
        self.portkey_map = portkey_map

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
        if self.portkey_map[x][y] == -1:
            return None
        return self.portals[self.portkey_map[x][y]]

    def get_spawn_point(self, num):
        x, y = self.spawn[num]
        return self.convert_cell((x, y))

    def get_ghost_spawn_point(self):
        x, y = self.ghost_spawn_point
        return self.convert_cell((x, y))

    def find_connected_components(self, without):
        width, height = self.size
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
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if self.map[nx][ny] in without:
                        continue
                    if connected_component[nx][ny] != -1:
                        continue
                    connected_component[nx][ny] = ccid
                    q.put((nx, ny))

        connected_component = [[-1] * height for _ in range(0, width)]
        cnt = 0
        for sx in range(0, width):
            for sy in range(0, height):
                if self.map[sx][sy] in without:
                    continue
                if connected_component[sx][sy] != -1:
                    continue
                find_connected_component(sx, sy, cnt)
                cnt += 1
        self.connected_component[without] = connected_component
        self.number_of_connected_components[without] = cnt

    def in_same_connected_component(self, p1, p2, without=None):
        if without is None:
            without = {const.MAP_OBSTACLE}
        without = frozenset(without)
        if without not in self.connected_component:
            self.find_connected_components(without)
        g1 = self.convert_coordinate(p1)
        g2 = self.convert_coordinate(p2)
        return self.connected_component[without][g1[0]][g1[1]] \
            == self.connected_component[without][g2[0]][g2[1]]

    def find_closest_cells(self, without):
        if without not in self.connected_component:
            self.find_connected_components(without)

        width, height = self.size
        cnt = self.number_of_connected_components[without]
        closest_distance = [[[(-1, -1)] * height for _ in range(0, width)] for _ in range(0, cnt)]

        def calculate_closest_distance(ccid):
            q = Queue()
            for i in range(0, width):
                for j in range(0, height):
                    if self.connected_component[without][i][j] == ccid:
                        q.put((i, j))
                        closest_distance[ccid][i][j] = (i, j)
            while not q.empty():
                tx, ty = q.get()
                direction = [[0, 1], [1, 0], [0, -1], [-1, 0]]
                for dx, dy in direction:
                    nx = tx + dx
                    ny = ty + dy
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if closest_distance[ccid][nx][ny] != (-1, -1):
                        continue
                    closest_distance[ccid][nx][ny] = closest_distance[ccid][tx][ty]
                    q.put((nx, ny))

        for i in range(0, cnt):
            calculate_closest_distance(i)

        self.closest_cell[without] = closest_distance

    def get_closest_reachable_cell(self, p, source, without=None):
        if without is None:
            without = {const.MAP_OBSTACLE}
        without = frozenset(without)
        if without not in self.closest_cell:
            self.find_closest_cells(without)
        g = self.convert_coordinate(p)
        gs = self.convert_coordinate(source)
        cc = self.connected_component[without][gs[0]][gs[1]]
        ans = self.closest_cell[without][cc][g[0]][g[1]]
        return ans


def load_map(map_dir):
    json_file = os.path.join(map_dir, 'map.json')
    map_file = os.path.join(map_dir, 'map.csv')

    with open(json_file) as f:
        data = json.load(f)
    images = data['images']

    name = os.path.basename(os.path.dirname(json_file))
    size = (data['width'], data['height'])
    spawn = [tuple(i) for i in data['spawn']]
    portals = [tuple(i) for i in data['portals']]
    ghost_spawn = tuple(data['ghost_spawn'])

    with open(map_file) as f:
        rows = csv.reader(f)

        map_list = [[0] * size[1] for _ in range(0, size[0])]
        portkey_map = [[-1] * size[1] for _ in range(0, size[0])]

        y = 0
        for row in rows:
            for x in range(0, size[0]):
                map_list[x][y] = min(int(row[x]), const.MAP_PORTKEY)
                if map_list[x][y] >= const.MAP_PORTKEY:
                    portkey_map[x][y] = int(row[x]) - const.MAP_PORTKEY
            y += 1

    return Map(name, size, map_list, portals, images, spawn, ghost_spawn, map_dir, portkey_map)
