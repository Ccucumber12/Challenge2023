from pygame import Vector2

from api.api import *


class TeamAI(AI):

    def player_tick(self) -> Vector2:
        vec = get_nearest_ghost().position - get_myself().position
        if 0 < vec.length() <= 300:
            return get_myself().position - vec.normalize() * get_myself().speed
        elif get_nearest_item() is not None:
            # print('test', get_myself().id, get_items())
            for i in get_items():
                if i.type == ItemType.GOLDEN_SNITCH:
                    return i.position
            return get_nearest_item().position
        else:
            return get_myself().position
