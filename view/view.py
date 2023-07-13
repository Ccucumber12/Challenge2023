import os
import cv2

import pygame as pg
from pygame import Vector2
from math import pi

import const
import util
from api.api_impl import get_last_target
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

    def __init__(self, r18g):
        model = get_game_engine()
        """
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        """
        self.r18g = r18g
        self.register_listeners()

        self.show_helper = False

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
        self.patronus_shockwave_animations = []
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
        self.portkey_animation_image: list[pg.Surface] = []
        self.portkey_animation: list[GIFAnimation] = []
        self.bleed_animation_images: list[pg.Surface] = []
        self.bleed_animations: list[GIFAnimation] = []

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
            loaded_image = cv2.imread(os.path.join(model.map.map_dir, i), cv2.IMREAD_UNCHANGED)
            loaded_image = cv2.resize(loaded_image, const.ARENA_SIZE, interpolation=cv2.INTER_AREA)
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            picture = pg.transform.scale(picture, const.ARENA_SIZE)
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            self.background_images.append((int(model.map.images[i]), picture, (x, y)))

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

        # port key
        picture = pg.image.load("pictures/other/portal_animation.png").convert_alpha()
        for t in range(8):
            subpicture = picture.subsurface(pg.Rect(t * 64, 128, 64, 64))
            self.portkey_animation_image.append(subpicture)
        
        # bleed animation
        picture = pg.transform.smoothscale(pg.image.load("pictures/other/bleed_animation.png").convert_alpha(), (128*3, 160*2))
        for y in range(2):
            for x in range(3):
                subpicture = picture.subsurface(pg.Rect(128 * x, 160 * y, 128, 160))
                self.bleed_animation_images.append(subpicture)


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
    
    def handle_show_helper(self, event: EventHelpMenu):
        self.show_helper = not self.show_helper

    def handle_player_move(self, event: EventPlayerMove):
        if get_game_engine().players[event.player_id].effect == const.EffectType.PETRIFICATION:
            return
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
    
    def handle_portkey(self, event: EventPortkey):
        self.portkey_animation.append(GIFAnimation(self.screen, event.destination, 
                                             self.portkey_animation_image, int(const.FPS / 3)))

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventHelpMenu, self.handle_show_helper)
        ev_manager.register_listener(EventGhostTeleportChant,
                                     self.add_ghost_teleport_chanting_animation)
        ev_manager.register_listener(EventCastPetrification, self.add_cast_petrification_animation)
        ev_manager.register_listener(EventPatronusShockwave, self.add_patronus_shockwave_animation)
        ev_manager.register_listener(EventSortinghat, self.add_sortinghat_animation)
        ev_manager.register_listener(EventTimesUp, self.register_places)
        ev_manager.register_listener(EventPlayerMove, self.handle_player_move)
        ev_manager.register_listener(EventGhostKill, self.handle_ghost_kill)
        ev_manager.register_listener(EventGhostKill, self.add_player_killed_animation)
        ev_manager.register_listener(EventPortkey, self.handle_portkey)

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

    def add_patronus_shockwave_animation(self, event):
        model = get_game_engine()
        duration = const.PATRONUS_SHOCKWAVE_ANIMATION_DURATION
        self.patronus_shockwave_animations.append((event.position, model.timer + duration, duration))

    def add_sortinghat_animation(self, event):
        model = get_game_engine()
        position = model.players[event.assailant.value].position
        victim = event.victim
        self.sortinghat_animations.append((position, victim, 0))
    
    def add_player_killed_animation(self, event: EventGhostKill):
        if self.r18g:
            self.bleed_animations.append(GIFAnimation(self.screen, event.destination + pg.Vector2(0, -50), 
                                        self.bleed_animation_images, int(const.FPS / 10), const.GHOST_KILL_ANIMATION_TIME))

    def register_places(self, event: EventTimesUp):
        self.places = event.places

    def render_menu(self):
        # draw background
        # self.screen.fill(Const.BACKGROUND_COLOR)
        self.screen.fill(const.BACKGROUND_COLOR)
        self.screen.blit(self.pictures[const.Scene.TITLE],
                         ((const.WINDOW_SIZE[0]-const.TITLE_SIZE[0])/2, 0))

        # draw text
        if not self.show_helper:
            font = pg.font.Font(os.path.join(const.FONT_PATH, "VinerHandITC.ttf"), 36)
            text_surface = font.render("Press [space] to start ...", 1, pg.Color('gray88'))
            text_center = (const.WINDOW_SIZE[0] / 2, 40)
            self.screen.blit(text_surface, text_surface.get_rect(center=text_center))
            text_surface = font.render("Press [ESC] to see helper.", 1, pg.Color('gray88'))
            text_center = (const.WINDOW_SIZE[0] / 2, 80)
            self.screen.blit(text_surface, text_surface.get_rect(center=text_center))
        else:
            background = pg.Surface((const.HELPER_SIZE[0], const.HELPER_SIZE[1]), pg.SRCALPHA)
            background.fill((255, 255, 255, 200))
            self.screen.blit(background, tuple((x - y)/2 for x, y in zip (const.WINDOW_SIZE, const.HELPER_SIZE)))
            # keyboard
            image = pg.image.load("pictures/other/keyboard.png").convert_alpha()
            bounding_rect = image.get_bounding_rect()
            cropped_image = pg.Surface(bounding_rect.size, pg.SRCALPHA)
            cropped_image.blit(image, (0, 0), bounding_rect)
            width, height = [cropped_image.get_width(), cropped_image.get_height()]
            ratio = min((const.HELPER_SIZE[0] * 2 / 3) / width, (const.HELPER_SIZE[1] * 2 / 3) / height)
            cropped_image = pg.transform.scale(cropped_image, (width*ratio, height*ratio))
            self.screen.blit(cropped_image, ((const.WINDOW_SIZE[0] - const.HELPER_SIZE[0] * 2 / 3) / 2, 160))
            # text
            text_position = pg.Vector2((const.WINDOW_SIZE[0] - const.HELPER_SIZE[0] * 2 / 3) / 2, 520)
            font = pg.font.Font(os.path.join(const.FONT_PATH, "VinerHandITC.ttf"), 60)
            text_surface = font.render("Manual", 1, pg.Color('black'))
            self.screen.blit(text_surface, text_surface.get_rect(
                center=(const.WINDOW_SIZE[0]/2, (const.WINDOW_SIZE[1] - const.HELPER_SIZE[1])/2 + 60)))
            font = pg.font.Font(None, 32)
            text_surface = font.render("F1: Mute/unmute the BGM", 1, pg.Color('black'))
            self.screen.blit(text_surface, text_position)
            text_position.y += 40
            text_surface = font.render("F2: Mute/unmute effect sounds", 1, pg.Color('black'))
            self.screen.blit(text_surface, text_position)

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
            detail = (item.vanish_time, item.ripple)
            objects.append(Object(coord[1], const.ObjectType.ITEM,
                                  item.render_position, item.type, detail))
        for player in model.players:
            coord = game_map.convert_coordinate(player.position)
            detail = (player.effect, player.dead, player.effect_timer, player.respawn_time - model.timer)
            # for kill_animation in self.ghost_kill_animations:
            #     if kill_animation[2] == player.player_id:
            #         detail = (kill_animation[3], player.dead, const.GAME_LENGTH)
            #         break
            objects.append(
                Object(coord[1], const.ObjectType.PLAYER, player.position, player.player_id, detail))
        for ghost in model.ghosts:
            coord = game_map.convert_coordinate(ghost.position)
            objects.append(
                Object(coord[1], const.ObjectType.GHOST, ghost.position, const.GhostIds.DEMENTOR, (ghost.ghost_id, )))
        for patronus in model.patronuses:
            coord = game_map.convert_coordinate(patronus.position)
            detail = (patronus.death_time, )
            objects.append(Object(coord[1], const.ObjectType.PATRONUS,
                                  patronus.position, None, detail))
        for portal in self.portkey_animation:
            coord = game_map.convert_coordinate(portal.position)
            detail = (portal, )
            objects.append(Object(coord[1], const.ObjectType.PORTAL, portal.position, None, detail))

        for row, image, position in self.background_images:
            objects.append(Object(row, const.ObjectType.MAP, pg.Vector2(position), None, (image,)))

        objects.sort(key=lambda x: x.y)
        # half_sec = model.timer // (const.FPS // 2)
        quarter_sec = model.timer // (const.FPS // 4)

        def render_picture(image_dic: dict, index, direction, obj):
            width = image_dic[index][direction].get_width()
            height = image_dic[index][direction].get_height()
            ul = [x - y for x, y in zip(obj.position, [width/2, height])]
            self.screen.blit(image_dic[index][direction], ul)
        
        for obj in objects:
            # ul means upper left
            if obj.object_type == const.ObjectType.PLAYER:
                direction = self.character_direction[obj.image_index]
                effect, dead, effect_timer, dead_time = obj.detail
                # if dead:
                #     if half_sec % 2 == 0:
                #         self.screen.blit(self.transparent_player_image[obj[2]], obj[3])
                #     else:
                #         self.screen.blit(self.pictures[obj[2]], obj[3])
                width = self.character_image[obj.image_index][direction].get_width()
                height = self.character_image[obj.image_index][direction].get_height()
                ul = [x - y for x, y in zip(obj.position, [width/2, height])]
                if dead:
                    if direction == const.CharacterDirection.DOWN or direction == const.CharacterDirection.UP:
                        render_picture(self.dead_player_image, obj.image_index, direction, obj)
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
                    angle = (dead_time / const.PLAYER_RESPAWN_TIME) * 2 * pi
                    radius = const.PLAYER_REVIVE_CIRCLE_RADIUS * 2
                    rect = pg.Rect((obj.position+pg.Vector2(0, -30)), (0, 0)).inflate(radius, radius)
                    pg.draw.arc(self.screen, const.PLAYER_COLOR[obj.image_index], rect, pi/2-angle, pi/2, width=6)
                elif effect_timer < const.ITEM_LOSE_EFFECT_HINT_TIME and quarter_sec % 2 == 0:
                    self.screen.blit(self.character_image[obj.image_index][direction], ul)
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
                    if kill_animation[0] == obj.detail[0]:
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
                if quarter_sec % 2 == 0 or model.timer + const.ITEM_LOSE_EFFECT_HINT_TIME <= effect_timer:
                    ul = [x - y for x, y in zip(obj.position,
                                                [const.PATRONUS_RADIUS, const.PATRONUS_RADIUS*2])]
                    self.screen.blit(self.shining_patronus, ul)
            elif obj.object_type == const.ObjectType.PORTAL:
                obj.detail[0].tick()
            elif obj.object_type == const.ObjectType.MAP:
                self.screen.blit(obj.detail[0], obj.position)
            elif obj.object_type == const.ObjectType.ITEM:
                # render ripple
                ripple = obj.detail[1]
                if ripple.show:
                    ripple_surface = pg.Surface(ripple.size, pg.SRCALPHA)
                    pg.draw.ellipse(ripple_surface, ripple.color, pg.Rect((0, 0), ripple.size), width=const.ITEM_RIPPLE_WIDTH)
                    self.screen.blit(ripple_surface, pg.Rect(ripple.position, (0, 0)).inflate(ripple.size))

                # render item
                ul = [x - y for x, y in zip(obj.position,
                                            [const.ITEM_RADIUS, const.ITEM_RADIUS*2])]
                # It's acually is a rectangle.
                # vanish_time = obj.detail[0]
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
            if effect.tick():
                self.petrification_animation.remove(animation)
                get_event_manager().post(EventPetrify(victim))
                continue
            for particle in effect.particles:
                pg.draw.circle(self.screen, particle.color, particle.position, particle.radius)
        
        # Patronus shockwave animation
        animations = self.patronus_shockwave_animations.copy()
        for animation in animations:
            position = animation[0]
            disappear_time = animation[1]
            duration = animation[2]
            if model.timer > disappear_time:
                self.patronus_shockwave_animations.remove(animation)
                continue
            for i in range(5):
                radius = const.PATRONUS_SHOCKWAVE_RADIUS * (1 - min(1, (disappear_time - model.timer + i) / duration))
                color = pg.Color(const.PATRONUS_SHOCKWAVE_COLOR)
                color.a = int(255 * (1 - radius / const.PATRONUS_SHOCKWAVE_RADIUS))
                pg.draw.circle(self.screen, color, position, radius=radius, width=1+i)


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
        kill_animations = self.ghost_kill_animations.copy()
        for kill_animation in kill_animations:
            if model.timer > kill_animation[4]:
                self.ghost_kill_animations.remove(kill_animation)

        self.portkey_animation = [x for x in self.portkey_animation if x.tick()]
        self.bleed_animations = [x for x in self.bleed_animations if x.tick()]

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

        # debug
        # AI target
        if model.show_ai_target:
            for i in range(4):
                target = get_last_target(i)
                if target is None:
                    continue
                source = model.players[i].position
                target = util.move_point_in_arena(source, Vector2(target))
                pg.draw.line(self.screen, const.PLAYER_COLOR[i], target, source, 5)
                pg.draw.circle(self.screen, const.PLAYER_COLOR[i], target, 10)
                pg.draw.circle(self.screen, "#000000", target, 10, 3)

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


class GIFAnimation:
    def __init__(self, screen, position: pg.Vector2, animation_image: list[pg.Surface], image_duration, delay: int = 0):
        self.screen = screen
        self.animation_image = animation_image
        self.animation_length = len(animation_image)
        self.image_duration = image_duration
        self.position = position.copy()
        self.delay = delay
        self.animation_index = 0
        self.animation_life = 0

    def tick(self):
        if self.delay > 0:
            self.delay -= 1
            return True
        image = self.animation_image[self.animation_index]
        rect = pg.Rect(self.position, (0, 0)).inflate(image.get_size())
        self.screen.blit(image, rect)
        self.animation_life += 1
        if self.animation_life == self.image_duration:
            self.animation_index += 1
            self.animation_life = 0
        return self.animation_index < self.animation_length


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
