from pygame import Vector2

from api.api import *


class TeamAI(AI):

    def player_tick(self) -> Vector2:
        vec = get_nearest_ghost().position - get_myself().position
        if 0 < vec.length() <= 100:
            return get_myself().position - vec.normalize() * get_myself().speed
        else:
            return get_myself().position
