import os

import pygame as pg

from InstancesManager import get_game_engine
from InstancesManager import get_event_manager
from EventManager.Events import EventInitialize, EventEveryTick
import Const


class GraphicalView:
    """
    Draws the state of GameEngine onto the screen.
    """
    background = pg.Surface(Const.ARENA_SIZE)

    def __init__(self):
        """
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        """
        self.register_listeners()

        self.screen = pg.display.set_mode(Const.WINDOW_SIZE)
        pg.display.set_caption(Const.WINDOW_CAPTION)
        self.background.fill(Const.BACKGROUND_COLOR)

        # scale the pictures to proper size
        self.pictures = {}
        def crop(picture: pg.Surface, desire_width, desire_height):
            """
            Will scale the image to desire size without changing the ratio of the width and height.
            The size of cropped image won't be bigger than desire size.
            """
            picture = picture.convert_alpha()
            bounding_rect = picture.get_bounding_rect()
            cropped_image = pg.Surface(bounding_rect.size, pg.SRCALPHA)
            cropped_image.blit(picture, (0, 0), bounding_rect)
            width, height = [cropped_image.get_width(), cropped_image.get_height()]
            ratio = min(desire_width/width, desire_height/height)
            cropped_image = pg.transform.scale(cropped_image, (width*ratio, height*ratio))
            return cropped_image
        for item in Const.ITEM_SET:
            picture = pg.image.load(Const.PICTURES_PATH[item])
            self.pictures[item] = crop(picture, Const.ITEM_WIDTH, Const.ITEM_HEIGHT)
        for player in Const.PLAYER_IDS:
            picture = pg.image.load(Const.PICTURES_PATH[player])
            self.pictures[player] = crop(picture, Const.PLAYER_RADIUS*2, Const.PLAYER_RADIUS*2)
        for ghost in Const.GHOST_IDS:
            picture = pg.image.load(Const.PICTURES_PATH[ghost])
            self.pictures[ghost] = crop(picture, Const.GHOST_RADIUS*2, Const.GHOST_RADIUS*2)

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pass

    def handle_every_tick(self, event):
        self.display_fps()

        model = get_game_engine()
        cur_state = model.state
        if cur_state == Const.STATE_MENU: self.render_menu()
        elif cur_state == Const.STATE_PLAY: self.render_play()
        elif cur_state == Const.STATE_STOP: self.render_stop()
        elif cur_state == Const.STATE_ENDGAME: self.render_endgame()

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def display_fps(self):
        """
        Display the current fps on the window caption.
        """
        model = get_game_engine()
        pg.display.set_caption(f'{Const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')

    def render_menu(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)

        # draw text
        font = pg.font.Font(None, 36)
        text_surface = font.render("Press [space] to start ...", 1, pg.Color('gray88'))
        text_center = (Const.ARENA_SIZE[0] / 2, Const.ARENA_SIZE[1] / 2)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))

        pg.display.flip()

    def render_play(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)

        # draw players
        model = get_game_engine()
        game_map = model.map
        objects = []
        for item in model.items:
            center = list(map(int, item.position))
            lt = [x - y for x, y in zip(center, [Const.ITEM_WIDTH/2, Const.ITEM_HEIGHT/2])]
            coord = game_map.convert_coordinate(item.position)
            objects.append((coord[1], Const.OBJECT_TYPE.ITEM, item.type, lt))
        for player in model.players:
            center = list(map(int, player.position))
            lt = [x - y for x, y in zip(center, [Const.PLAYER_RADIUS, Const.PLAYER_RADIUS])]
            coord = game_map.convert_coordinate(player.position)
            objects.append((coord[1], Const.OBJECT_TYPE.PLAYER, player.player_id, lt))
        for ghost in model.ghosts:
            center = list(map(int, ghost.position))
            lt = [x - y for x, y in zip(center, [Const.GHOST_RADIUS, Const.GHOST_RADIUS])]
            coord = game_map.convert_coordinate(ghost.position)
            objects.append((coord[1], Const.OBJECT_TYPE.GHOST, ghost.ghost_id, lt))
        for row, image in game_map.images:
            objects.append((row, Const.OBJECT_TYPE.MAP, image))

        objects.sort(key=lambda x: (x[0], x[1]))
        for i in objects:
            if i[1] == Const.OBJECT_TYPE.PLAYER:
                self.screen.blit(self.pictures[i[2]], i[3])
            elif i[1] == Const.OBJECT_TYPE.GHOST:
                self.screen.blit(self.pictures[i[2]], i[3])
            elif i[1] == Const.OBJECT_TYPE.MAP:
                self.screen.blit(i[2], (0, 0))
            elif i[1] == Const.OBJECT_TYPE.ITEM:
                # It's acually is a rectangle.
                self.screen.blit(self.pictures[i[2]], i[3])

        pg.display.flip()

    def render_stop(self):
        pass

    def render_endgame(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)

        pg.display.flip()
