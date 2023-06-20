import random
from math import sqrt, ceil

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
        speed = Const.PLAYER_SPEED
        super().__init__(position, speed)
        self.dead = False
        self.invisible = False
        self.invincible = 0 # will be invicible until timer > invincible.
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
        if self.iscaught():
            self.caught()

    def iscaught(self):
        if self.dead or self.invincible:
            # If the player has sortinghat and is invincible, the effect of sortinghat won't triggered.
            # Even if the player is invisible, the ghost can still catch him.
            return False
        model = get_game_engine()
        for ghost in model.ghosts:
            xx = (self.position.x - ghost.position.x) ** 2
            yy = (self.position.y - ghost.position.y) ** 2
            if xx + yy < ((Const.PLAYER_RADIUS + Const.GHOST_RADIUS) ** 2):
                return True
        return False

    def caught(self):
        """
        Caught by the ghost.
        Kill player
        """
        print(f"Player {self.player_id} is caught!")
        model = get_game_engine()
        if self.effect == "sortinghat":
            others = [x for x in range(4) if x != self.player_id]
            victim = random.choice(others)
            second = ceil(model.timer / Const.FPS)
            for _ in range(5):
                minute = second // 60
                model.players[victim].score -= Const.PLAYER_ADD_SCORE[minute]
            self.effect = "none"
            self.invincible = model.timer + Const.SORTINGHAT_INVINCIBLE_TIME
            return
        elif not self.dead:
            self.dead = True
            model.register_user_event(Const.PLAYER_RESPAWN_TIME, self.respawn_handler)

    def respawn_handler(self):
        self.dead = False

    def move_direction(self, direction: str):
        """
        Move the player along the direction by its speed.
        Will automatically clip the position so no need to worry out-of-bound moving.
        """
        # Modify position of player
        # self.position += self.speed / Const.FPS * Const.DIRECTION_TO_VEC2[direction]
        if self.effect == "petrification":
            return
        x = 1 if direction == 'right' else -1 if direction == 'left' else 0
        y = 1 if direction == 'down' else -1 if direction == 'up' else 0
        super().move(x, y)

        # clipping
        self.position.x = max(0, min(Const.ARENA_SIZE[0], self.position.x))
        self.position.y = max(0, min(Const.ARENA_SIZE[1], self.position.y))

    def add_score(self, minutes: int):
        # if self.dead:
        #    return
        self.score += Const.PLAYER_ADD_SCORE[minutes]
        # print(self.score)

    def remove_effect(self):
        self.effect_timer = 0
        if self.effect == "cloak":
            self.invisible = False
        elif self.effect == "patronus":
            pass
        self.effect = "none"

    def get_effect(self, effect: str, effect_status: str):
        self.effect = effect
        self.effect_timer = Const.ITEM_DURATION[effect][effect_status]
        if self.effect == "cloak":
            self.invisible = True
        elif self.effect == "patronus":
            model = get_game_engine()
            model.patronuses.append(Patronus(0, self.position, random.randint(0, 3)))
            # The parameters passed is not properly assigned yet
        elif self.effect == "petrification":
            # One can't move when it's effect is pertification.
            # It will be implemented in function move_direction.
            pass


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
        self.teleport_available_time = 0 # Ghost can teleport if timer >= teleport_available_time
        self.teleport_cd = teleport_cd
        self.teleport_chanting = False  # if it is chantting
        self.teleport_time = -1 # Ghost will teleport if timer == teleport_time
        # self.teleport_chanting_time is how long it has to continue chanting. NOT teleport cd.
        self.teleport_distination = pg.Vector2(0, 0)
        self.prey = None

    def tick(self):
        """
        Run when EventEveryTick() arises.
        """
        model = get_game_engine()
        if model.timer == self.teleport_time:
            self.position = self.teleport_distination
            self.teleport_chanting = False

    def move_direction(self, direction):
        if self.teleport_chanting:
            return

        if direction[0] != 0 or direction[1] != 0:
            # Avoid division by zero
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
        model = get_game_engine()
        if self.teleport_chanting:
            return
        if model.timer < self.teleport_available_time:
            return
        self.teleport_chanting = True
        self.teleport_distination = destination
        self.teleport_time = model.timer + Const.GHOST_CHATING_TIME
        self.teleport_available_time = model.timer + self.teleport_cd
    
    def chase(self):
        """
        Ghost will move toward its prey.
        """
        if (self.prey is None):
            return
        self.move_direction([self.prey.position.x, self.prey.position.y]-self.position)

    def hunt(self):
        """
        AI of ghost.
        Determine what ghost should do next.
        """
        model = get_game_engine()
        if (self.prey is None):
            # TEST
            self.prey = model.players[0]
        self.chase()