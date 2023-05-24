import random
from math import sqrt

import pygame as pg

import Const

from InstancesManager import get_game_engine


class Character:
    """
    Parent class of Player, Ghost and all movable characters
    """

    def __init__(self, position, speed):
        self.position = position  # is a pg.Vector2
        self.speed = speed

    def move(self, x, y):
        """
        +x: right, +y: down
        (x, y) will be automatically transfered to unit vector.
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """
        r = (x * x + y * y) ** (1 / 2)

        # Calculate new position
        new_position = self.position + self.speed / Const.FPS * pg.Vector2((x / r), (y / r))

        # clamp
        new_position.x = max(0, min(Const.ARENA_SIZE[0], new_position.x))
        new_position.y = max(0, min(Const.ARENA_SIZE[1], new_position.y))

        # Todo: Obstacle checking
        model = get_game_engine()
        if model.map.get_type(new_position) == Const.MAP_OBSTACLE:
            return

        # Todo: Portal
        portal = model.map.get_portal(new_position)
        if portal is not None:
            print('Portal', portal)

        # Update
        self.position = new_position


class Player(Character):
    def __init__(self, player_id):
        self.player_id = player_id
        position = Const.PLAYER_INIT_POSITION[player_id]  # is a pg.Vector2
        speed = Const.SPEED_ATTACK if player_id == 1 else Const.SPEED_DEFENSE
        super().__init__(position, speed)
        self.dead = False
        self.invisible = False
        self.invincible = False
        self.respawn_timer = 0
        self.score = 0
        self.effect_timer = 0
        self.effect = "none"

    def tick(self):
        """
        Run when EventEveryTick() arises.
        """
        if self.effect_timer > 0:
            self.effect_timer -= 1
        else:
            self.remove_effect()

        if self.dead:
            self.respawn_timer -= 1

        if self.respawn_timer <= 0:
            self.dead = False

    def move_direction(self, direction: str):
        """
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """
        # Modify position of player
        # self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]
        x = 1 if direction == 'right' else -1 if direction == 'left' else 0
        y = 1 if direction == 'down' else -1 if direction == 'up' else 0
        super().move(x, y)

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))

    def caught(self):
        """
        Caught by the ghost.
        Kill player
        """
        if self.respawn_timer <= 0:
            self.dead = True
            self.respawn_timer = Const.PLAYER_RESPAWN_TIME

    def isinvisible(self):
        return self.dead or self.invisible or self.invincible

    def add_score(self, minutes: int):
        # if self.dead:
        #    return
        if minutes == 0:
            self.score += 2
        elif minutes == 1:
            self.score += 3
        else:
            self.score += 5
        # print(self.score)

    def remove_effect(self):
        self.effect_timer = 0
        if self.effect == "cloak":
            self.invisible = False
        elif self.effect == "patronus":
            pass

    def get_effect(self, effect: str, effect_status: str):
        self.effect = effect
        self.effect_timer = Const.ITEM_DURATION[effect][effect_status]
        if self.effect == "cloak":
            self.invisible = True
        elif self.effect == "patronus":
            model = get_game_engine()
            model.patronuses.append(Patronus(0, self.position, random.randint(0, 3)))
            # The parameters passed is not properly assigned yet


class Patronus(Character):
    def __init__(self, patronus_id, position, chase_player):
        self.patronus_id = patronus_id
        speed = Const.SPEED_ATTACK
        super().__init__(position, speed)
        self.chase_player = chase_player  # The player which the patronous choose to chase

    def tick(self):
        # Look for the direction of the player it is chasing
        x = 1 if self.position.x < self.chase_player.position.x else -1 if self.position.x > self.chase_player.position.x else 0
        y = 1 if self.position.y < self.chase_player.position.y else -1 if self.position.y > self.chase_player.position.y else 0
        super().move(x, y)


class Ghost(Character):
    def __init__(self, ghost_id, teleport_cd):
        self.ghost_id = ghost_id
        position = Const.GHOST_INIT_POSITION[ghost_id]  # is a pg.Vector2
        speed = Const.GHOST_INIT_SPEED
        super().__init__(position, speed)

        # teleport
        self.teleport_last_time = 0
        self.teleport_cd = teleport_cd
        self.teleport_chanting = False  # if it is chantting
        self.teleport_chanting_time = 0
        # how long it has to continue chanting before teleport_chanting. NOT teleport cd.
        self.teleport_distination = pg.Vector2(0, 0)

    def tick(self):
        """
        Run when EventEveryTick() arises.
        """
        if self.teleport_chanting:
            self.teleport_chanting_time -= 1
            if self.teleport_chanting_time <= 0:
                self.position = self.teleport_distination
                self.teleport_chanting = False

    def move_direction(self, direction):
        if self.teleport_chanting:
            return

        x = self.speed / Const.FPS * direction[0] / sqrt(direction[0] ** 2 + direction[1] ** 2)
        y = self.speed / Const.FPS * direction[1] / sqrt(direction[0] ** 2 + direction[1] ** 2)
        super().move(x, y)

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))

    def teleport(self, destination: pg.Vector2):
        """
        ghost will transport to the destination after a little delay.
        This won't automatically clip the position so you need to worry out-of-bound moving.
        """
        if self.teleport_chanting:
            return
        # if (time now) - self.teleport_last_time < self.teleport_cd:
        #     return
        self.teleport_chanting = True
        self.teleport_distination = destination
        self.teleport_chanting_time = Const.GHOST_CHATING_TIME
