from InstancesManager import get_game_engine


class Item:
    def __init__(self, position, item_id, item_type, item_width, item_height, item_status):
        self.id = item_id
        self.type = item_type
        # specify the type of item ["cloak": 隱形斗篷, "patronus": 護法, "golden_snitch": 金探子, "petrification": 石化]
        self.position = position  # is a pg.Vector2
        self.width = item_width
        self.height = item_height
        self.status = item_status  # ["normal", "reversed", "enhanced"]

    def tick(self):
        model = get_game_engine()
        for player in model.players:
            if self.position.x - (self.width / 2) <= player.position.x <= self.position.x + (self.width / 2) and \
                    self.position.y - (self.height / 2) <= player.position.y <= self.position.y + (self.height / 2):
                '''
                Apply the effect to the player according to the type of item (item_type).
                '''
                if self.status == "normal":
                    player.get_status(self.type, self.status)

class Item_Generator:
    def __init__(self):
        self.generate_cd = Const.ITEM_GENERATE_COOLDOWN
        self.golden_snitch_tag = 0
        self.id_counter = 1

    def generate(self):
        generated_item = None

        #determining type of item
        type_id = 0
        if self.golden_snitch == 1:
            type_id = random.randint(0, 2)
        else:
            type_id = random.randint(0, 3)
        generate_type = "clock" if type_id == 0 else "patronus" if type_id == 1 else "golden_snitch" if type_id == 3 else "petrification" if type_id == 2
        if type_id == 3:
            self.golden_snitch_tag = 1

        #determining status of item (could modify probility by modifying the constants)
        status_id = random.randint(1, 15)
        generate_status = "normal" if 1 <= status_id <= 12 else "reversed" if status_id == 13 else "enhanced" if 14 <= status_id <=15
   
        #determining location of item
        generate_x = 0
        generate_y = 0
        '''
        Put a random method to determine location here
        '''

        generated_item = Item(Vector2(generate_x, generate_y), self.idcounter, generate_type, Const.ITEM_WIDTH, Const.ITEM_HEIGHT, generate_status)
        generate_model = get_game_engine()
        generate_model.items.append(generate_item)
        self.id_counter = self.id_counter + 1

    def tick(self):
        self.generate_cd -= 1
        generate_model = get_game_engine()
        if self.generate_cd <= 0:
            if len(generate_model.items) < Const.MAX_ITEN_NUMBER:
                self.generate()
                self.generate_cd = Const.ITEM_GENERATE_COOLDOWN
