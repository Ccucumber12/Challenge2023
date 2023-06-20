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
        items = []
        for item in model.items:
            center = list(map(int, item.position))
            coord = game_map.convert_coordinate(item.position)
            items.append((coord[1], 4, item.item_id, center))
        for player in model.players:
            center = list(map(int, player.position))
            coord = game_map.convert_coordinate(player.position)
            items.append((coord[1], 3, player.player_id, center))
        for ghost in model.ghosts:
            center = list(map(int, ghost.position))
            coord = game_map.convert_coordinate(ghost.position)
            items.append((coord[1], 2, ghost.ghost_id, center))
        for row, image in game_map.images:
            items.append((row, 1, image))

        items.sort(key=lambda x: (x[0], x[1]))
        for i in items:
            if i[1] == 3:
                pg.draw.circle(self.screen, Const.PLAYER_COLOR[i[2]], i[3], Const.PLAYER_RADIUS)
            elif i[1] == 2:
                pg.draw.circle(self.screen, Const.GHOST_COLOR[i[2]], i[3], Const.GHOST_RADIUS)
            elif i[1] == 1:
                self.screen.blit(i[2], (0, 0))
            elif i[1] == 4:
                # It's acually is a rectangle, but here I just draw a circle for test.
                pg.draw.circle(self.screen, Const.ITEM_TEST_COLOR, i[3], Const.ITEM_WIDTH)

        for particle in model.particles:
            particle.emit()

        pg.display.flip()

    def render_stop(self):
        pass

    def render_endgame(self):
        # draw background
        self.screen.fill(Const.BACKGROUND_COLOR)

        pg.display.flip()
