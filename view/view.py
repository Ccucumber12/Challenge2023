import os

import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager, get_game_engine
from view.particle import CastMagicParticleEffect, GatheringParticleEffect


class Object():
    def __init__(self, y, object_type: const.ObjectType, position: pg.Vector2,
                 image_index, detail: tuple):
        self.y = y
        self.object_type = object_type
        self.position = position
        self.image_index = image_index
        self.detail = detail


class GraphicalView:
    """
    Draws the state of GameEngine onto the screen.
    """
    background = pg.Surface(const.ARENA_SIZE)

    def __init__(self):
        model = get_game_engine()
        """
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        """
        self.register_listeners()

        # optimization

        self.screen = pg.display.set_mode(size=const.WINDOW_SIZE, flags=pg.DOUBLEBUF)
        pg.display.set_caption(const.WINDOW_CAPTION)
        self.background.fill(const.BACKGROUND_COLOR)

        # characters' directions
        self.character_direction = {}
        for player in const.PlayerIds:
            self.character_direction[player] = const.CharacterDirection.DOWN

        # animations
        self.ghost_teleport_chanting_animations: list[GatheringParticleEffect] = []
        self.petrification_animation: list[CastMagicParticleEffect] = []
        self.sortinghat_animations = []
        self.ghost_kill_animations = []

        # scale the pictures to proper size
        self.pictures = {}
        self.character_image = {}
        self.petrified_player_image = {}
        self.transparent_player_image = {}
        self.wearing_sortinghat_image = {}
        self.shining_player_image = {}
        self.dead_player_image = {}
        self.sortinghat_animation_picture = []
        self.shining_patronus: pg.Surface
        self.magic_circle: pg.Surface

        def crop(picture: pg.Surface, desire_width, desire_height, large=False):
            """
            Will scale the image to desire size without changing the ratio of the width and height.

            The size of cropped image won't be bigger than desired size if `large == False`.

            The size of cropped image won't be smaller than desired size if `large == True`.
            """
            image = picture.convert_alpha()
            bounding_rect = image.get_bounding_rect()
            cropped_image = pg.Surface(bounding_rect.size, pg.SRCALPHA)
            cropped_image.blit(image, (0, 0), bounding_rect)
            width, height = [cropped_image.get_width(), cropped_image.get_height()]
            if large:
                ratio = max(desire_width/width, desire_height/height)
            else:
                ratio = min(desire_width/width, desire_height/height)
            cropped_image = pg.transform.scale(cropped_image, (width*ratio, height*ratio))
            return cropped_image

        for item in const.ItemType:
            picture = pg.image.load(const.PICTURES_PATH[item]).convert_alpha()
            self.pictures[item] = crop(picture, const.ITEM_RADIUS*2, const.ITEM_RADIUS*2, True)
            self.transparent_player_image[item] = self.pictures[item].convert_alpha()
            self.transparent_player_image[item].set_alpha(const.NEAR_VANISH_TRANSPARENCY)

        for player in const.PlayerIds:
            # normal
            self.character_image[player] = {}
            picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                 const.PICTURES_PATH[const.PlayerSkins.NORMAL],
                                                 "front.png")).convert_alpha()
            self.character_image[player][const.CharacterDirection.DOWN] =\
                crop(picture, const.PLAYER_RADIUS*2, const.PLAYER_RADIUS*2, True)
            picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                 const.PICTURES_PATH[const.PlayerSkins.NORMAL],
                                                 "left.png")).convert_alpha()
            self.character_image[player][const.CharacterDirection.LEFT] =\
                crop(picture, const.WINDOW_SIZE[0],
                     self.character_image[player][const.CharacterDirection.DOWN].get_height())
            picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                 const.PICTURES_PATH[const.PlayerSkins.NORMAL],
                                                 "rear.png")).convert_alpha()
            self.character_image[player][const.CharacterDirection.UP] =\
                crop(picture, const.WINDOW_SIZE[0],
                     self.character_image[player][const.CharacterDirection.DOWN].get_height())
            picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                 const.PICTURES_PATH[const.PlayerSkins.NORMAL],
                                                 "right.png")).convert_alpha()
            self.character_image[player][const.CharacterDirection.RIGHT] =\
                crop(picture, const.WINDOW_SIZE[0],
                     self.character_image[player][const.CharacterDirection.DOWN].get_height())

            # grayscale
            self.petrified_player_image[player] = {}
            for direction in const.CharacterDirection:
                self.petrified_player_image[player][direction] = pg.transform.grayscale(
                    self.character_image[player][direction])

            # transparent
            self.transparent_player_image[player] = {}
            for direction in const.CharacterDirection:
                self.transparent_player_image[player][direction] =\
                    self.character_image[player][direction].convert_alpha()
                self.transparent_player_image[player][direction].set_alpha(
                    const.CLOAK_TRANSPARENCY)

            def load_player_skin(player, imgdic: dict, skin: const.PlayerSkins):
                imgdic[player] = {}
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[skin],
                                                     "front.png")).convert_alpha()
                imgdic[player][const.CharacterDirection.DOWN] = crop(
                    picture, self.character_image[player][const.CharacterDirection.DOWN].get_width(
                    ),
                    const.PLAYER_RADIUS*5)
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[skin],
                                                     "left.png")).convert_alpha()
                imgdic[player][const.CharacterDirection.LEFT] =\
                    crop(picture, const.WINDOW_SIZE[0],
                         imgdic[player][const.CharacterDirection.DOWN].get_height())
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[skin],
                                                     "rear.png")).convert_alpha()
                imgdic[player][const.CharacterDirection.UP] =\
                    crop(picture, const.WINDOW_SIZE[0],
                         imgdic[player][const.CharacterDirection.DOWN].get_height())
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[skin],
                                                     "right.png")).convert_alpha()
                imgdic[player][const.CharacterDirection.RIGHT] =\
                    crop(picture, const.WINDOW_SIZE[0],
                         imgdic[player][const.CharacterDirection.DOWN].get_height())

            # sortinghat
            load_player_skin(player, self.wearing_sortinghat_image, const.PlayerSkins.SORTINGHAT)

            # shining player
            self.shining_player_image[player] = {}
            for direction in const.CharacterDirection:
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[const.PlayerSkins.SHINING],
                                                     const.PICTURES_PATH[direction])).convert_alpha()
                self.shining_player_image[player][direction] =\
                    crop(picture, *const.SHINING_PLAYER_SIZE[direction], True)
            
            #dead player
            self.dead_player_image[player] = {}
            for direction in const.CharacterDirection:
                picture = pg.image.load(os.path.join(const.PICTURES_PATH[player],
                                                     const.PICTURES_PATH[const.PlayerSkins.DEAD],
                                                     const.PICTURES_PATH[direction])).convert_alpha()
                self.dead_player_image[player][direction] =\
                    crop(picture, *const.DEAD_PLAYER_SIZE[direction], True)

        for ghost in const.GhostIds:
            if ghost == const.GhostIds.DEMENTOR:
                self.character_image[ghost] = []
                for i in range(const.DEMENTOR_PICTURE_NUMBER):
                    picture = pg.image.load(os.path.join(const.PICTURES_PATH[ghost], "dementor" + 
                                                         str(i) + ".png")).convert_alpha()
                    self.character_image[ghost].append(crop(picture, const.GHOST_RADIUS*2, const.GHOST_RADIUS*2, True))
        self.ghost_killing_image = {}
        picture = pg.image.load(os.path.join(const.PICTURES_PATH[const.GhostSkins.KILLING], "right.png")).convert_alpha()
        self.ghost_killing_image[const.CharacterDirection.RIGHT] = crop(picture, const.GHOST_RADIUS*2, const.GHOST_RADIUS*2, True)
        picture = pg.image.load(os.path.join(const.PICTURES_PATH[const.GhostSkins.KILLING], "left.png")).convert_alpha()
        self.ghost_killing_image[const.CharacterDirection.LEFT] = crop(picture, const.GHOST_RADIUS*2, const.GHOST_RADIUS*2, True)

        self.background_images = []
        for i in model.map.images:
            loaded_image = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            loaded_image = pg.transform.scale(loaded_image, const.ARENA_SIZE)
            self.background_images.append((int(model.map.images[i]), loaded_image))

        picture = pg.image.load(const.PICTURES_PATH[const.Scene.SCORE_BOARD]).convert_alpha()
        self.pictures[const.Scene.SCORE_BOARD] = crop(
            picture, const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.Scene.TITLE]).convert_alpha()
        self.pictures[const.Scene.TITLE] = crop(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.Scene.FOG]).convert_alpha()
        picture.set_alpha(const.FOG_TRANSPARENCY)
        self.pictures[const.Scene.FOG] = crop(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.Scene.ENDGAME]).convert_alpha()
        self.pictures[const.Scene.ENDGAME] = crop(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        self.fog = Fog(self.screen, self.pictures[const.Scene.FOG], const.FOG_SPEED)
        # print(self.pictures[const.SCENE.FOG].get_width())
        # print(self.pictures[const.SCENE.FOG].get_height())

        # Animation
        picture = pg.image.load(const.PICTURES_PATH[const.OtherPictures.PATRONUS]).convert_alpha()
        self.shining_patronus = crop(
            picture, const.PATRONUS_RADIUS*2, const.PATRONUS_RADIUS*2, True)
        picture = pg.image.load(
            const.PICTURES_PATH[const.OtherPictures.MAGIC_CIRCLE]).convert_alpha()
        self.magic_circle = crop(
            picture, const.MAGIC_CIRCLE_RADIUS*2, const.MAGIC_CIRCLE_RADIUS*2, True)
        self.magic_circle.set_alpha(127)
        picture = pg.image.load(const.PICTURES_PATH[const.ItemType.SORTINGHAT]).convert_alpha()
        self.sortinghat_animation_picture.append(
            crop(picture, const.ITEM_RADIUS, const.ITEM_RADIUS))

        angle = 0
        while angle < 360:
            angle += const.SORTINGHAT_ANIMATION_ROTATE_SPEED / const.FPS
            self.sortinghat_animation_picture.append(
                pg.transform.rotate(self.sortinghat_animation_picture[0], angle))

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        model = get_game_engine()
        model.register_user_event(const.GOLDEN_SNITCH_APPEAR_TIME, self.last_stage_handler)

    def last_stage_handler(self):
        self.fog.start = True

    def handle_every_tick(self, event):
        self.display_fps()

        model = get_game_engine()
        cur_state = model.state
        if cur_state == const.STATE_MENU:
            self.render_menu()
        elif cur_state == const.STATE_PLAY:
            self.render_play()
        elif cur_state == const.STATE_STOP:
            self.render_stop()
        elif cur_state == const.STATE_ENDGAME:
            self.render_endgame()

    def handle_player_move(self, event: EventPlayerMove):
        move_direction = event.direction
        direction = const.CharacterDirection.DOWN
        if move_direction.length() == 0:
            return
        down = move_direction.dot((0, 1))
        up = move_direction.dot((0, -1))
        left = move_direction.dot((-1, 0))
        right = move_direction.dot((1, 0))
        mx = max(down, up, left, right)
        if left == mx:
            direction = const.CharacterDirection.LEFT
        elif right == mx:
            direction = const.CharacterDirection.RIGHT
        elif up == mx:
            direction = const.CharacterDirection.UP
        self.character_direction[event.player_id] = direction

    def handle_ghost_kill(self, event: EventGhostKill):
        self.ghost_kill_animations.append((event.ghost_id, event.destination, event.victim_id, event.victim_effect,
                                           get_game_engine().timer + const.GHOST_KILL_ANIMATION_TIME))

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventGhostTeleportChant,
                                     self.add_ghost_teleport_chanting_animation)
        ev_manager.register_listener(EventCastPetrification, self.add_cast_petrification_animation)
        ev_manager.register_listener(EventSortinghat, self.add_sortinghat_animation)
        ev_manager.register_listener(EventTimesUp, self.register_places)
        ev_manager.register_listener(EventPlayerMove, self.handle_player_move)
        ev_manager.register_listener(EventGhostKill, self.handle_ghost_kill)

    def display_fps(self):
        """
        Display the current fps on the window caption.
        """
        model = get_game_engine()
        pg.display.set_caption(f'{const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')

    def add_ghost_teleport_chanting_animation(self, event):
        model = get_game_engine()
        self.ghost_teleport_chanting_animations.append((
            GatheringParticleEffect(event.position, const.GHOST_CHANTING_TIME + model.timer,
                                    const.GHOST_CHANTING_COLOR), event.destination))

    def add_cast_petrification_animation(self, event):
        self.petrification_animation.append((
            CastMagicParticleEffect(event.attacker, event.victim, const.PETRIFICATION_ANIMATION_SPEED,
                                    const.PETRIFICATION_ANIMATION_COLOR,
                                    const.PETRIFICATION_ANIMATION_THICKNESS), event.victim))

    def add_sortinghat_animation(self, event):
        model = get_game_engine()
        position = model.players[event.assailant.value].position
        victim = event.victim
        self.sortinghat_animations.append((position, victim, 0))

    def register_places(self, event: EventTimesUp):
        self.places = event.places

    def render_menu(self):
        # draw background
        # self.screen.fill(Const.BACKGROUND_COLOR)
        self.screen.blit(self.pictures[const.Scene.TITLE],
                         ((const.WINDOW_SIZE[0]-const.TITLE_SIZE[0])/2, 0))

        # draw text
        font = pg.font.Font(os.path.join(const.FONT_PATH, "VinerHandITC.ttf"), 36)
        text_surface = font.render("Press [space] to start ...", 1, pg.Color('gray88'))
        text_center = (const.WINDOW_SIZE[0] / 2, 40)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))
        text_surface = font.render("Press [F1] to mute/unmute music", 1, pg.Color('gray88'))
        text_center = (const.WINDOW_SIZE[0] / 2, 80)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))

        pg.display.flip()

    def render_play(self):
        # draw background
        self.screen.fill(const.BACKGROUND_COLOR)
        model = get_game_engine()

        # draw players
        game_map = model.map
        objects: list[Object] = []
        for item in model.items:
            coord = game_map.convert_coordinate(item.position)
            detail = (item.vanish_time, )
            objects.append(Object(coord[1], const.ObjectType.ITEM,
                                  item.position, item.type, detail))
        for player in model.players:
            coord = game_map.convert_coordinate(player.position)
            detail = (player.effect, player.dead, player.effect_timer)
            for kill_animation in self.ghost_kill_animations:
                if kill_animation[2] == player.player_id:
                    detail = (kill_animation[3], player.dead, const.GAME_LENGTH)
                    break
            objects.append(
                Object(coord[1], const.ObjectType.PLAYER, player.position, player.player_id, detail))
        for ghost in model.ghosts:
            coord = game_map.convert_coordinate(ghost.position)
            objects.append(
                Object(coord[1], const.ObjectType.GHOST, ghost.position, ghost.ghost_id, tuple()))
        for patronus in model.patronuses:
            coord = game_map.convert_coordinate(patronus.position)
            detail = (patronus.death_time, )
            objects.append(Object(coord[1], const.ObjectType.PATRONUS,
                                  patronus.position, None, detail))

        for row, image in self.background_images:
            objects.append(Object(row, const.ObjectType.MAP, pg.Vector2(0, 0), None, (image,)))

        objects.sort(key=lambda x: x.y)
        half_sec = model.timer // (const.FPS // 2)
        quater_sec = model.timer // (const.FPS // 4)

        def render_picture(image_dic: dict, index, direction):
            width = image_dic[index][direction].get_width()
            height = image_dic[index][direction].get_height()
            ul = [x - y for x, y in zip(obj.position, [width/2, height])]
            self.screen.blit(image_dic[index][direction], ul)
            
        for obj in objects:
            # ul means upper left
            if obj.object_type == const.ObjectType.PLAYER:
                direction = self.character_direction[obj.image_index]
                effect, dead, effect_timer = obj.detail
                # if dead:
                #     if half_sec % 2 == 0:
                #         self.screen.blit(self.transparent_player_image[obj[2]], obj[3])
                #     else:
                #         self.screen.blit(self.pictures[obj[2]], obj[3])
                width = self.character_image[obj.image_index][direction].get_width()
                height = self.character_image[obj.image_index][direction].get_height()
                ul = [x - y for x, y in zip(obj.position, [width/2, height])]
                if effect_timer < const.ITEM_LOSE_EFFECT_HINT_TIME and quater_sec % 2 == 0:
                    self.screen.blit(self.character_image[obj.image_index][direction], ul)
                elif dead:
                    if direction == const.CharacterDirection.DOWN or direction == const.CharacterDirection.UP:
                        render_picture(self.dead_player_image, obj.image_index, direction)
                    if direction == const.CharacterDirection.LEFT:
                        width = self.dead_player_image[obj.image_index][direction].get_width()
                        height = self.dead_player_image[obj.image_index][direction].get_height()
                        ul = [x - y for x, y in zip(obj.position, [width/2-7, height])]
                        self.screen.blit(self.dead_player_image[obj.image_index][direction], ul)
                    if direction == const.CharacterDirection.RIGHT:
                        width = self.dead_player_image[obj.image_index][direction].get_width()
                        height = self.dead_player_image[obj.image_index][direction].get_height()
                        ul = [x - y for x, y in zip(obj.position, [width/2+7, height])]
                        self.screen.blit(self.dead_player_image[obj.image_index][direction], ul)
                elif effect == const.EffectType.PETRIFICATION:
                    self.screen.blit(self.petrified_player_image[obj.image_index][direction], ul)
                elif effect == const.EffectType.CLOAK:
                    self.screen.blit(self.transparent_player_image[obj.image_index][direction], ul)
                elif effect == const.EffectType.SORTINGHAT:
                    width = self.wearing_sortinghat_image[obj.image_index][direction].get_width()
                    height = self.wearing_sortinghat_image[obj.image_index][direction].get_height()
                    ul = [x - y for x, y in zip(obj.position, [width/2, height])]
                    self.screen.blit(self.wearing_sortinghat_image[obj.image_index][direction], ul)
                elif effect == const.EffectType.REMOVED_SORTINGHAT:
                    width = self.shining_player_image[obj.image_index][direction].get_width()
                    height = (self.character_image[obj.image_index][direction].get_height() + 
                              self.shining_player_image[obj.image_index][direction].get_height()) / 2
                    ul = [x - y for x, y in zip(obj.position, [width/2, height])]
                    self.screen.blit(self.shining_player_image[obj.image_index][direction], ul)
                else:
                    self.screen.blit(self.character_image[obj.image_index][direction], ul)
            elif obj.object_type == const.ObjectType.GHOST:
                ul = [x - y for x, y in zip(obj.position,
                                            [const.GHOST_RADIUS, const.GHOST_RADIUS*2])]
                # if obj.image_index == const.GhostIds.DEMENTOR:
                ghost_shown = False
                for kill_animation in self.ghost_kill_animations:
                    if kill_animation[0] == obj.image_index:
                        if obj.position.x < kill_animation[1].x:
                            self.screen.blit(self.ghost_killing_image[const.CharacterDirection.RIGHT], ul)
                        else:
                            self.screen.blit(self.ghost_killing_image[const.CharacterDirection.LEFT], ul)
                        ghost_shown = True
                        break
                if not ghost_shown:
                    self.screen.blit(self.character_image[const.GhostIds.DEMENTOR][model.timer//const.ANIMATION_PICTURE_LENGTH % const.DEMENTOR_PICTURE_NUMBER], ul)
            elif obj.object_type == const.ObjectType.PATRONUS:
                effect_timer = obj.detail[0]
                if quater_sec % 2 == 0 or model.timer + const.ITEM_LOSE_EFFECT_HINT_TIME <= effect_timer:
                    ul = [x - y for x, y in zip(obj.position,
                                                [const.PATRONUS_RADIUS, const.PATRONUS_RADIUS*2])]
                    self.screen.blit(self.shining_patronus, ul)
            elif obj.object_type == const.ObjectType.MAP:
                self.screen.blit(obj.detail[0], obj.position)
            elif obj.object_type == const.ObjectType.ITEM:
                ul = [x - y for x, y in zip(obj.position,
                                            [const.ITEM_RADIUS, const.ITEM_RADIUS*2])]
                # It's acually is a rectangle.
                vanish_time = obj.detail[0]
                # if half_sec % 2 == 0 or model.timer + 5*const.FPS < vanish_time:
                #     self.screen.blit(self.pictures[obj.image_index], obj.position)
                # else:
                #     self.screen.blit(self.transparent_player_image[Object[2]], Object[3])
                self.screen.blit(self.pictures[obj.image_index], ul)

        # Ghost teleport chanting animation
        animations = self.ghost_teleport_chanting_animations.copy()
        for animation in animations:
            effect = animation[0]
            destination = animation[1]
            if effect.alive_time < model.timer:
                self.ghost_teleport_chanting_animations.remove(animation)
                continue
            for particle in effect.particles:
                pg.draw.circle(self.screen, particle.color, particle.position, particle.radius)
            effect.tick()
            ul = [x - y for x, y in zip(destination,
                                        [const.MAGIC_CIRCLE_RADIUS, const.MAGIC_CIRCLE_RADIUS])]
            self.screen.blit(self.magic_circle, ul)

        # Cast petrification animation
        animations = self.petrification_animation.copy()
        for animation in animations:
            effect = animation[0]
            victim = animation[1]
            if effect.tick() == True:
                self.petrification_animation.remove(animation)
                get_event_manager().post(EventPetrify(victim))
                continue
            for particle in effect.particles:
                pg.draw.circle(self.screen, particle.color, particle.position, particle.radius)

        # Sortinghat animation
        animations = self.sortinghat_animations.copy()
        for animation in animations:
            position = animation[0]
            victim = animation[1]
            destination = model.players[victim.value].position
            index = animation[2]
            self.sortinghat_animations.remove(animation)
            if (destination-position).length() < 2 * const.SORTINGHAT_ANIMATION_SPEED / const.FPS:
                # maybe here can add some special effect
                continue
            self.screen.blit(self.sortinghat_animation_picture[index], position)
            index += 1
            if index == len(self.sortinghat_animation_picture):
                index = 0
            position = position + \
                (destination-position).normalize() * const.SORTINGHAT_ANIMATION_SPEED / const.FPS
            self.sortinghat_animations.append((position, victim, index))

        # Ghost Killing Animation
        # for kill_animation in self.ghost_kill_animations:
        #     pg.draw.line(self.screen, pg.Color('red'), kill_animation[1] + pg.Vector2(-15, -20 - 35),
        #                  kill_animation[1] + pg.Vector2(15, 20 - 35), 10)
        #     pg.draw.line(self.screen, pg.Color('red'), kill_animation[1] + pg.Vector2(-15, 20 - 35),
        #                  kill_animation[1] + pg.Vector2(15, -20 - 35), 10)
        kill_animation_end_list = []
        for kill_animation in self.ghost_kill_animations:
            if model.timer > kill_animation[4]:
                kill_animation_end_list.append(kill_animation)
        for kill_animation in kill_animation_end_list:
            self.ghost_kill_animations.remove(kill_animation)

        # Fog
        self.fog.tick()

        # Scoreboard
        self.screen.blit(self.pictures[const.Scene.SCORE_BOARD], (const.ARENA_SIZE[0], 0))

        def print_text(text, position, font="magic-school.one.ttf", size=36):
            font = pg.font.Font(os.path.join(const.FONT_PATH, font), size)
            text_surface = font.render(str(text), True, pg.Color('black'))
            self.screen.blit(text_surface, text_surface.get_rect(center=position))
        # Name
        for i in range(const.NUM_OF_PLAYERS):
            print_text(const.PLAYER_NAME[i], const.NAME_POSITION[i], "VinerHandITC.ttf", 20)
        # Time
        count_down = (const.GAME_LENGTH - model.timer) // const.FPS
        print_text(count_down // 60 // 10, const.TIME_POSITION[0])
        print_text(count_down // 60 % 10, const.TIME_POSITION[1])
        print_text(count_down % 60 // 10, const.TIME_POSITION[2])
        print_text(count_down % 60 % 10, const.TIME_POSITION[3])
        # Score
        for i in range(const.NUM_OF_PLAYERS):
            score = model.players[i].score
            j = 1000
            for position in const.SCORE_POSITION[i]:
                print_text(int(score // j % 10), position)
                j /= 10

        pg.display.flip()

    def render_stop(self):
        pass

    def render_endgame(self):
        # draw background
        self.screen.blit(self.pictures[const.Scene.ENDGAME],
                         ((const.WINDOW_SIZE[0] - const.ENDGAME_SIZE[0]) / 2, 0))

        # draw text
        font = pg.font.Font(os.path.join(const.FONT_PATH, "VinerHandITC.ttf"), 36)
        text_surface = font.render("Game Over", 1, pg.Color('black'))
        text_center = (const.WINDOW_SIZE[0] / 2, 40)
        self.screen.blit(text_surface, text_surface.get_rect(center=text_center))
        for place in range(3):
            ul = [x - y for x, y in zip(const.PODIUM_POSITION[place],
                                        [const.PLAYER_RADIUS, const.PLAYER_RADIUS*2])]
            self.screen.blit(
                self.character_image[self.places[place].player_id][const.CharacterDirection.DOWN], ul)
            font = pg.font.Font(os.path.join(const.FONT_PATH, "VinerHandITC.ttf"), 36)
            text_surface = font.render(str(self.places[place].score), 1, pg.Color('black'))
            text_center = const.FINAL_SCORE_POSITION[place]
            self.screen.blit(text_surface, text_surface.get_rect(center=text_center))

        pg.display.flip()


class Fog:
    def __init__(self, screen, fog: pg.surface, speed):
        self.start = False
        self.picture = fog
        self.position = pg.Vector2(0, const.ARENA_SIZE[1])
        self.speed = speed
        self.screen = screen
        self.raising = True

    def tick(self):
        if not self.start:
            return
        if self.raising:
            self.position = self.position + pg.Vector2(0, -self.speed)
            if self.position.y <= 0:
                self.position.y = 0
                self.raising = False
        self.screen.blit(self.picture, self.position)
        self.screen.blit(self.picture, self.position - pg.Vector2(const.FOG_SIZE[0], 0))
        self.position = self.position + pg.Vector2(self.speed, 0)
        if self.position.x > const.WINDOW_SIZE[0]:
            self.position.x -= const.FOG_SIZE[0]
