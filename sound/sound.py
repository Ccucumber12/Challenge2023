import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager, get_game_engine


class BackGroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created.
        For more specific objects related to a game instance,
        they should be initialized in BackGroundMusic.initialize()
        """
        self.register_listeners()
        pg.mixer.init()
        self.musics = {}
        self.muted = False
        pg.mixer.music.load(const.MUSIC_PATH[const.STATE_MENU])

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventStateChange, self.handle_state_change)
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventMuteMusic, self.handle_mute)

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pg.mixer.music.load(const.MUSIC_PATH[const.STATE_MENU])
        if not self.muted:
            pg.mixer.music.play(-1)

    def handle_state_change(self, event):
        if event.state in const.MUSIC_PATH:
            pg.mixer.music.load(const.MUSIC_PATH[event.state])
            if not self.muted:
                pg.mixer.music.play(-1)

    def handle_every_tick(self, event):
        pass

    def handle_mute(self, event):
        if self.muted:
            pg.mixer.music.play(-1)
            self.muted = False
        else:
            self.muted = True
            pg.mixer.music.stop()
