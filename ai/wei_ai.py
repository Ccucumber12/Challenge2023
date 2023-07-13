from api.api import *


class TeamAI(AI):
    def __init__(self) -> None:
        # while True:
        #     pass
        # super(
        # ItemType.CLOAK = 10
        super().__init__()

        self.weight = {ItemType.GOLDEN_SNITCH: 10, ItemType.CLOAK: 20,
                       ItemType.PATRONUS: 10, ItemType.PETRIFICATION: 20,
                       ItemType.SORTINGHAT: 30}
        self.random_dest: Vector2 | None = None

    def update_weight(self):
        myself = get_myself()
        ghosts = get_ghosts()
        if myself.effect == EffectType.CLOAK:
            self.weight[ItemType.GOLDEN_SNITCH] = 40
        else:
            self.weight[ItemType.GOLDEN_SNITCH] = 10
        for ghost in ghosts:
            if (myself.position - ghost.position).length() < 300:
                self.weight[ItemType.SORTINGHAT] = 50
                self.weight[ItemType.CLOAK] = 50
            else:
                self.weight[ItemType.SORTINGHAT] = 30
                self.weight[ItemType.CLOAK] = 20

    def update_random_dest(self):
        import random
        myself = get_myself()
        while (self.random_dest is None
               or (myself.position - self.random_dest).length() < 20
               or get_ground_type(self.random_dest) == GroundType.OBSTACLE):
            self.random_dest = myself.position + (random.randint(1, 100), random.randint(1, 100))

    def choose_item(self) -> Item | None:
        def calculate_weight(myself: Player, item: Item):
            if (myself.position - item.position).length() == 0:
                return 1000000000
            return self.weight[item.type] / (myself.position - item.position).length()

        self.update_weight()
        myself = get_myself()
        items = get_items()
        chosen = None
        for item in items:
            if (chosen is None
                or (calculate_weight(myself, item) > calculate_weight(myself, chosen)
                    and myself.effect_remain * myself.speed < (myself.position - item.position).length())):
                chosen = item
        return chosen

    def escaped_ghost(self) -> Ghost | None:
        myself = get_myself()
        nearest = get_nearest_ghost()
        escaped = None
        if myself.effect_remain > 2 and myself.effect == EffectType.SORTINGHAT:
            return None
        if (not nearest.chanting
                and distance_to(nearest.position) < 5 * get_ticks_per_second() * nearest.speed):
            escaped = nearest
        return escaped

    def move_along(self, direction: Vector2) -> Vector2 | None:
        if direction.length() == 0:
            return get_myself().position
        myself = get_myself()
        displacement = direction.normalize() * myself.speed
        for _ in range(3):
            if get_ground_type(myself.position + displacement) != GroundType.OBSTACLE:
                return myself.position + displacement
            displacement /= 2
        if displacement.length() < myself.speed / 5:
            # print("Failed to move along, rotate")
            return self.move_along(direction.rotate(10))

    def player_tick(self) -> Vector2:
        # while True:
        #     pass
        # ItemType.CLOAK = 10
        # super(
        myself = get_myself()
        chosen_item = self.choose_item()
        escaped_ghost = self.escaped_ghost()
        if escaped_ghost is not None:
            direction = -(escaped_ghost.position - myself.position)
            return self.move_along(direction)
        elif chosen_item is not None:
            return chosen_item.position
        else:
            self.update_random_dest()
            return self.random_dest
