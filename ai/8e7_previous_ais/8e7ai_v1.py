from pygame import Vector2

from api.api import *
import random


class TeamAI(AI):

    def evaluate_position(self, pos):
        #tries to find the most "empty" position that is nearby
        ghosts = get_ghosts()
        ret = distance(pos, get_myself().position)
        if get_ground_type(pos) == GroundType.OBSTACLE:
            ret += 10000
        for ghost in ghosts:
            ret -= distance(ghost.position, get_myself().position)
        ret -= distance(get_myself().position, get_nearest_player().position)
        return ret

    def player_tick(self) -> Vector2:
        pos = get_myself().position
        vec = get_nearest_ghost().position - pos
        if get_myself().effect == EffectType.SORTINGHAT:
            return pos + vec
        if vec.length() < 250:
            return pos - vec
        if get_nearest_item() is not None:
            for i in get_items():
                if i.type == ItemType.SORTINGHAT:
                    return i.position
            return get_nearest_item().position
        else:
            candidates = [Vector2(random.uniform(0, 1200), random.uniform(0, 800)) for i in range(10)] 
            ret = min(candidates,
                key=lambda x: self.evaluate_position(x),
                default=None)
            return ret
