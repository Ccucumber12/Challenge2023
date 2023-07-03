import pygame as pg

import const
from event_manager.event_manager import *
from event_manager.events import (EventEveryTick, EventInitialize,
                                  EventPlayerMove, EventQuit, EventStateChange,
                                  EventTimesUp)
from instances_manager import get_event_manager
from model.character import Ghost, Patronus, Player
from model.item import Item, ItemGenerator
from model.map import load_map
import api.api_impl as api_impl


class GameEngine:
    """
    The main game engine. The main loop of the game is in GameEngine.run()
    """

    def __init__(self, map_name, ai):
        """
        This function is called when the GameEngine is created.
        For more specific objects related to a game instance,
        they should be initialized in GameEngine.initialize()
        """
        self.register_listeners()
        self._state = None
        self.map = load_map(map_name)
        self.timer = 0
        self.ai = ai
        print(ai)

    @property
    def state(self):
        return self._state

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        self.clock = pg.time.Clock()
        self._state = const.STATE_MENU
        self.players: list[Player] = []
        for i in const.PLAYER_IDS:
            self.players.append(Player(i))
        self.ghosts: list[Ghost] = []
        for i in const.GHOST_IDS:
            self.ghosts.append(Ghost(i, const.GHOST_INIT_TP_CD))
        self.patronuses: list[Patronus] = []
        self.items: set[Item] = set()
        self.timer = 0
        self.user_events: dict[int, list[function]] = {}
        self.item_generator = ItemGenerator()

        api_impl.init(self.ai)

    def handle_every_tick(self, event):
        cur_state = self.state
        ev_manager = get_event_manager()
        if cur_state == const.STATE_MENU:
            self.update_menu()
        elif cur_state == const.STATE_PLAY:
            self.update_objects()

            self.timer += 1

            # checks if a new second has passed and calls each player to update score
            if self.timer % const.FPS == 0:
                for player in self.players:
                    if not player.dead:
                        player.add_score(const.PLAYER_ADD_SCORE[(self.timer // const.FPS) // 60])

            if self.timer == const.GAME_LENGTH:
                ev_manager.post(EventTimesUp())

            # Check if a item is eaten
            item_deletions = []
            for item in self.items:
                item.tick()
                if item.eaten:
                    item_deletions.append(item)
            for item in item_deletions:
                self.items.remove(item)
                del item

            # Handle user events
            if self.timer in self.user_events:
                events = self.user_events[self.timer]
                for event in events:
                    event()
                del self.user_events[self.timer]

            for i in range(0, 4):
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
        self.players[event.player_id].move_direction(event.direction)

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
        self.ghosts[0].tick()
        for patronuse in self.patronuses:
            patronuse.tick()
            if patronuse.dead:
                self.patronuses.remove(patronuse)
                del patronuse

    def update_endgame(self):
        """
        Update the objects in endgame scene.
        For example: scoreboard
        """
        pass

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
