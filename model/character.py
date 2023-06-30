import heapq
import random
from math import ceil, sqrt

import pygame as pg

import const
from instances_manager import get_game_engine, get_event_manager
from event_manager.events import *


class Character:
    """
    Parent class of Player, Ghost and all movable characters
    """

    def __init__(self, position: pg.Vector2, speed: int):
        self.position = position
        self.speed = speed

        #This caches the first x cells in the calculated path
        self.saved_path = []

    # might be discard since there is a built-in pg.Vector2.distance_to()
    def get_distance(self, character):
        """gets euclidean distance between self and character"""
        return (self.position - character.position).length()

    def move(self, x, y):
        """
        +x: right, +y: down.
        (x, y) will be automatically transfered to unit vector.
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """

        # If it hits an obstacle, try a smaller distance
        r = (x * x + y * y) ** (1 / 2)
        for attempt in range(3):
            # Calculate new position
            new_position = self.position + self.speed / const.FPS * pg.Vector2((x / r), (y / r))

            # clamp
            new_position.x = max(0, min(const.ARENA_SIZE[0], new_position.x))
            new_position.y = max(0, min(const.ARENA_SIZE[1], new_position.y))

            model = get_game_engine()
            if model.map.get_type(new_position) == const.MAP_OBSTACLE:
                x, y = x/2, y/2
                continue
            # Todo: Portal
            portal = model.map.get_portal(new_position)
            if portal is not None:
                print('Portal', portal)
            # Update
            self.position = new_position
            return

    def pathfind(self, x, y):
        """Pathfinding algorithm implementation"""
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
                        heapq.heappush(open_list, (tentative_g +
                                                   neighbor_h, tentative_g, neighbor))
            return []

        Map = get_game_engine().map
        grid = Map.map
        start = Map.convert_coordinate(self.position)
        
        ##Checks saved path
        while len(self.saved_path) > 0 and start == self.saved_path[0]:
            self.saved_path.pop(0);
        ##Checks if the character is too far from path (by maybe teleport or something)
        if len(self.saved_path) > 0 and abs(start[0] - self.saved_path[0][0]) + abs(start[1] - self.saved_path[0][1]) > 2:
            self.saved_path = []

        end = Map.convert_coordinate([x, y])
        
        if len(self.saved_path) == 0:
            path = a_star(grid, start, end)
            self.saved_path = [(path[i][0], path[i][1]) for i in range(1, min(len(path), const.CACHE_CELLS+1))]
        if len(self.saved_path) == 0:
            return x, y
        r = (x - self.position[0]) ** 2 + (y - self.position[1]) ** 2
        dx = (x - self.position[0]) / r
        dy = (y - self.position[1]) / r

        return Map.convert_cell((self.saved_path[0][0], self.saved_path[0][1]), dx, dy)

    def get_random_position(self, obj):
        """Finds a random position that does not collide with obstacles"""
        Map = get_game_engine().map
        while obj == None or Map.get_type(obj) == const.MAP_OBSTACLE:
            obj = pg.Vector2(random.randint(0, const.ARENA_SIZE[0]),
                             random.randint(0, const.ARENA_SIZE[1]))
        return obj


