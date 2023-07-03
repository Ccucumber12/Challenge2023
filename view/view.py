import math
import os
import random

import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager, get_game_engine
from view.particle import GatheringParticleEffect
from view.particle import CastMagicParticleEffect


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

        # animations
        self.ghost_teleport_chanting_animations: list[GatheringParticleEffect] = []
        self.petrification_animation: list[CastMagicParticleEffect] = []
        self.sortinghat_animations = []

        # scale the pictures to proper size
        self.pictures = {}
        self.grayscale_image = {}
        self.transparent_image = {}
        self.sortinghat_animation_pictures = []
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
        for item in const.ITEM_SET:
            picture = pg.image.load(const.PICTURES_PATH[item]).convert_alpha()
            self.pictures[item] = crop(picture, const.ITEM_WIDTH, const.ITEM_HEIGHT, True)
            self.transparent_image[item] = self.pictures[item].convert_alpha()
            self.transparent_image[item].set_alpha(const.NEAR_VANISH_TRANSPARENCY)
        for player in const.PLAYER_IDS:
            picture = pg.image.load(const.PICTURES_PATH[player]).convert_alpha()
            self.pictures[player] = crop(picture, const.PLAYER_RADIUS*2, const.PLAYER_RADIUS*2, True)
            # grayscale
            self.grayscale_image[player] = pg.transform.grayscale(self.pictures[player])
            # transparent
            self.transparent_image[player] = self.pictures[player].convert_alpha()
            self.transparent_image[player].set_alpha(const.CLOAK_TRANSPARENCY)
        for ghost in const.GHOST_IDS:
            picture = pg.image.load(const.PICTURES_PATH[ghost]).convert_alpha()
            self.pictures[ghost] = crop(picture, const.GHOST_RADIUS*2, const.GHOST_RADIUS*2, True)

        
        self.background_images = []
        for i in model.map.images:
            loaded_image = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            loaded_image = pg.transform.scale(loaded_image, const.ARENA_SIZE)
            self.background_images.append((int(model.map.images[i]), loaded_image))

        picture = pg.image.load(const.PICTURES_PATH[const.SCENE.SCORE_BOARD]).convert_alpha()
        self.pictures[const.SCENE.SCORE_BOARD] = crop(
            picture, const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.SCENE.TITLE]).convert_alpha()
        self.pictures[const.SCENE.TITLE] = crop(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        picture = pg.image.load(const.PICTURES_PATH[const.SCENE.FOG]).convert_alpha()
        picture.set_alpha(const.FOG_TRANSPARENCY)
        self.pictures[const.SCENE.FOG] = crop(
            picture, 2*const.ARENA_SIZE[0], const.ARENA_SIZE[1])
        self.fog = Fog(self.screen, self.pictures[const.SCENE.FOG], const.FOG_SPEED)
        # print(self.pictures[const.SCENE.FOG].get_width())
        # print(self.pictures[const.SCENE.FOG].get_height())

        # Animation
        picture = pg.image.load(const.PICTURES_PATH[const.OTEHR_PICTURES.PATRONUS]).convert_alpha()
        self.shining_patronus = crop(picture, const.PATRONUS_RADIUS*2, const.PATRONUS_RADIUS*2, True)
        picture = pg.image.load(const.PICTURES_PATH[const.OTEHR_PICTURES.MAGIC_CIRCLE]).convert_alpha()
        self.magic_circle = crop(picture, const.MAGIC_CIRCLE_RADIUS*2, const.MAGIC_CIRCLE_RADIUS*2, True)
        self.magic_circle.set_alpha(127)
        picture = pg.image.load(const.PICTURES_PATH[const.ITEM_SET.SORTINGHAT]).convert_alpha()
        self.sortinghat_animation_pictures.append(crop(picture, 0.5*const.ITEM_WIDTH, 0.5*const.ITEM_HEIGHT))

        angle = 0
        while angle < 360:
            angle += const.SORTINGHAT_ANIMATION_ROTATE_SPEED / const.FPS
            self.sortinghat_animation_pictures.append(
                pg.transform.rotate(self.sortinghat_animation_pictures[0], angle))

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

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventGhostTeleport, self.add_ghost_teleport_chanting_animation)
        ev_manager.register_listener(EventCastPetrification, self.add_cast_petrification_animation)
        ev_manager.register_listener(EventSortinghat, self.add_sortinghat_animation)

    def display_fps(self):
        """
        Display the current fps on the window caption.
        """
        model = get_game_engine()
        pg.display.set_caption(f'{const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')
    
    def add_ghost_teleport_chanting_animation(self, event):
        model = get_game_engine()
        self.ghost_teleport_chanting_animations.append((
            GatheringParticleEffect(event.position, const.GHOST_CHANTING_TIME + model.timer, const.GHOST_CHANTING_COLOR), event.destination))
    
    def add_cast_petrification_animation(self, event):
        self.petrification_animation.append((
            CastMagicParticleEffect(event.attacker, event.victim, const.PETRIFICATION_ANIMATION_SPEED, const.PETRIFICATION_ANIMATION_COLOR, const.PETRIFICATION_ANIMATION_THICKNESS), event.victim))
        

    def add_sortinghat_animation(self, event):
        model = get_game_engine()
        position = model.players[event.assailant.value].position
        victim = event.victim
        self.sortinghat_animations.append((position, victim, 0))
    
    def get_ul(self, center: list, size: list):
        """
        get the upper left of a image.
        """
        ul = [x - y for x, y in zip(center, [const.ITEM_WIDTH/2, const.ITEM_HEIGHT/2])]
        return ul

    def render_menu(self):
        # draw background
        # self.screen.fill(Const.BACKGROUND_COLOR)
        self.screen.blit(self.pictures[const.SCENE.TITLE],
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
        objects = []
        for item in model.items:
            center = list(map(int, item.position))
            ul = [x - y for x, y in zip(center, [const.ITEM_WIDTH/2, const.ITEM_HEIGHT/2])]
            coord = game_map.convert_coordinate(item.position)
            objects.append((coord[1], const.OBJECT_TYPE.ITEM, item.type, ul, item.vanish_time))
        for player in model.players:
            center = list(map(int, player.position))
            ul = [x - y for x, y in zip(center, [const.PLAYER_RADIUS, const.PLAYER_RADIUS*2])]
            coord = game_map.convert_coordinate(player.position)
            objects.append((coord[1], const.OBJECT_TYPE.PLAYER,
                           player.player_id, ul, player.effect, player.dead))
        for ghost in model.ghosts:
            center = list(map(int, ghost.position))
            ul = [x - y for x, y in zip(center, [const.GHOST_RADIUS, const.GHOST_RADIUS*2])]
            coord = game_map.convert_coordinate(ghost.position)
            objects.append((coord[1], const.OBJECT_TYPE.GHOST, ghost.ghost_id, ul))
        for patronus in model.patronuses:
            center = list(map(int, patronus.position))
            ul = [x - y for x, y in zip(center, [const.PATRONUS_RADIUS, const.PATRONUS_RADIUS*2])]
            coord = game_map.convert_coordinate(patronus.position)
            objects.append((coord[1], const.OBJECT_TYPE.PATRONUS, patronus.patronus_id, ul))

        for row, image in self.background_images:
            objects.append((row, const.OBJECT_TYPE.MAP, image))

        objects.sort(key=lambda x: (x[0], x[1]))
        half_sec = model.timer // (const.FPS // 2)
        for obj in objects:
            if obj[1] == const.OBJECT_TYPE.PLAYER:
                if obj[5]:
                    if half_sec % 2 == 0:
                        self.screen.blit(self.transparent_image[obj[2]], obj[3])
                    else:
                        self.screen.blit(self.pictures[obj[2]], obj[3])
                elif obj[4] == const.ITEM_SET.PETRIFICATION:
                    self.screen.blit(self.grayscale_image[obj[2]], obj[3])
                elif obj[4] == const.ITEM_SET.CLOAK:
                    self.screen.blit(self.transparent_image[obj[2]], obj[3])
                else:
                    self.screen.blit(self.pictures[obj[2]], obj[3])
            elif obj[1] == const.OBJECT_TYPE.GHOST:
                self.screen.blit(self.pictures[const.GHOST_IDS.DEMENTOR], obj[3])
            elif obj[1] == const.OBJECT_TYPE.PATRONUS:
                self.screen.blit(self.shining_patronus, obj[3])
            elif obj[1] == const.OBJECT_TYPE.MAP:
                self.screen.blit(obj[2], (0, 0))
            elif obj[1] == const.OBJECT_TYPE.ITEM:
                # It's acually is a rectangle.
                if half_sec % 2 == 0 or model.timer + 5*const.FPS < obj[4]:
                    self.screen.blit(self.pictures[obj[2]], obj[3])
                else:
                    self.screen.blit(self.transparent_image[obj[2]], obj[3])

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
            ul = [x - y for x, y in zip(destination, [const.MAGIC_CIRCLE_RADIUS, const.MAGIC_CIRCLE_RADIUS])]
            self.screen.blit(self.magic_circle, ul)
        
        # Cast petrification animation
        animations = self.petrification_animation.copy()
        for animation in animations:
            effect = animation[0]
            victim = animation[1]
            if effect.tick() == True:
                self.petrification_animation.remove(animation)
                victim.set_effect(const.ITEM_SET.PETRIFICATION)
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
            self.screen.blit(self.sortinghat_animation_pictures[index], position)
            index += 1
            if index == len(self.sortinghat_animation_pictures):
                index = 0
            position = position + \
                (destination-position).normalize() * const.SORTINGHAT_ANIMATION_SPEED / const.FPS
            self.sortinghat_animations.append((position, victim, index))

        # Fog
        self.fog.tick()

        # Scoreboard
        self.screen.blit(self.pictures[const.SCENE.SCORE_BOARD], (const.ARENA_SIZE[0], 0))

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
        self.screen.fill(const.BACKGROUND_COLOR)

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
            self.position = self.position + pg.Vector2(0, -self.speed/const.FPS)
            if self.position.y <= 0:
                self.position.y = 0
                self.raising = False
        self.screen.blit(self.picture, self.position)
        self.screen.blit(self.picture, self.position - pg.Vector2(const.FOG_SIZE[0], 0))
        self.position = self.position + pg.Vector2(self.speed/const.FPS, 0)
        if self.position.x > const.WINDOW_SIZE[0]:
            self.position.x -= const.FOG_SIZE[0]
