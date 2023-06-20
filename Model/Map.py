import Const
import os
import re
import pygame


class Map:

    def __init__(self, size, map_list, portals, images):
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals

    def convert_coordinate(self, position):
        """
        For detection of obstacles
        """
        x = max(0, min(self.size[0] - 1, int(position[0] * self.size[0] / Const.ARENA_SIZE[0])))
        y = max(0, min(self.size[1] - 1, int(position[1] * self.size[1] / Const.ARENA_SIZE[1])))
        return x, y

    def convert_cell(self, cell, dx, dy):
        #dx, dy denote the specific part of the cell that should be traveled to
        x = max(0, min(Const.ARENA_SIZE[0], (cell[0] + 0.5 * (1 + dx) ) * Const.ARENA_SIZE[0] / self.size[0]))
        y = max(0, min(Const.ARENA_SIZE[1], (cell[1] + 0.5 * (1 + dy) ) * Const.ARENA_SIZE[1] / self.size[1]))
        return x, y

    def get_type(self, position):
        x, y = self.convert_coordinate(position)
        return self.map[x][y]

    def get_portal(self, position):
        x, y = self.convert_coordinate(position)
        for i in self.portals:
            if (i[0], i[1]) == (x, y):
                return i[2], i[3]
        return None


def load_map(map_dir):
    map_file = os.path.join(map_dir, 'map.txt')
    portal_file = os.path.join(map_dir, 'portal.txt')
    with open(map_file) as f:
        size = [int(i) for i in f.readline().split(' ')]
        map_list = [[0] * size[0] for _ in range(0, size[1])]
        y = 0
        for line in f.readlines():
            if len(line) == 0:
                continue
            for x in range(0, size[0]):
                map_list[x][y] = int(line[x])
            y += 1

    with open(portal_file) as f:
        num_portals = int(f.readline())
        portals = []
        for i in range(0, num_portals):
            portals.append([int(i) for i in f.readline().split(' ')])

    images = []
    for i in os.listdir(map_dir):
        if re.match("^-?[0-9]+.png$", i):
            loaded_image = pygame.image.load(os.path.join(map_dir, i))
            loaded_image = pygame.transform.scale(loaded_image, Const.ARENA_SIZE)
            images.append((int(i[:-4]), loaded_image))

    return Map(size, map_list, portals, images)
