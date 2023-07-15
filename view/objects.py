"""
* "Static" object means that it is rendered every tick!
* The term "static" is designed compared to "animation", which is dynamic.
"""

import pygame as pg
import const
from util import crop_image
from instances_manager import get_game_engine


class __ObjectBase:
    image_initialized = False
    images = tuple()

    @classmethod
    def init_convert(cls):
        cls.images = tuple(_image.convert_alpha() for _image in cls.images)

    def __init__(self):
        if not self.image_initialized:
            self.init_convert()
            self.image_initialized = True


class ScoreBoard(__ObjectBase):
    images = (
        crop_image(
            pg.image.load(const.PICTURES_PATH[const.Scene.SCORE_BOARD]),
            const.ARENA_SIZE[0],
            const.ARENA_SIZE[1],
        ),
    )

    def draw(self, screen):
        screen.blit(self.images[0], (const.ARENA_SIZE[0], 0))
