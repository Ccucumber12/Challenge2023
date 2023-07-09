import heapq
import random
from math import ceil

import pygame as pg

import const
import instances_manager
import util
from event_manager.events import (EventGhostKill, EventGhostTeleport, EventGhostTeleportChant,
                                  EventPetrify, EventPlayerGetItem, EventSortinghat, EventPortkey)
from instances_manager import get_event_manager, get_game_engine


class Character:
    """
    Parent class of Player, Ghost and all movable characters
    """

    def __init__(self, position: pg.Vector2, speed: int, radius):
        self.position = position
        self.speed = speed
        self.radius = radius

        # This caches the first x cells in the calculated path
        self.saved_path = []

    def is_invisible(self):
        return False

    def is_invincible(self):
        return False

    # might be discard since there is a built-in pg.Vector2.distance_to()
    def get_distance(self, character):
        """gets euclidean distance between self and character"""
        return (self.position - character.position).length()

    def move(self, direction: pg.Vector2):
        """
        Move the player along the direction by its speed.
        +x: right, +y: down.
        direction will be automatically transfered to unit vector.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """

        # If direction = (0, 0), then no need to move
        if direction == pg.Vector2(0, 0):
            return

        # Normalize direction in place if direction is longer than the max distance character can move
        if direction.length() > self.speed:
            direction = self.speed * direction.normalize()

        # If it hits an obstacle, try a smaller distance
        for attempt in range(3):
            # Calculate new position
            new_position = self.position + direction

            # clamp
            new_position.x = util.clamp(new_position.x, 0, const.ARENA_SIZE[0] - 1)
            new_position.y = util.clamp(new_position.y, 0, const.ARENA_SIZE[1] - 1)

            model = get_game_engine()
            if model.map.get_type(new_position) == const.MAP_OBSTACLE:
                direction /= 2
                continue

            # Update
            self.position = new_position
            return

    def pathfind(self, x, y) -> pg.Vector2:
        """
        Pathfinding algorithm implementation.
        Take x and y as the destination, 
        then return the first (x, y) that the character should go to.
        """
        def reconstruct_path(parent, current):
            path = []
            while current is not None:
                path.append(current)
                current = parent[current[0]][current[1]]
            return path[::-1]

        def a_star(grid, start, target):
            rows = len(grid)
            cols = len(grid[0])

            def heuristic(cell, target):
                return abs(cell[0] - target[0]) + abs(cell[1] - target[1])

            def get_neighbors(cell):
                neighbors = []
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                              (1, 1), (-1, -1), (1, -1), (-1, 1)]  # Right, Left, Down, Up
                for dx, dy in directions:
                    new_row = cell[0] + dx
                    new_col = cell[1] + dy
                    if (0 <= new_row < rows and 0 <= new_col < cols
                            and grid[new_row][new_col] != const.MAP_OBSTACLE
                            and grid[cell[0]][new_col] != const.MAP_OBSTACLE
                            and grid[new_row][cell[1]] != const.MAP_OBSTACLE):
                        neighbors.append((new_row, new_col))
                return neighbors

            parent = [[None] * cols for _ in range(rows)]
            closed = [[False] * cols for _ in range(rows)]
            dis = [[10000] * cols for _ in range(rows)]
            dis[start[0]][start[1]] = 0

            start_h = heuristic(start, target)
            open_list = [(start_h, 0, start)]  # (f, g, cell)

            while open_list:
                _, g, current = heapq.heappop(open_list)
                # print(current, g)
                if g != dis[current[0]][current[1]]:
                    continue
                if current == target:
                    return reconstruct_path(parent, current)
                closed[current[0]][current[1]] = True

                for neighbor in get_neighbors(current):
                    if closed[neighbor[0]][neighbor[1]]:
                        continue
                    tentative_g = g + 1
                    if (parent[neighbor[0]][neighbor[1]] is None
                            or tentative_g < dis[neighbor[0]][neighbor[1]]):
                        parent[neighbor[0]][neighbor[1]] = (
                            current[0], current[1], tentative_g)
                        dis[neighbor[0]][neighbor[1]] = tentative_g
                        neighbor_h = heuristic(neighbor, target)
                        heapq.heappush(open_list, 
                                       (tentative_g + neighbor_h, tentative_g, neighbor))
            return []


        Map = get_game_engine().map
        grid = Map.map
        start = Map.convert_coordinate(self.position)

        # Checks saved path
        while len(self.saved_path) > 0 and start == self.saved_path[0]:
            self.saved_path.pop(0)
        # Checks if the character is too far from path (by maybe teleport or something)
        if len(self.saved_path) > 0 and abs(start[0] - self.saved_path[0][0]) + abs(start[1] - self.saved_path[0][1]) > 2:
            self.saved_path = []

        end = Map.convert_coordinate([x, y])
        if grid[end[0]][end[1]] == const.MAP_OBSTACLE or \
                not Map.in_same_connected_component(self.position, (x, y)):
            return x, y

        if len(self.saved_path) == 0:
            path = a_star(grid, start, end)
            self.saved_path = [(path[i][0], path[i][1])
                               for i in range(1, min(len(path), const.CACHE_CELLS+1))]
        if len(self.saved_path) == 0:
            return pg.Vector2(x, y)
        r = (x - self.position[0]) ** 2 + (y - self.position[1]) ** 2

        if r == 0:
            self.saved_path = []
            return x, y

        dx = (x - self.position[0]) / r
        dy = (y - self.position[1]) / r

        return pg.Vector2(Map.convert_cell(
            (self.saved_path[0][0] + 0.5 * (1 + dx), self.saved_path[0][1] + 0.5 * (1 + dy))))


