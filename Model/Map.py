import Const
import os
import re


class Map:

    def __init__(self, size, map_list, portals, image_files):
        self.size = size
        self.map = map_list
        self.image_files = image_files
        self.portals = portals

    def convert_coordinate(self, position):
        x = max(0, min(self.size[0] - 1, int(position[0] * self.size[0] / Const.ARENA_SIZE[0])))
        y = max(0, min(self.size[1] - 1, int(position[1] * self.size[1] / Const.ARENA_SIZE[1])))
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

    image_files = []
    for i in os.listdir(map_dir):
        if re.match("^-?[0-9]+.png$", i):
            image_files.append(os.path.join(map_dir, i))

    return Map(size, map_list, portals, image_files)
