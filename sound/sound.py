import os

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
        self.mute_BGM = False
        self.mute_sound = False
        pg.mixer.music.load(const.MUSIC_PATH[const.STATE_MENU])
        self.sound = {}
        for effect, paths in const.EFFECT_SOUND_PATH.items():
            self.sound[effect] = []
            for path in paths:
                self.sound[effect].append(pg.mixer.Sound(os.path.join(const.EFFECT_SOUND_DIR, path)))

    def handle_effect_sound(self, event: EventPlayerGetItem):
        if event.effect_type in self.sound:
            for s in self.sound[event.effect_type]:
                s.play()

    def handle_teleport_sound(self, event: EventGhostTeleport):
        self.sound[const.GhostState.TELEPORT][0].play()

    def handle_petrification_sound(self, event: EventCastPetrification):
        self.sound[const.ItemType.PETRIFICATION][0].play()

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventStateChange, self.handle_state_change)
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventMuteMusic, self.handle_mute)
        ev_manager.register_listener(EventPlayerGetItem, self.handle_effect_sound)
        ev_manager.register_listener(EventGhostTeleport, self.handle_teleport_sound)
        ev_manager.register_listener(EventCastPetrification, self.handle_petrification_sound)

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pg.mixer.music.load(const.MUSIC_PATH[const.STATE_MENU])
        if not self.mute_BGM:
            pg.mixer.music.play(-1)

    def handle_state_change(self, event):
        if event.state in const.MUSIC_PATH:
            pg.mixer.music.load(const.MUSIC_PATH[event.state])
            if not self.mute_BGM:
                pg.mixer.music.play(-1)

    def handle_every_tick(self, event):
        pass

    def handle_mute(self, event):
        if event.type == "BGM":
            if self.mute_BGM:
                self.mute_BGM = False
                pg.mixer.music.play(-1)
            else:
                self.mute_BGM = True
                pg.mixer.music.stop()
        elif event.type == "effect":
            if self.mute_sound:
                self.mute_sound = False
                pg.mixer.set_num_channels(8)
            else:
                self.mute_sound = True
                pg.mixer.set_num_channels(0)  # Mute all sound effect channels