class Player(Character):
    def __init__(self, player_id: int):
        model = get_game_engine()
        position = pg.Vector2(model.map.get_spawn_point(player_id.value))
        super().__init__(position, const.PLAYER_SPEED, const.PLAYER_RADIUS)

        self.player_id = player_id
        self.dead = False
        self.respawn_time = 0
        self.score = 0
        self.effect_timer = 0
        self.effect: const.EffectType | None = None
        self.golden_snitch = False
        self.unfreeze_timer = 0

        ev_manager = get_event_manager()
        ev_manager.register_listener(EventPetrify, self.handle_petrify)

    @property
    def base_speed(self):
        speed = const.PLAYER_SPEED
        if self.golden_snitch:
            speed *= 1.5
        return speed

    def is_invisible(self):
        return self.effect == const.EffectType.CLOAK

    def is_invincible(self):
        return self.effect == const.EffectType.REMOVED_SORTINGHAT

    def handle_petrify(self, event: EventPetrify):
        event.victim.set_effect(const.EffectType.PETRIFICATION)

    def freeze(self):
        self.unfreeze_timer = const.GHOST_KILL_ANIMATION_TIME

    def iscaught(self):
        model = get_game_engine()
        """Return if the player is caught by one of the ghosts"""
        if self.dead or self.is_invincible():
            # If the player has sortinghat and is invincible, the effect of sortinghat won't triggered.
            # Even if the player is invisible, the ghost can still catch him.
            return False
        for ghost in model.ghosts:
            if ghost.teleport_chanting:
                continue
            if self.get_distance(ghost) < (const.PLAYER_RADIUS + const.GHOST_RADIUS):
                return ghost # Not a good method but it's the easiest I can think of now
        return False

    def caught(self, catcher):
        """
        Caught by the ghost.
        Kill player
        """
        print(f"{self.player_id} was caught!")
        model = get_game_engine()
        if self.effect == const.EffectType.SORTINGHAT:
            catcher.freeze(self.position)
            self.freeze()
            get_event_manager().post(EventGhostKill(catcher.ghost_id, self.position, self.player_id, self.effect))
            self.remove_effect()
            others = [x for x in const.PlayerIds
                      if x != self.player_id and not model.players[x.value].dead]
            if len(others) > 0:
                victim = random.choice(others)
                get_event_manager().post(EventSortinghat(self.player_id, victim))
                start_second = ceil(model.timer / const.FPS)
                for second in range(start_second, start_second + 5):
                    minute = second // 60
                    model.players[victim.value].score -= const.PLAYER_ADD_SCORE[minute]
            self.set_effect(const.EffectType.REMOVED_SORTINGHAT)
            return
        elif not self.dead:
            catcher.freeze(self.position)
            self.freeze()
            get_event_manager().post(EventGhostKill(catcher.ghost_id, self.position, self.effect))
            self.dead = True
            self.remove_effect()
            self.respawn_time = model.timer + const.PLAYER_RESPAWN_TIME
            model.register_user_event(const.PLAYER_RESPAWN_TIME, self.respawn_handler)

    def respawn_handler(self):
        print(f"{self.player_id} respawned!")
        self.dead = False

    def move(self, direction: pg.Vector2):
        if self.effect == const.EffectType.PETRIFICATION or self.unfreeze_timer > 0:
            return
        super().move(direction)

        model = get_game_engine()
        portal = model.map.get_portal(self.position)
        if portal is not None:
            self.position = model.map.convert_cell(portal)
            get_event_manager().post(EventPortkey(self.position))
            print(f"Player {self.player_id} used a portal!")

    def add_score(self, points: int):
        self.score += points

    def remove_effect(self):
        self.effect_timer = 0
        self.effect = None

    def set_golden_snitch_effect(self):
        self.add_score(150)
        self.golden_snitch = True


    def set_effect(self, effect: const.EffectType):
        get_event_manager().post(EventPlayerGetItem(self.player_id, effect))
        self.effect = effect
        self.effect_timer = const.ITEM_DURATION[effect]
        if self.effect == const.EffectType.PATRONUS:
            model = get_game_engine()
            model.patronuses.append(Patronus(model.patronus_counter, self.position, self))
            model.patronus_counter += 1
            for ghost in model.ghosts:
                while ghost.prey == self:
                    ghost.choose_prey(1)

    def tick(self):
        """
        Run when EventEveryTick() arises.
        """
        model = get_game_engine()
        if self.unfreeze_timer > 0:
            self.unfreeze_timer -= 1
        if model.map.get_type(self.position) == const.MAP_PUDDLE:
            self.speed = 0.7 * self.base_speed
        else:
            self.speed = self.base_speed
        if self.effect_timer > 0:
            self.effect_timer -= 1
        else:
            self.remove_effect()
        catcher = self.iscaught()
        if catcher:
            self.caught(catcher)


