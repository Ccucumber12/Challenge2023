import random

import pygame as pg
from pygame import Vector2

import const


def overlap_with(a: pg.Vector2, r_a, b: pg.Vector2, r_b) -> bool:
    """Treat a and b as circle with and return if thay are overlaping."""
    return a.distance_to(b) <= r_a + r_b


def random_fluctuation(value):
    return value * ((random.random() - 0.5) * const.FLUCTUATION_RATIO + 1)


def get_random_pos(r: int) -> pg.Vector2:
    """Return a legal random position for a character of radius r."""
    return pg.Vector2(random.randint(r, const.ARENA_SIZE[0] - r),
                      random.randint(r, const.ARENA_SIZE[1] - r))


def clamp(v, lo, hi):
    if v < lo:
        return lo
    elif v > hi:
        return hi
    else:
        return v


def move_point_in_arena(source: Vector2, target: Vector2):
    eps = 1e-5

    def intersect(p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2):
        a123 = (p2 - p1).cross(p3 - p1)
        a124 = (p2 - p1).cross(p4 - p1)
        return (p4 * a123 - p3 * a124) / (a123 - a124)

    width, height = const.ARENA_SIZE

    if target.x < -eps:
        target = intersect(source, target, Vector2(0, 0), Vector2(0, height))
    if target.x > width + eps:
        target = intersect(source, target, Vector2(width, 0), Vector2(width, height))
    if target.y < -eps:
        target = intersect(source, target, Vector2(0, 0), Vector2(width, 0))
    if target.y > height + eps:
        target = intersect(source, target, Vector2(0, height), Vector2(width, height))

    return target


def get_full_exception(exception: Exception) -> str:
    exception_cls = exception.__class__
    exception_module = exception_cls.__module__
    if exception_module == 'builtins':
        return exception_cls.__qualname__
    else:
        return exception_module + '.' + exception_cls.__qualname__


def crop_image(picture: pg.Surface, desire_width, desire_height, large=False):
    """
    Will scale the image to desire size without changing the ratio of the width and height.

    The size of cropped image won't be bigger than desired size if `large == False`.

    The size of cropped image won't be smaller than desired size if `large == True`.
    """
    image = picture
    bounding_rect = image.get_bounding_rect()
    cropped_image = pg.Surface(bounding_rect.size, pg.SRCALPHA)
    cropped_image.blit(image, (0, 0), bounding_rect)
    width, height = [cropped_image.get_width(), cropped_image.get_height()]
    if large:
        ratio = max(desire_width/width, desire_height/height)
    else:
        ratio = min(desire_width/width, desire_height/height)
    cropped_image = pg.transform.scale(cropped_image, (width*ratio, height*ratio))
    return cropped_image
