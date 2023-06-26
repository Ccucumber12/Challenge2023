import os

import pygame as pg

from instances_manager import get_game_engine
from instances_manager import get_event_manager
from event_manager.events import EventInitialize, EventEveryTick
import const


class GraphicalView:
    """
    Draws the state of GameEngine onto the screen.
    """
    background = pg.Surface(const.ARENA_SIZE)

    def __init__(self):
        """
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        """
        self.register_listeners()

        self.screen = pg.display.set_mode(const.WINDOW_SIZE)
        pg.display.set_caption(const.WINDOW_CAPTION)
        self.background.fill(const.BACKGROUND_COLOR)

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
        for item in const.ITEM_SET:
            picture = pg.image.load(const.PICTURES_PATH[item])
            self.pictures[item] = crop(picture, const.ITEM_WIDTH, const.ITEM_HEIGHT)
        for player in const.PLAYER_IDS:
            picture = pg.image.load(const.PICTURES_PATH[player])
            self.pictures[player] = crop(picture, const.PLAYER_RADIUS*2, const.PLAYER_RADIUS*2)
        for ghost in const.GHOST_IDS:
            picture = pg.image.load(const.PICTURES_PATH[ghost])
            self.pictures[ghost] = crop(picture, const.GHOST_RADIUS*2, const.GHOST_RADIUS*2)
        picture = pg.image.load(const.PICTURES_PATH[const.SCENE.SCORE_BOARD])
        self.pictures[const.SCENE.SCORE_BOARD] = crop(picture, const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        # print(self.pictures[Const.SCENE.SCORE_BOARD].get_width())
        # print(self.pictures[Const.SCENE.SCORE_BOARD].get_height())
        picture = pg.image.load(const.PICTURES_PATH[const.SCENE.TITLE])
        self.pictures[const.SCENE.TITLE] = crop(picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        # print(self.pictures[Const.SCENE.TITLE].get_width())
        # print(self.pictures[Const.SCENE.TITLE].get_height())

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pass

    def handle_every_tick(self, event):
        self.display_fps()

        model = get_game_engine()
        cur_state = model.state
        if cur_state == const.STATE_MENU: self.render_menu()
        elif cur_state == const.STATE_PLAY: self.render_play()
        elif cur_state == const.STATE_STOP: self.render_stop()
        elif cur_state == const.STATE_ENDGAME: self.render_endgame()

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def display_fps(self):
        """
        Display the current fps on the window caption.
        """
        model = get_game_engine()
        pg.display.set_caption(f'{const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')

    def render_menu(self):
        # draw background
        # self.screen.fill(Const.BACKGROUND_COLOR)
        self.screen.blit(self.pictures[const.SCENE.TITLE], ((const.WINDOW_SIZE[0]-const.TITLE_SIZE[0])/2, 0))

        # draw text
        font = pg.font.Font(os.path.join(const.FONT_PATH, "magic-school.one.ttf"), 36)
        text_surface = font.render("Press [space] to start ...", 1, pg.Color('gray88'))
        text_center = (const.WINDOW_SIZE[0] / 2, 20)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))

        pg.display.flip()

    def render_play(self):
        # draw background
        self.screen.fill(const.BACKGROUND_COLOR)

        # draw players
        model = get_game_engine()
        game_map = model.map
        objects = []
        for item in model.items:
            center = list(map(int, item.position))
            lt = [x - y for x, y in zip(center, [const.ITEM_WIDTH/2, const.ITEM_HEIGHT/2])]
            coord = game_map.convert_coordinate(item.position)
            objects.append((coord[1], const.OBJECT_TYPE.ITEM, item.type, lt))
        for player in model.players:
            center = list(map(int, player.position))
            lt = [x - y for x, y in zip(center, [const.PLAYER_RADIUS, const.PLAYER_RADIUS])]
            coord = game_map.convert_coordinate(player.position)
            objects.append((coord[1], const.OBJECT_TYPE.PLAYER, player.player_id, lt))
        for ghost in model.ghosts:
            center = list(map(int, ghost.position))
            lt = [x - y for x, y in zip(center, [const.GHOST_RADIUS, const.GHOST_RADIUS])]
            coord = game_map.convert_coordinate(ghost.position)
            objects.append((coord[1], const.OBJECT_TYPE.GHOST, ghost.ghost_id, lt))
        for row, image in game_map.images:
            objects.append((row, const.OBJECT_TYPE.MAP, image))

        objects.sort(key=lambda x: (x[0], x[1]))
        for i in objects:
            if i[1] == const.OBJECT_TYPE.PLAYER:
                self.screen.blit(self.pictures[i[2]], i[3])
            elif i[1] == const.OBJECT_TYPE.GHOST:
                self.screen.blit(self.pictures[i[2]], i[3])
            elif i[1] == const.OBJECT_TYPE.MAP:
                self.screen.blit(i[2], (0, 0))
            elif i[1] == const.OBJECT_TYPE.ITEM:
                # It's acually is a rectangle.
                self.screen.blit(self.pictures[i[2]], i[3])

        # Scoreboard
        self.screen.blit(self.pictures[const.SCENE.SCORE_BOARD], (const.ARENA_SIZE[0], 0))
        font = pg.font.Font(os.path.join(const.FONT_PATH, "magic-school.one.ttf"), 36)
        def print_digit(digit: int, position):
            text_surface = font.render(str(digit), True, pg.Color('black'))
            self.screen.blit(text_surface, text_surface.get_rect(center=position))
        # Time
        count_down = (const.GAME_LENGTH - model.timer) // const.FPS
        print_digit(count_down//60//10, const.TIME_POSITION[0])
        print_digit(count_down//60%10, const.TIME_POSITION[1])
        print_digit(count_down%60//10, const.TIME_POSITION[2])
        print_digit(count_down%60%10, const.TIME_POSITION[3])

        for i in range(const.NUM_OF_PLAYERS):
            score = model.players[i].score
            j = 1000
            for position in const.SCORE_POSITION[i]:
                print_digit(int(score//j%10), position)
                j /= 10

        # pg.draw.circle(self.screen, pg.Color('red'), (854, 161), 3)

        pg.display.flip()

    def render_stop(self):
        pass

    def render_endgame(self):
        # draw background
        self.screen.fill(const.BACKGROUND_COLOR)

        pg.display.flip()