class Patronus(Character):
    def __init__(self, patronus_id: int, position: pg.Vector2, owner: Player):
        self.patronus_id = patronus_id
        super().__init__(position, const.PATRONUS_SPEED, const.PATRONUS_RADIUS)

        self.owner = owner
        self.chasing = self.choose_target()

        self.score = 500
        self.dead = False
        self.death_time = get_game_engine().timer + const.ITEM_DURATION[const.EffectType.PATRONUS]
        print(
            f"Patronus {self.patronus_id} which belongs to {owner.player_id} was gernerated at {position}!")

    def choose_target(self) -> Player | None:
        """Return a player that is not dead and is not the one who call the patronus"""
        players = get_game_engine().players
        candidates = [ply for ply in players if ply != self.owner and not ply.dead]
        if not len(candidates) == 0:
            return random.choice(candidates)
        else:
            return None

    def chase(self):
        """Patronus will move toward its taget player."""
        # Uses Pathfind
        self.move(self.pathfind(*self.chasing.position) - self.position)

    def iscaught(self) -> bool:
        """Return if the patronus is caught by one of the ghosts"""
        model = get_game_engine()
        for ghost in model.ghosts:
            if self.get_distance(ghost) < (const.PATRONUS_RADIUS + const.GHOST_RADIUS):
                get_event_manager().post(EventGhostKill(ghost.ghost_id, self.position))
                ghost.freeze(self.position)
                return True
        return False

    def tick(self):
        # Look for the direction of the player it is chasing
        if self.chasing == None or self.chasing.dead or self.chasing.effect == const.EffectType.CLOAK:
            self.chasing = self.choose_target()
        if self.chasing != None:
            self.chase()
        if self.iscaught():
            print(f"Patronus {self.patronus_id} was caught!")
            self.dead = True


