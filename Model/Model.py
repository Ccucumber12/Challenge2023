import random

import pygame as pg
from math import sqrt

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
        self.ghosts = [Ghost(0, Const.GHOST_INIT_TP_CD)]

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
        self.ev_manager.post(EventInitialize())
        self.timer = Const.GAME_LENGTH
        while self.running:
            self.ev_manager.post(EventEveryTick())
            self.clock.tick(Const.FPS)

class Character:
    '''
    Parent class of Player, Ghost and all movable characters
    '''
    def __init__(self, position, speed):
        self.position = position # is a pg.Vector2
        self.speed = speed

    def move(self, x, y):
        '''
        +x: right, +y: down 
        (x, y) will be automatically transfered to unit vector.
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        '''
        r = (x*x+y*y)**(1/2)

        # Modify position of player
        self.position += self.speed / Const.FPS * pg.Vector2((x/r), (y/r))

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))

class Player(Character):
    def __init__(self, player_id):
        self.player_id = player_id
        position = Const.PLAYER_INIT_POSITION[player_id] # is a pg.Vector2
        speed = Const.SPEED_ATTACK if player_id == 1 else Const.SPEED_DEFENSE
        super().__init__(position, speed)
        self.dead = False
        self.invisible = False
        self.invincible = False
        self.respawn_timer = 0
        self.score = 0

    def tick(self):
        '''
        Run when EventEveryTick() arises.
        '''
        if self.dead:
            self.respawn_timer -= 1
        
        if self.respawn_timer <= 0:
            self.dead = False

    def move_direction(self, direction: str):
        '''
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        '''
        # Modify position of player
        # self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]
        x = 1 if direction == 'right' else -1 if direction == 'left' else 0
        y = 1 if direction == 'down' else -1 if direction == 'up' else 0
        super().move(x, y)

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))
    
    def caught(self):
        '''
        Caught by the ghost.
        Kill player
        '''
        if self.respawn_timer <= 0:
            self.dead = True
            self.respawn_timer = Const.PLAYER_RESPAWN_TIME
    
    def isinvisible(self):
        return self.dead or self.invisible or self.invincible

    def add_score(self, minutes: int):
        #if self.dead:
        #    return
        if minutes == 0:
            self.score += 2; 
        elif minutes == 1:
            self.score += 3; 
        else:
            self.score += 5; 
        #print(self.score)

class Ghost(Character):
    def __init__(self, ghost_id, teleport_cd):
        self.ghost_id = ghost_id
        position = Const.GHOST_INIT_POSITION[ghost_id] # is a pg.Vector2
        speed = Const.GHOST_INIT_SPEED
        super().__init__(position, speed)

        #teleport
        self.teleport_last_time = 0
        self.teleport_cd = teleport_cd
        self.teleport_chanting = False # if it is chantting
        self.teleport_chanting_time = 0 # how long it has to continue chanting before teleport_chanting. NOT teleport cd.
        self.teleport_distination = pg.Vector2(0, 0)

    def tick(self):
        '''
        Run when EventEveryTick() arises.
        '''
        if self.teleport_chanting:
            self.teleport_chanting_time -= 1
            if self.teleport_chanting_time <= 0:
                self.position = self.teleport_distination
                self.teleport_chanting = False

    def move_direction(self, direction):
        '''
        '''
        if self.teleport_chanting:
            return

        x = self.speed / Const.FPS * direction[0] / sqrt(direction[0] ** 2 + direction[1] ** 2)
        y = self.speed / Const.FPS * direction[1] / sqrt(direction[0] ** 2 + direction[1] ** 2)
        super().move(x, y)

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))

    def teleport(self, destination: pg.Vector2):
        '''
        ghost will transport to the destination after a little delay.
        This won't automatically clip the position so you need to worry out-of-bound moving.
        '''
        if self.teleport_chanting:
            return
        # if (time now) - self.teleport_last_time < self.teleport_cd:
        #     return
        self.teleport_chanting = True
        self.teleport_distination = destination
        self.teleport_chanting_time = Const.GHOST_CHATING_TIME
    

