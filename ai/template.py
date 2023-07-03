from api.api import *


class TeamAI(AI):

    def player_tick(self) -> Vector2:
        return get_myself().position
