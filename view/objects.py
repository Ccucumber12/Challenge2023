"""
* "Static" object means that it is rendered every tick!
* The term "static" is designed compared to "animation", which is dynamic.
"""

import math
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
        img = self.images[self.item.type]
        screen.blit(img, img.get_rect(midbottom=self.item.render_position))


class Player(__ObjectBase):
    images = {
        player: {
            skin: {face_dir: None for face_dir in const.CharacterDirection}
            for skin in [*const.PlayerSkins, "gray", "transparent"]
        }
        for player in const.PlayerIds
    }

    def __init__(self, player):
        super().__init__()
        self.face_dir = const.CharacterDirection.DOWN
        self.player = player
        self.old_position = self.player.position.copy()

    def update_face_dir(self):
        direction = self.player.position - self.old_position
        if direction.length() == 0:
            return
        d = direction.dot((0, 1))
        u = direction.dot((0, -1))
        l = direction.dot((-1, 0))
        r = direction.dot((1, 0))
        max_ = max(d, u, l, r)
        if d == max_:
            self.face_dir = const.CharacterDirection.DOWN
        elif u == max_:
            self.face_dir = const.CharacterDirection.UP
        elif l == max_:
            self.face_dir = const.CharacterDirection.LEFT
        elif r == max_:
            self.face_dir = const.CharacterDirection.RIGHT
        self.old_position = self.player.position.copy()

    @classmethod
    def init_convert(cls):
        for player in const.PlayerIds:
            for skin in const.PlayerSkins:
                for face_dir in const.CharacterDirection:
                    path = (
                        const.PICTURES_PATH[player]
                        / const.PICTURES_PATH[skin]
                        / const.PICTURES_PATH[face_dir]
                    )
                    img = pg.image.load(path)
                    width = (
                        const.PLAYER_RADIUS * 2
                        if face_dir == const.CharacterDirection.DOWN
                        else const.WINDOW_SIZE[0]
                    )
                    height = const.PLAYER_RADIUS * 2
                    match skin:
                        case const.PlayerSkins.NORMAL:
                            cls.images[player][skin][face_dir] = crop_image(
                                img,
                                width,
                                height,
                                face_dir == const.CharacterDirection.DOWN,
                            ).convert_alpha()

                        case const.PlayerSkins.SORTINGHAT:
                            cls.images[player][skin][face_dir] = crop_image(
                                img,
                                width,
                                height,
                            ).convert_alpha()

                        case const.PlayerSkins.SHINING:
                            cls.images[player][skin][face_dir] = crop_image(
                                img, *const.SHINING_PLAYER_SIZE[face_dir], True
                            )

                        case const.PlayerSkins.DEAD:
                            cls.images[player][skin][face_dir] = crop_image(
                                img, *const.DEAD_PLAYER_SIZE[face_dir], True
                            )

        # other skins that is not contained in const.PlayerSkins
        for player in const.PlayerIds:
            for face_dir in const.CharacterDirection:
                img = cls.images[player][const.PlayerSkins.NORMAL][face_dir]
                cls.images[player]["gray"][face_dir] = pg.transform.grayscale(img)
                cls.images[player]["transparent"][face_dir] = img.copy()
                cls.images[player]["transparent"][face_dir].set_alpha(
                    const.CLOAK_TRANSPARENCY
                )

        # grayscale -> petrified

        # transparent -> cloak

    # TODO: change this property's name to `depth`
    @property
    def y(self):
        model = get_game_engine()
        _, y = model.map.convert_coordinate(self.player.position)
        return y

    def draw(self, screen: pg.Surface):
        model = get_game_engine()

        player = self.player
        quarter_sec = model.timer // (const.FPS // 4)

        if player.dead:
            # draw character
            match self.face_dir:
                case const.CharacterDirection.DOWN | const.CharacterDirection.UP:
                    delta = pg.Vector2(0, 0)
                case const.CharacterDirection.LEFT:
                    delta = pg.Vector2(7, 0)
                case const.CharacterDirection.RIGHT:
                    delta = pg.Vector2(-7, 0)
            img = self.images[player.player_id][const.PlayerSkins.DEAD][self.face_dir]
            screen.blit(img, img.get_rect(midbottom=(player.position + delta)))

            # draw cooldown circle
            dead_time = self.player.respawn_time - model.timer
            angle = (dead_time / const.PLAYER_RESPAWN_TIME) * 2 * math.pi
            radius = const.PLAYER_REVIVE_CIRCLE_RADIUS * 2
            rect = pg.Rect((player.position + pg.Vector2(0, -30)), (0, 0)).inflate(
                radius, radius
            )
            pg.draw.arc(
                screen,
                const.PLAYER_COLOR[player.player_id],
                rect,
                math.pi / 2 - angle,
                math.pi / 2,
                width=6,
            )

        elif (
            player.effect_timer < const.ITEM_LOSE_EFFECT_HINT_TIME
            and quarter_sec % 2 == 0
        ):
            img = self.images[player.player_id][const.PlayerSkins.NORMAL][self.face_dir]
            screen.blit(img, img.get_rect(midbottom=player.position))

        elif player.effect == const.EffectType.PETRIFICATION:
            img = self.images[player.player_id]["gray"][self.face_dir]
            screen.blit(img, img.get_rect(midbottom=player.position))

        elif player.effect == const.EffectType.CLOAK:
            img = self.images[player.player_id]["transparent"][self.face_dir]
            screen.blit(img, img.get_rect(midbottom=player.position))

        elif player.effect == const.EffectType.SORTINGHAT:
            img = self.images[player.player_id][const.PlayerSkins.SORTINGHAT][
                self.face_dir
            ]
            screen.blit(img, img.get_rect(midbottom=player.position))

        elif player.effect == const.EffectType.REMOVED_SORTINGHAT:
            img = self.images[player.player_id][const.PlayerSkins.SHINING][
                self.face_dir
            ]
            screen.blit(img, img.get_rect(midbottom=player.position))

        else:
            img = self.images[player.player_id][const.PlayerSkins.NORMAL][self.face_dir]
            screen.blit(img, img.get_rect(midbottom=player.position))
