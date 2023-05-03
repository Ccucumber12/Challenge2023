import random

import pygame as pg

from EventManager.EventManager import *
import Const


class GameEngine:
    '''
    The main game engine. The main loop of the game is in GameEngine.run()
    '''

    def __init__(self, ev_manager: EventManager):
        '''
        This function is called when the GameEngine is created.
        For more specific objects related to a game instance
            , they should be initialized in GameEngine.initialize()
        '''
        self.ev_manager = ev_manager
        self.register_listeners()
        self._state = None

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

    def handle_every_tick(self, event):
        cur_state = self.state
        if cur_state == Const.STATE_MENU:
            self.update_menu()
        elif cur_state == Const.STATE_PLAY:
            self.update_objects()

            self.timer -= 1
            if self.timer == 0:
                self.ev_manager.post(EventTimesUp())
        elif cur_state == Const.STATE_ENDGAME:
            self.update_endgame()

    def handle_state_change(self, event):
        self._state = event.state

    def handle_quit(self, event):
        self.running = False

    def handle_move(self, event):
        self.players[event.player_id].move_direction(event.direction)

    def handle_times_up(self, event):
        self.ev_manager.post(EventStateChange(Const.STATE_ENDGAME))

    def register_listeners(self):
        self.ev_manager.register_listener(EventInitialize, self.initialize)
        self.ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        self.ev_manager.register_listener(EventStateChange, self.handle_state_change)
        self.ev_manager.register_listener(EventQuit, self.handle_quit)
        self.ev_manager.register_listener(EventPlayerMove, self.handle_move)
        self.ev_manager.register_listener(EventTimesUp, self.handle_times_up)

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
        pass

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
        self.ev_manager.post(EventInitialize())
        self.timer = Const.GAME_LENGTH
        while self.running:
            self.ev_manager.post(EventEveryTick())
            self.clock.tick(Const.FPS)


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.position = Const.PLAYER_INIT_POSITION[player_id] # is a pg.Vector2
        self.speed = Const.SPEED_ATTACK if player_id == 1 else Const.SPEED_DEFENSE

    def move_direction(self, direction: str):
        '''
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        '''
        # Modify position of player
        self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))