class Ghost(Character):
    def __init__(self, ghost_id, teleport_cd: int, position: pg.Vector2):
        self.ghost_id = ghost_id

        speed = const.GHOST_INIT_SPEED
        super().__init__(position, speed, const.GHOST_RADIUS)

        # State as defined by Const.GHOST_STATE
        self.state = const.GhostState.CHASE

        # teleport
        self.teleport_available = True
        self.teleport_cd = teleport_cd
        self.teleport_chanting = False  # if it is chantting
        self.teleport_distination = pg.Vector2(0, 0)
        self.prey = None
        self.__teleport_time = 0
        self.__teleport_last = -self.teleport_cd

        # Wander and chase config
        self.wander_time = const.GHOST_WANDER_TIME
        self.wander_pos: pg.Vector2 = util.get_random_pos(const.GHOST_RADIUS)
        self.chase_time = const.GHOST_CHASE_TIME
        self.unfreeze_timer = 0

    @property
    def teleport_after(self):
        model = instances_manager.get_game_engine()
        return self.__teleport_time - model.timer

    @property
    def teleport_cooldown_remain(self):
        model = instances_manager.get_game_engine()
        return max(0, self.teleport_cd - (model.timer - self.__teleport_last))

    def move(self, direction: pg.Vector2):
        """Move the ghost along direction."""
        if self.teleport_chanting:
            return

        super().move(direction)

    def teleport(self, destination: pg.Vector2):
        """
        ghost will transport to the destination after a little delay.
        This won't automatically clip the position so you need to worry out-of-bound moving.
        """
        if self.teleport_chanting:
            return
        if not self.teleport_available:
            return
        self.teleport_chanting = True
        self.teleport_available = False
        self.teleport_distination = destination
        model = get_game_engine()
        self.__teleport_last = model.timer
        self.__teleport_time = model.timer + const.GHOST_CHANTING_TIME
        model.register_user_event(const.GHOST_CHANTING_TIME, self.teleport_handler)
        model.register_user_event(self.teleport_cd, self.teleport_cd_handler)
        get_event_manager().post(EventGhostTeleportChant(self.ghost_id, self.position, self.teleport_distination))

    def teleport_handler(self):
        self.teleport_chanting = False
        self.position = self.teleport_distination
        get_event_manager().post(EventGhostTeleport(self.ghost_id, self.position, self.teleport_distination))

    def teleport_cd_handler(self):
        self.teleport_available = True

    def chase_handler(self):
        model = get_game_engine()
        self.state = const.GhostState.CHASE
        self.chase_time = const.GHOST_CHASE_TIME
        model.register_user_event(const.GHOST_CHASE_TIME, self.wander_handler)
        # Temporary: the speed of ghost will increase by 0.2 coordinate/tick for each wandering period
        self.speed = min(const.GHOST_MAX_SPEED, self.speed + 0.2)
        print(f"Ghost speed updated to {self.speed}")

    def chase(self):
        """
        Ghost will move toward its prey.
        """
        if self.prey is None:
            self.wander()
            return

        # Uses Pathfind
        self.move(self.pathfind(*self.prey.position) - self.position)

    def freeze(self, after_freeze_position: pg.Vector2):
        self.unfreeze_timer = const.GHOST_KILL_ANIMATION_TIME
        self.after_freeze_position = after_freeze_position

    def wander_handler(self):
        model = get_game_engine()
        self.state = const.GhostState.WANDER
        self.wander_pos = model.map.get_random_pos(const.GHOST_RADIUS)
        model.register_user_event(int(self.wander_time), self.chase_handler)
        self.wander_time = max(0.5 * const.FPS, self.wander_time - 0.5 * const.FPS)

    def wander(self):
        model = get_game_engine()
        if self.position.distance_to(self.wander_pos) < const.GHOST_RADIUS:
            self.wander_pos = model.map.get_random_pos(const.GHOST_RADIUS)
        self.move(self.pathfind(*self.wander_pos) - self.position)

    def choose_prey(self, randomness):
        #randomness: a real number which denotes how much randomness affects the result
        model = get_game_engine()
        prey_candidates = (
            [x for x in model.players if not x.dead and not x.is_invisible() and not x.is_invincible()]
            + model.patronuses)
        self.prey = min(
            prey_candidates,
            key=lambda x: self.get_distance(x) - x.score + randomness * random.uniform(0, 100),
            default=None)
    
    def choose_random_pos(self, randomness):
        #count: The number of candidates
        model = get_game_engine()
        positions = [model.map.get_random_pos(const.GHOST_RADIUS) for _ in range(5)]
        ghosts = model.ghosts
        
        ret = min(positions,
            key=lambda x: -sum([(g.position - x).length() for g in ghosts]) + randomness * random.uniform(0, 100),
            default=None)
        return ret

    def tick(self):
        """
        AI of ghost.
        Determine what ghost should do next.
        Runs every tick.
        """
        if self.unfreeze_timer > 0:
            self.unfreeze_timer -= 1
            if self.unfreeze_timer == 0:
                self.position = self.after_freeze_position
            return
        model = get_game_engine()
        if model.timer == 1:
            self.chase_handler()

        if self.teleport_chanting:
            return
        if self.teleport_available:
            if self.state == const.GhostState.WANDER:
                self.wander_pos = self.choose_random_pos(0.5)
                self.teleport(self.wander_pos)
            else:
                self.choose_prey(10)
                if self.prey is None:
                    self.teleport(self.choose_random_pos(0.5))
                    return
                self.teleport(self.prey.position)
            return

        if self.state == const.GhostState.WANDER:
            self.wander()
        elif self.state == const.GhostState.CHASE:
            if (self.prey is None or self.prey.dead or self.prey.is_invisible()
                   or self.prey.is_invincible()):
                self.choose_prey(1)
                if self.prey is None:
                    self.wander()
                    return
            self.chase()
