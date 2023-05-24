from InstancesManager import get_game_engine


class Item:
    def __init__(self, position, item_id, item_type, item_width, item_height, item_status):
        self.id = item_id
        self.type = item_type   # specify the type of item ["cloak": 隱形斗篷, "patronus": 護法, "golden_snitch": 金探子, "petrification": 石化]
        self.position = position # is a pg.Vector2
        self.width = item_width
        self.height = item_height
        self.status = item_status # ["normal", "reversed", "enhanced"]

    def tick(self):
        model = get_game_engine()
        for player in model.players:
            if self.position.x - (self.width / 2) <= player.position.x and self.position.x + (self.width / 2) >= player.position.x and self.position.y - (self.height / 2) <= player.position.y and self.position.y - (self.height / 2) <= player.position.y:
                '''
                Apply the effect to the player according to the type of item (item_type).
                '''
                if self.status == "normal":
                    player.get_status(self.type, self.status)
