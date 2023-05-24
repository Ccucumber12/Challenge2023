import random

import pygame as pg

from EventManager.EventManager import *
import Const
from EventManager.Events import EventInitialize, EventQuit, EventStateChange, EventEveryTick, EventTimesUp, \
    EventPlayerMove
from Model.Character import Player, Ghost
from Model.Map import load_map
from InstancesManager import get_event_manager

class GameEngine:
    '''
    The main game engine. The main loop of the game is in GameEngine.run()
    '''

    def __init__(self):
        '''
        This function is called when the GameEngine is created.
        For more specific objects related to a game instance
            , they should be initialized in GameEngine.initialize()
        '''
        self.register_listeners()
        self._state = None
        self.map = load_map('Maps/emptymap')

    @property
    def state(self):
        return self._state

    def initialize(self, event):
        '''
        This method is called when a new game is instantiated.
        '''
        self.clock = pg.time.Clock()
        self._state = Const.STATE_MENU
        self.players = [Player(0), Player(1), Player(2), Player(3)]
        self.ghosts = [Ghost(0, Const.GHOST_INIT_TP_CD)]
        self.patronuses = []

    def handle_every_tick(self, event):
        cur_state = self.state
        if cur_state == Const.STATE_MENU:
            self.update_menu()
        elif cur_state == Const.STATE_PLAY:
            self.update_objects()

            self.timer -= 1

            # checks if a new second has passed and calls each player to update score
            self.second_change = True if (Const.GAME_LENGTH - self.timer) % Const.FPS == 0 else False
            self.minutes_passed = ((Const.GAME_LENGTH - self.timer) // Const.FPS) // 60
            if self.second_change:
                for player in self.players:
                    player.add_score(self.minutes_passed); 

            if self.timer == 0:
                self.ev_manager.post(EventTimesUp())
        elif cur_state == Const.STATE_ENDGAME:
            self.update_endgame()
        self.ghosts[0].move_direction(pg.Vector2(random.random() * 2 - 1, random.random() * 2 - 1))
        self.ghosts[0].teleport(pg.Vector2(random.random() * 200 - 1, random.random() * 200 - 1))

    def handle_state_change(self, event):
        self._state = event.state

    def handle_quit(self, event):
        self.running = False

    def handle_move(self, event):
        self.players[event.player_id].move_direction(event.direction)

    def handle_times_up(self, event):
        get_event_manager().post(EventStateChange(Const.STATE_ENDGAME))

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventStateChange, self.handle_state_change)
        ev_manager.register_listener(EventQuit, self.handle_quit)
        ev_manager.register_listener(EventPlayerMove, self.handle_move)
        ev_manager.register_listener(EventTimesUp, self.handle_times_up)

    def update_menu(self):
        '''
        Update the objects in welcome scene.
        For example: game title, hint text
        '''
        pass

    def update_objects(self):
        '''
        Update the objects not controlled by user.
        For example: obstacles, items, special effects
        '''
        for player in self.players:
            player.tick()
        self.ghosts[0].tick()

    def update_endgame(self):
        '''
        Update the objects in endgame scene.
        For example: scoreboard
        '''
        pass

    def run(self):
        '''
        The main loop of the game is in this function.
        This function activates the GameEngine.
        '''
        self.running = True
        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())
        self.timer = Const.GAME_LENGTH
        while self.running:
            ev_manager.post(EventEveryTick())
            self.clock.tick(Const.FPS)
