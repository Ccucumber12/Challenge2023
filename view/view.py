import os
import cv2

import pygame as pg
from pygame import Vector2
from math import pi

import const
import view.objects as view_objects
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

    def __init__(self, r18g, player_names):
        model = get_game_engine()
        """
        This function is called when the GraphicalView is created.
        For more specific objects related to a game instance
            , they should be initialized in GraphicalView.initialize()
        """
        self.r18g = r18g
        self.player_names = player_names
        self.register_listeners()

        self.show_helper = False

        # optimization

        self.screen = pg.display.set_mode(size=const.WINDOW_SIZE, flags=pg.DOUBLEBUF)
        pg.display.set_caption(const.WINDOW_CAPTION)
        self.background.fill(const.BACKGROUND_COLOR)

        # animations
        self.ghost_teleport_chanting_animations: list[GatheringParticleEffect] = []
        self.petrification_animation: list[CastMagicParticleEffect] = []
        self.patronus_shockwave_animations = []
        self.sortinghat_animations = []
        self.ghost_kill_animations = {}

        # scale the pictures to proper size
        self.pictures = {}
        self.character_image = {}
        self.petrified_player_image = {}
        self.transparent_player_image = {}
        self.wearing_sortinghat_image = {}
        self.shining_player_image = {}
        self.dead_player_image = {}
        self.sortinghat_animation_picture = []
        self.magic_circle: pg.Surface
        self.portkey_animation_image: list[pg.Surface] = []
        self.portkey_animation: list[GIFAnimation] = []
        self.bleed_animation_images: list[pg.Surface] = []
        self.bleed_animations: list[GIFAnimation] = []
        self.golden_snitch_animations: list[GSAnimation] = []
        self.coordinate_unit = 0 # it won't show the coordinate if the variable is set to zero

        self.background_images = []
        for i in model.map.images:
            loaded_image = cv2.imread(os.path.join(model.map.map_dir, i), cv2.IMREAD_UNCHANGED)
            loaded_image = cv2.resize(loaded_image, const.ARENA_SIZE, interpolation=cv2.INTER_AREA)
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            picture = pg.transform.scale(picture, const.ARENA_SIZE)
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            self.background_images.append((int(model.map.images[i]), picture, (x, y)))

        picture = pg.image.load(const.PICTURES_PATH[const.Scene.TITLE]).convert_alpha()
        self.pictures[const.Scene.TITLE] = util.crop_image(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.Scene.FOG]).convert_alpha()
        picture.set_alpha(const.FOG_TRANSPARENCY)
        self.pictures[const.Scene.FOG] = util.crop_image(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.Scene.ENDGAME]).convert_alpha()
        self.pictures[const.Scene.ENDGAME] = util.crop_image(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        self.fog = Fog(self.screen, self.pictures[const.Scene.FOG], const.FOG_SPEED)
        # print(self.pictures[const.SCENE.FOG].get_width())
        # print(self.pictures[const.SCENE.FOG].get_height())

        picture = pg.image.load(
            const.PICTURES_PATH[const.OtherPictures.MAGIC_CIRCLE]).convert_alpha()
        self.magic_circle = util.crop_image(
            picture, const.MAGIC_CIRCLE_RADIUS*2, const.MAGIC_CIRCLE_RADIUS*2, True)
        self.magic_circle.set_alpha(127)
        picture = pg.image.load(const.PICTURES_PATH[const.ItemType.SORTINGHAT]).convert_alpha()
        self.sortinghat_animation_picture.append(
            util.crop_image(picture, const.ITEM_RADIUS, const.ITEM_RADIUS))

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

        # Objects and animations should be initialized after pygame is initialized.
        # Therefore, they should be created in initialize() instead of __init__().
        self.scoreboard = view_objects.ScoreBoard()
        self.players = [view_objects.Player(player) for player in model.players]

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
        model = get_game_engine()
        if model.players[event.player_id].effect == const.EffectType.PETRIFICATION:
            return
        for player in self.players:
            if player.player.player_id == event.player_id:
                break
        player.update_face_dir()

    def handle_ghost_kill(self, event: EventGhostKill):
        self.ghost_kill_animations[event.ghost_id] = (event.destination, event.victim_id, event.victim_effect,
                                           get_game_engine().timer + const.GHOST_KILL_ANIMATION_TIME)

    def handle_portkey(self, event: EventPortkey):
        self.portkey_animation.append(GIFAnimation(self.screen, event.destination,
                                             self.portkey_animation_image, int(const.FPS / 3)))

    def handle_get_golden_snitch(self, event: EventGetGoldenSnitch):
        self.screen_copy = self.screen.copy()
        self.golden_snitch_animations.append(
            GSAnimation(
                self.screen,
                event.item_pos,
                event.player_id,
                view_objects.Item.images[const.ItemType.GOLDEN_SNITCH],
            )
        )

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
        ev_manager.register_listener(EventShowCoordinate, self.handle_show_coordinate)
        ev_manager.register_listener(EventGetGoldenSnitch, self.handle_get_golden_snitch)

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

    def handle_show_coordinate(self, event: EventShowCoordinate):
        if self.coordinate_unit == 0:
            self.coordinate_unit = event.unit
        else:
            self.coordinate_unit = 0

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
            text_position.y += 40
            text_surface = font.render("F3: Show/hide the coordinate (default interval: 25)", 1, pg.Color('black'))
            self.screen.blit(text_surface, text_position)

        pg.display.flip()

    def render_play(self):
        model = get_game_engine()
        if model.forced_paused:
            self.screen.blit(self.screen_copy, (0, 0))
            self.golden_snitch_animations = [x for x in self.golden_snitch_animations if x.tick()]
            if len(self.golden_snitch_animations) == 0:
                get_event_manager().post(EventContinueModel())
            pg.display.flip()
            return

        self.screen.fill(const.BACKGROUND_COLOR)
        game_map = model.map

        objects = []
        objects += self.players
        objects += [view_objects.Item(item) for item in model.items]
        objects += [view_objects.Ghost(ghost) for ghost in model.ghosts]
        objects += [view_objects.Patronus(patronus) for patronus in model.patronuses]

        for portal in self.portkey_animation:
            coord = game_map.convert_coordinate(portal.position)
            detail = (portal, )
            objects.append(Object(coord[1], const.ObjectType.PORTAL, portal.position, None, detail))

        for row, image, position in self.background_images:
            objects.append(Object(row, const.ObjectType.MAP, pg.Vector2(position), None, (image,)))

        objects.sort(key=lambda x: x.y)
        for obj in objects:
            if isinstance(obj, view_objects.Item):
                obj.draw(self.screen)
            elif isinstance(obj, view_objects.Player):
                obj.draw(self.screen)
            elif isinstance(obj, view_objects.Ghost):
                obj.draw(self.screen, self.ghost_kill_animations)
            elif isinstance(obj, view_objects.Patronus):
                obj.draw(self.screen)

            elif obj.object_type == const.ObjectType.PORTAL:
                obj.detail[0].tick()
            elif obj.object_type == const.ObjectType.MAP:
                self.screen.blit(obj.detail[0], obj.position)

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
        for k, v in kill_animations.items():
            if model.timer > v[3]:
                del self.ghost_kill_animations[k]

        self.portkey_animation = [x for x in self.portkey_animation if x.tick()]
        self.bleed_animations = [x for x in self.bleed_animations if x.tick()]

        # Fog
        self.fog.tick()

        # Scoreboard
        self.scoreboard.draw(self.screen)

        def print_text(text, position, font="magic-school.one.ttf", size=36):
            font = pg.font.Font(os.path.join(const.FONT_PATH, font), size)
            text_surface = font.render(str(text), True, pg.Color('black'))
            self.screen.blit(text_surface, text_surface.get_rect(center=position))
        # Name
        for i in range(const.NUM_OF_PLAYERS):
            print_text(self.player_names[i], const.NAME_POSITION[i], "VinerHandITC.ttf", 20)
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

        # Coordinate
        if self.coordinate_unit != 0:
            z = 0
            while z < const.ARENA_SIZE[0]:
                if z % 400 == 0:
                    pg.draw.line(self.screen, "white", (z, 0), (z, const.ARENA_SIZE[1]-1), 1)
                elif z % 100 == 0:
                    pg.draw.line(self.screen, "black", (z, 0), (z, const.ARENA_SIZE[1]-1), 1)
                else:
                    pg.draw.line(self.screen, "gold", (z, 0), (z, const.ARENA_SIZE[1]-1), 1)
                z += self.coordinate_unit
            z = 0
            while z < const.ARENA_SIZE[1]:
                if z % 400 == 0:
                    pg.draw.line(self.screen, "white", (0, z), (const.ARENA_SIZE[0]-1, z), 1)
                elif z % 100 == 0:
                    pg.draw.line(self.screen, "black", (0, z), (const.ARENA_SIZE[0]-1, z), 1)
                else:
                    pg.draw.line(self.screen, "gold", (0, z), (const.ARENA_SIZE[0]-1, z), 1)
                z += self.coordinate_unit

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


class GSAnimation:
    def __init__(self, screen, item_pos, player_id, pic):
        self.start_pos = item_pos
        self.end_pos = const.SCORE_POSITION[player_id][2]
        self.middle_pos = (int(self.start_pos[0] - 0.2*(self.end_pos[0]-self.start_pos[0])), int((self.start_pos[0]+self.end_pos[0])/2)+20)
        self.now_tick = 0
        self.screen = screen
        self.pic = pic

    def get_B_curve_pos(self, tick):
        # Quadratic Bézier curves
        # B(t) = (1-t)[(1-t)P0 + tP1] + t[(1-t)P1 + tP2]
        length = const.GOLDEN_SNITCH_ANIMATION_LENGTH
        P = (self.start_pos, self.middle_pos, self.end_pos)
        t = tick / length
        x = (1-t)*((1-t)*P[0][0] + t*P[1][0]) + t*((1-t)*P[1][0] + t*P[2][0])
        y = (1-t)*((1-t)*P[0][1] + t*P[1][1]) + t*((1-t)*P[1][1] + t*P[2][1])
        return x, y
    
    def tick(self):
        if self.now_tick > const.GOLDEN_SNITCH_ANIMATION_LENGTH*2//3:
            self.now_tick += 2
        if self.now_tick > const.GOLDEN_SNITCH_ANIMATION_LENGTH//3:
            self.now_tick += 1.5
        else:
            self.now_tick += 1
        if self.now_tick >= const.GOLDEN_SNITCH_ANIMATION_LENGTH:
            return False
        self.screen.blit(self.pic, self.pic.get_rect(center=self.get_B_curve_pos(self.now_tick)))
        return True