class Player(Character):
    def __init__(self, player_id: int):
        self.player_id = player_id
        model = get_game_engine()

        position = pg.Vector2(model.map.get_spawn_point(player_id.value))

        # temporary: gets random positioin for spawn point
        position = self.get_random_position(position)

        speed = const.PLAYER_SPEED
        super().__init__(position, speed)
        self.dead = False
        self.invisible = False
        self.invincible = 0  # will be invicible until timer > invincible.
        self.respawn_timer = 0
        self.score = 0
        self.effect_timer = 0
        self.effect = None

    def tick(self):
        """
        Run when EventEveryTick() arises.
        """
        if self.effect_timer > 0:
            self.effect_timer -= 1
        else:
            self.remove_effect()
        if self.iscaught():
            self.caught()

    def iscaught(self):
        model = get_game_engine()
        """Return if the player is caught by one of the ghosts"""
        if self.dead or self.invincible >= model.timer:
            # If the player has sortinghat and is invincible, the effect of sortinghat won't triggered.
            # Even if the player is invisible, the ghost can still catch him.
            return False
        for ghost in model.ghosts:
            if self.get_distance(ghost) < (const.PLAYER_RADIUS + const.GHOST_RADIUS):
                return True
        return False

    def caught(self):
        """
        Caught by the ghost.
        Kill player
        """
        print(f"{self.player_id} was caught!")
        model = get_game_engine()
        if self.effect == const.ITEM_SET.SORTINGHAT:
            self.remove_effect()
            others = [x for x in const.PLAYER_IDS if x != self.player_id]
            victim = random.choice(others)
            model.sortinghat_animations.append((self.position, victim, 0))
            second = ceil(model.timer / const.FPS)
            for _ in range(5):
                minute = second // 60
                model.players[victim.value].score -= const.PLAYER_ADD_SCORE[minute]
            self.invincible = model.timer + const.SORTINGHAT_INVINCIBLE_TIME
            return
        elif not self.dead:
            self.dead = True
            self.remove_effect()
            model.register_user_event(const.PLAYER_RESPAWN_TIME, self.respawn_handler)

    def respawn_handler(self):
        print(f"{self.player_id} respawned!")
        self.dead = False

    def move_direction(self, direction: str):
        """
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """
        # Modify position of player
        # self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]
        if self.effect == const.ITEM_SET.PETRIFICATION:
            return
        x = 1 if direction == 'right' else -1 if direction == 'left' else 0
        y = 1 if direction == 'down' else -1 if direction == 'up' else 0
        self.move(x, y)

        self.position

        # clipping
        self.position.x = max(0, min(const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(const.ARENA_SIZE[1], self.position.y))

    def add_score(self, points: int):
        self.score += points

    def remove_effect(self):
        self.effect_timer = 0
        if self.effect == const.ITEM_SET.CLOAK:
            self.invisible = False
        elif self.effect == const.ITEM_SET.PATRONUS:
            pass
        self.effect = None

    def get_effect(self, effect: const.ITEM_SET, effect_status: const.ITEM_STATUS):
        self.effect = effect
        self.effect_timer = const.ITEM_DURATION[effect][effect_status]
        if self.effect == const.ITEM_SET.GOLDEN_SNITCH:
            self.add_score(150)
            self.speed *= 1.5
        elif self.effect == const.ITEM_SET.CLOAK:
            self.invisible = True
        elif self.effect == const.ITEM_SET.PATRONUS:
            model = get_game_engine()
            print(type(list(const.PLAYER_IDS)[0]))
            model.patronuses.append(
                Patronus(0, self.position, 
                         random.choice([x for x in const.PLAYER_IDS if x != self.player_id])))
            # The parameters passed is not properly assigned yet
        elif self.effect == const.ITEM_SET.PETRIFICATION:
            # One can't move when it's effect is pertification.
            # It will be implemented in function move_direction.
            pass


class Patronus(Character):
    def __init__(self, patronus_id: int, position: pg.Vector2, chase_player: Player):
        self.patronus_id = patronus_id
        speed = const.PATRONUS_SPEED
        super().__init__(position, speed)
        self.chase_player = chase_player  # The player which the patronous choose to chase
        print(f"A patronus chasing {chase_player} has gernerated at {position}!")

    def tick(self):
        # Look for the direction of the player it is chasing
        x = 1 if self.position.x < self.chase_player.position.x else -1 \
            if self.position.x > self.chase_player.position.x else 0
        y = 1 if self.position.y < self.chase_player.position.y else -1 \
            if self.position.y > self.chase_player.position.y else 0
        self.move(x, y)


class Ghost(Character):
    def __init__(self, ghost_id, teleport_cd):

        self.ghost_id = ghost_id
        position = const.GHOST_INIT_POSITION[ghost_id]  # is a pg.Vector2

        # temp
        position = self.get_random_position(position)

        speed = const.GHOST_INIT_SPEED
        super().__init__(position, speed)

        # State as defined by Const.GHOST_STATE
        self.state = const.GHOST_STATE.CHASE

        # teleport
        self.teleport_available = True
        self.teleport_cd = teleport_cd
        self.teleport_chanting = False  # if it is chantting
        self.teleport_distination = pg.Vector2(0, 0)
        self.prey = None

        # Wander and chase config
        self.wander_time = const.GHOST_WANDER_TIME
        self.wander_pos = None
        self.chase_time = const.GHOST_CHASE_TIME

    def move_direction(self, direction):
        if self.teleport_chanting:
            return

        if direction[0] != 0 or direction[1] != 0:
            # Avoid division by zero
            x = self.speed / const.FPS * direction[0] / sqrt(direction[0] ** 2 + direction[1] ** 2)
            y = self.speed / const.FPS * direction[1] / sqrt(direction[0] ** 2 + direction[1] ** 2)
            self.move(x, y)

        # clipping
        self.position.x = max(0, min(const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(const.ARENA_SIZE[1], self.position.y))

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
        model.register_user_event(const.GHOST_CHANTING_TIME, self.teleport_handler)
        model.register_user_event(self.teleport_cd, self.teleport_cd_handler)
        get_event_manager().post(EventGhostTeleport(self.ghost_id, self.position, self.teleport_distination))

    def teleport_handler(self):
        self.teleport_chanting = False
        self.position = self.teleport_distination

    def teleport_cd_handler(self):
        self.teleport_available = True

    def chase_handler(self):
        model = get_game_engine()
        self.state = const.GHOST_STATE.CHASE
        self.chase_time = const.GHOST_CHASE_TIME
        model.register_user_event(const.GHOST_CHASE_TIME, self.wander_handler)
        self.speed = min(const.GHOST_MAX_SPEED, self.speed + self.chase_time / const.FPS)
        print(f"Ghost speed updated to {self.speed}")
        self.chase_time += 2 * const.FPS

    def chase(self):
        """
        Ghost will move toward its prey.
        """
        if self.prey is None:
            return

        # Uses Pathfind
        self.move_direction(pg.Vector2( \
            super().pathfind(self.prey.position.x, self.prey.position.y))-self.position)

        # Goes straight to the position
        # self.move_direction([self.prey.position.x, self.prey.position.y]-self.position)

    def wander_handler(self):
        model = get_game_engine()
        self.state = const.GHOST_STATE.WANDER
        self.wander_pos = None
        model.register_user_event(int(self.wander_time), self.chase_handler)
        self.wander_time = max(0.5 * const.FPS, self.wander_time - 0.5 * const.FPS)

    def wander(self):
        if self.wander_pos == None:
            self.wander_pos = self.get_random_position(self.wander_pos)
        self.move_direction(pg.Vector2(self.pathfind(
            self.wander_pos.x, self.wander_pos.y))-self.position)

    def tick(self):
        """
        AI of ghost.
        Determine what ghost should do next.
        Runs every tick.
        """
        model = get_game_engine()
        if model.timer == 1:
            self.chase_handler()

        if self.state == const.GHOST_STATE.WANDER:
            self.wander()
        elif self.state == const.GHOST_STATE.CHASE:
            if self.teleport_chanting:
                return
            while (self.prey is None) or (self.prey.dead == True) or (self.prey.invisible):
                # Choose prey by closest person alive
                self.prey = min(
                    (player for player in model.players if not player.dead and not player.invisible),
                    key=lambda player: self.get_distance(player) - player.score + random.random(), default=None
                )
                if self.prey is None:
                    break
            if self.teleport_available and self.prey is not None \
                    and self.get_distance(self.prey) > self.speed * const.GHOST_CHANTING_TIME / const.FPS:
                print(f"Teleporting to {self.prey.position}")
                self.teleport(self.prey.position)
                return
            self.chase()
