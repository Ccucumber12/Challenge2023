import math

import pygame as pg


def overlaped(a: pg.Vector2, r_a, b: pg.Vector2, r_b):
    """ Treat a and b as circle with and return if thay are opverlaped"""
    return math.hypot(a.x - b.x, a.y - b.y) <= r_a + r_b
