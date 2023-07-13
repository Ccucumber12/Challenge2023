import pygame as pg

import const
from event_manager.events import (EventEveryTick, EventInitialize, EventMuteMusic, EventPlayerMove,
                                  EventQuit, EventStateChange, EventHelpMenu)
from instances_manager import get_event_manager, get_game_engine


class Controller:
    """
    Handles the control input. Either from keyboard or from AI.
    """

    def __init__(self):
        """
        This function is called when the Controller is created. For more specific objects related to a game instance
            , they should be initialized in Controller.initialize()
        """
        self.register_listeners()

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        pass

    def handle_every_tick(self, event):
        key_down_events = []
        ev_manager = get_event_manager()
        model = get_game_engine()
        # Called once per game tick. We check our keyboard presses here.
        for event_pg in pg.event.get():
            # handle window manager closing our window
            if event_pg.type == pg.QUIT:
                ev_manager.post(EventQuit())
            if event_pg.type == pg.KEYDOWN:
                if event_pg.key == const.MUTE_BGM_KEY:
                    ev_manager.post(EventMuteMusic("BGM"))
                if event_pg.key == const.MUTE_EFFECT_SOUND_KEY:
                    ev_manager.post(EventMuteMusic("effect"))
                key_down_events.append(event_pg)
            # for orientating
            if event_pg.type == pg.MOUSEBUTTONDOWN:
                if event_pg.button == 1:  # Left mouse button
                    mouse_pos = event_pg.pos
                    x, y = mouse_pos
                    print(f"Mouse click position: ({x}, {y})")

        cur_state = model.state
        if cur_state == const.STATE_MENU:
            self.ctrl_menu(key_down_events)
        if cur_state == const.STATE_PLAY:
            self.ctrl_play(key_down_events)
        if cur_state == const.STATE_STOP:
            self.ctrl_stop(key_down_events)
        if cur_state == const.STATE_ENDGAME:
            self.ctrl_endgame(key_down_events)

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def ctrl_menu(self, key_down_events):
        ev_manager = get_event_manager()
        for event_pg in key_down_events:
            if event_pg.type == pg.KEYDOWN and event_pg.key == pg.K_SPACE:
                ev_manager.post(EventStateChange(const.STATE_PLAY))
            elif event_pg.type == pg.KEYDOWN and event_pg.key == pg.K_ESCAPE:
                ev_manager.post(EventHelpMenu())

    def ctrl_play(self, key_down_events):
        ev_manager = get_event_manager()
        model = get_game_engine()
        keys = pg.key.get_pressed()
        for player_id, key_val in const.PLAYER_KEYS.items():
            if model.ai[player_id] != 'manual':
                continue
            direction = pg.Vector2(0, 0)
            for k, v in key_val.items():
                if keys[k]:
                    direction += v
            if direction.length() != 0:
                ev_manager.post(EventPlayerMove(player_id, direction, full_length=True))

    def ctrl_stop(self, key_down_events):
        pass

    def ctrl_endgame(self, key_down_events):
        pass
