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
    images: tuple | dict = tuple()

    @classmethod
    def init_convert(cls):
        if isinstance(cls.images, tuple):
            cls.images = tuple(_image.convert_alpha() for _image in cls.images)
        elif isinstance(cls.images, dict):
            cls.images = {key: _image for key, _image in cls.images.items()}
        else:
            raise Exception(
                f"type({cls.__name__}.images) should be either tuple or dict"
            )

    def __init__(self):
        if not self.image_initialized:
            self.init_convert()
            self.image_initialized = True

    def draw(self, screen: pg.Surface):
        pass


class ScoreBoard(__ObjectBase):
    images = (
        crop_image(
            pg.image.load(const.PICTURES_PATH[const.Scene.SCORE_BOARD]),
            const.ARENA_SIZE[0],
            const.ARENA_SIZE[1],
        ),
    )

    def draw(self, screen: pg.Surface):
        screen.blit(self.images[0], (const.ARENA_SIZE[0], 0))


class Item(__ObjectBase):
    images = {
        item: crop_image(
            pg.image.load(const.PICTURES_PATH[item]),
            const.ITEM_RADIUS * 2,
            const.ITEM_RADIUS * 2,
            True,
        )
        for item in const.ItemType
    }

    def __init__(self, item):
        super().__init__()
        self.item = item

    # TODO: change this property's name to `depth`
    @property
    def y(self):
        model = get_game_engine()
        _, y = model.map.convert_coordinate(self.item.position)
        return y

    def draw(self, screen: pg.Surface):
        # render ripple
        ripple = self.item.ripple
        if ripple.show:
            ripple_surface = pg.Surface(ripple.size, pg.SRCALPHA)
            pg.draw.ellipse(
                ripple_surface,
                ripple.color,
                pg.Rect((0, 0), ripple.size),
                width=const.ITEM_RIPPLE_WIDTH,
            )
            screen.blit(
                ripple_surface, pg.Rect(ripple.position, (0, 0)).inflate(ripple.size)
            )

        # render item
        x = self.item.render_position[0] - const.ITEM_RADIUS
        y = self.item.render_position[1] - const.ITEM_RADIUS * 2
        screen.blit(self.images[self.item.type], (x, y))
