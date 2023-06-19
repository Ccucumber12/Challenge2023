# obstacle: red #FF0000
# puddle: blue #0000FF
# road: other (prefer white)
# be careful that the alpha channel is ignored

import numpy as np
import cv2
import sys


def gen_map_file_from_image(img_path, width, height, threshold=0.8, distance=10):
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    image_width = img.shape[0]
    image_height = img.shape[1]

    map_list = [[0 for j in range(width)] for i in range(height)]
    for x in range(width):
        for y in range(height):
            obstacle = 0
            puddle = 0
            total = 0
            for i in range(int(image_width / width * x), int(image_width / width * (x + 1))):
                for j in range(int(image_height / height * y), int(image_height / height * (y + 1))):
                    total += 1
                    # OpenCV uses BGR
                    b, g, r = [int(v) for v in img[i][j]]
                    if b + g + (255 - r) <= distance:
                        obstacle += 1
                    elif (255 - b) + g + r <= distance:
                        puddle += 1
            if obstacle / total >= threshold:
                map_list[x][y] = 2
            elif puddle / total >= threshold:
                map_list[x][y] = 1
            else:
                map_list[x][y] = 0

    print(width, height)
    for i in map_list:
        print(''.join([str(j) for j in i]))


def print_help():
    print('Usage: python MapTool.py <img path> <width> <height> [threshold] [distance]')


if len(sys.argv) < 4:
    print_help()
    exit(0)

path, width, height = sys.argv[1:4]
width = int(width)
height = int(height)
if len(sys.argv) == 4:
    gen_map_file_from_image(path, width, height)
elif len(sys.argv) == 5:
    gen_map_file_from_image(path, width, height, float(sys.argv[4]))
elif len(sys.argv) == 6:
    gen_map_file_from_image(path, width, height, int(sys.argv[5]))
else:
    print_help()
    exit(0)