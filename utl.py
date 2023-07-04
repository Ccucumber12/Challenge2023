import random

import pygame as pg

import const


def overlaped(a: pg.Vector2, r_a, b: pg.Vector2, r_b) -> bool:
    """ Treat a and b as circle with and return if thay are opverlaped"""
    return a.distance_to(b) <= r_a + r_b

def random_fluctuation(value):
    return value * ((random.random() - 0.5) * const.FLUCTUATION_RATIO + 1)