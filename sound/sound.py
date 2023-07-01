import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager, get_game_engine

class BackGroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created.
        For more specific objects related to a game instance
            , they should be initialized in BackGroundMusic.initialize()
        """
        self.register_listeners()
        pg.mixer.init()
        self.musics = {}
        self.current_music: pg.mixer.music
        for state, path in const.MUSIC_PATH.items():
            self.musics[state] = pg.mixer.Sound(path)
        self.current_music = self.musics[const.STATE_MENU]
        self.current_music.play()

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventStateChange, self.handle_state_change)
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pass

    def handle_state_change(self, event):
        self.current_music.stop()
        if event.state in self.musics:
            self.current_music = self.musics[event.state]
            self.current_music.play()

    def handle_every_tick(self, event):
        pass