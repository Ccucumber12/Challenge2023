import random
import os

import pygame as pg

import api.api_impl as api_impl
import const
from event_manager.event_manager import *
from event_manager.events import (EventEveryTick, EventInitialize, EventPlayerMove, EventQuit,
                                  EventStateChange, EventTimesUp)
from instances_manager import get_event_manager
from model.character import Ghost, Patronus, Player
from model.item import Item, ItemGenerator
from model.map import load_map


class GameEngine:
    """
    The main game engine. The main loop of the game is in GameEngine.run()
    """

    def __init__(self, map_name, ai, show_ai_target, no_error_message):
        """
        This function is called when the GameEngine is created.
        For more specific objects related to a game instance,
        they should be initialized in GameEngine.initialize()
        """
        self.register_listeners()
        self._state = None
        self.map = load_map(os.path.join(const.MAP_DIR, map_name))
        self.timer = 0
        self.ai = ai
        self.show_ai_target = show_ai_target
        self.no_error_message = no_error_message

    @property
    def state(self):
        return self._state

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        self.clock = pg.time.Clock()
        self.user_events: dict[int, list[function]] = {}
        self._state = const.STATE_MENU
        self.players: list[Player] = []
        for i in const.PlayerIds:
            self.players.append(Player(i))
        self.ghosts: list[Ghost] = [
            Ghost(0, const.GHOST_INIT_TP_CD, self.map.get_ghost_spawn_point())]
        self.patronuses: list[Patronus] = []
        self.patronus_counter = 0
        self.items: set[Item] = set()
        self.timer = 0
        self.item_generator = ItemGenerator()
        self.register_user_event(60 * const.FPS, self.create_ghost_handler)

    def handle_every_tick(self, event):
        cur_state = self.state
        ev_manager = get_event_manager()
        if cur_state == const.STATE_MENU:
            self.update_menu()
        elif cur_state == const.STATE_PLAY:
            self.update_objects()

            self.timer += 1

            if self.timer == 1:
                api_impl.init(self.ai)

            # checks if a new second has passed and calls each player to update score
            if self.timer % const.FPS == 0:
                for player in self.players:
                    if not player.dead:
                        player.add_score(const.PLAYER_ADD_SCORE[(self.timer // const.FPS) // 60])

            if self.timer == const.GAME_LENGTH:
                places = self.players.copy()
                places.sort(key=lambda x: x.score, reverse=True)
                ev_manager.post(EventTimesUp(places))

            # Check if a item is eaten
            item_deletions = []
            for item in self.items:
                item.tick()
                if item.eaten or self.timer > item.vanish_time:
                    item_deletions.append(item)
            for item in item_deletions:
                self.items.remove(item)

            # Handle user events
            if self.timer in self.user_events:
                events = self.user_events[self.timer]
                for event in events:
                    event()
                self.user_events.pop(self.timer)

            for i in const.PlayerIds:
                api_impl.call_ai(i)

        elif cur_state == const.STATE_ENDGAME:
            self.update_endgame()

    def register_user_event(self, delay, handler):
        """
        handler will be executed after delay ticks
        """
        if not type(delay) is int:
            raise TypeError("delay should be an integer!")
        if not callable(handler):
            raise TypeError("handler is not callable!")
        time = delay + self.timer
        if time in self.user_events:
            self.user_events[time].append(handler)
        else:
            self.user_events[time] = [handler]

    def handle_state_change(self, event):
        self._state = event.state

    def handle_quit(self, event):
        self.running = False

    def handle_move(self, event: EventPlayerMove):
        player = self.players[event.player_id]
        player.move(event.direction)

    def handle_times_up(self, event):
        get_event_manager().post(EventStateChange(const.STATE_ENDGAME))

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(
            EventStateChange, self.handle_state_change)
        ev_manager.register_listener(EventQuit, self.handle_quit)
        ev_manager.register_listener(EventPlayerMove, self.handle_move)
        ev_manager.register_listener(EventTimesUp, self.handle_times_up)

    def update_menu(self):
        """
        Update the objects in welcome scene.
        For example: game title, hint text
        """
        pass

    def update_objects(self):
        """
        Update the objects not controlled by user.
        For example: obstacles, items, special effects.
        """
        for player in self.players:
            player.tick()

        for ghost in self.ghosts:
            ghost.tick()

        for patronuse in self.patronuses:
            patronuse.tick()
            if patronuse.dead or self.timer > patronuse.death_time:
                patronuse.dead = True
                self.patronuses.remove(patronuse)

        item_deletions = []
        for item in self.items:
            item.tick()
            if item.eaten:
                item_deletions.append(item)
        for item in item_deletions:
            self.items.remove(item)

    def update_endgame(self):
        """
        Update the objects in endgame scene.
        For example: scoreboard
        """
        pass

    def create_ghost(self):
        candidate = pg.Vector2(
            random.randint(const.GHOST_RADIUS, const.ARENA_SIZE[0] - const.GHOST_RADIUS),
            random.randint(const.GHOST_RADIUS, const.ARENA_SIZE[1] - const.GHOST_RADIUS))
        while self.map.get_type(candidate) == const.MAP_OBSTACLE:
            candidate = pg.Vector2(
                random.randint(const.GHOST_RADIUS, const.ARENA_SIZE[0] - const.GHOST_RADIUS),
                random.randint(const.GHOST_RADIUS, const.ARENA_SIZE[1] - const.GHOST_RADIUS))
        new_ghost = Ghost(len(self.ghosts), const.GHOST_INIT_TP_CD, candidate)
        self.ghosts.append(new_ghost)

    def create_ghost_handler(self):
        self.create_ghost()
        self.register_user_event(60 * const.FPS, self.create_ghost_handler)

    def run(self):
        """
        Execute the main loop of the game is in this function.
        This function activates the GameEngine.
        """
        self.running = True
        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())
        self.timer = 0
        while self.running:
            ev_manager.post(EventEveryTick())
            self.clock.tick(const.FPS)
