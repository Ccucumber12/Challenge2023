import pygame as pg

import const
import instances_manager
from event_manager.event_manager import BaseEvent


class EventInitialize(BaseEvent):
    name = 'Initialize event'


class EventQuit(BaseEvent):
    name = 'Quit event'


class EventStateChange(BaseEvent):
    name = 'StateChange event'

    def __init__(self, state):
        super().__init__()
        self.state = state

    def __str__(self):
        return f'{self.name} => StateTo: {self.state}'

class EventHelpMenu(BaseEvent):
    name = 'HelpMenu Event'

    def __init__(self):
        pass

    def __str__(self):
        return f'Show help menu'


class EventEveryTick(BaseEvent):
    name = 'Tick event'


class EventTimesUp(BaseEvent):
    name = "Time's Up event"

    def __init__(self, places):
        super().__init__
        self.places = places


class EventPlayerMove(BaseEvent):
    name = 'PlayerMove event'

    def __init__(self, player_id, direction: pg.Vector2, full_length: bool = False):
        super().__init__()
        self.player_id = player_id
        if full_length:
            player = instances_manager.get_game_engine().players[player_id]
            direction = direction.normalize() * player.speed
        self.direction = direction

    def __str__(self):
        return f'{self.name} => player_id {self.player_id} move {self.direction}'


class EventPlayerGetItem(BaseEvent):
    name = 'PlayerGetItem event'

    def __init__(self, player_id, effect_type: const.EffectType):
        super().__init__()
        self.player_id = player_id
        self.effect_type = effect_type

    def __str__(self):
        return f'{self.name} => player_id {self.player_id} get {self.effect_type}'


class EventPortkey:
    name = 'Portkey event'
    
    def __init__(self, destination):
        super().__init__()
        self.destination = destination


class EventGhostMove(BaseEvent):
    name = 'GhostMove event'

    def __init__(self, ghost_id, direction):
        super().__init__()
        self.ghost_id = ghost_id
        self.direction = direction

    def __str__(self):
        return f'{self.name} => ghost_id {self.ghost_id} move {self.direction}'


class EventCastPetrification(BaseEvent):
    name = 'Cast petrification event'

    def __init__(self, attacker, victim):
        super().__init__()
        self.attacker = attacker
        self.victim = victim

    def __str__(self):
        return f'{self.name} => {self.attacker.player_id} cast petrification against {self.victim.player_id}'


class EventPetrify(BaseEvent):
    name = 'Petrify event'

    def __init__(self, victim):
        from model.character import Player
        super().__init__()
        self.victim: Player = victim

    def __str__(self):
        return f'{self.name} => {self.victim.player_id} is petrified'


class EventGhostTeleportChant(BaseEvent):
    name = 'GhostTeleportChant event'

    def __init__(self, ghost_id, position: pg.Vector2, destination: pg.Vector2):
        super().__init__()
        self.ghost_id = ghost_id
        self.position = position
        self.destination = destination

    def __str__(self):
        return f'{self.name} => ghost_id {self.ghost_id} start chatting and will teleport from {self.position} to {self.destination}'


class EventGhostTeleport(BaseEvent):
    name = 'GhostTeleport event'

    def __init__(self, ghost_id, position: pg.Vector2, destination: pg.Vector2):
        super().__init__()
        self.ghost_id = ghost_id
        self.position = position
        self.destination = destination

    def __str__(self):
        return f'{self.name} => ghost_id {self.ghost_id} teleport from {self.position} to {self.destination}'


class EventPatronusShockwave(BaseEvent):
    name = 'Patronus shockwave event'

    def __init__(self, position: pg.Vector2):
        super().__init__()
        self.position = position

    def __str__(self):
        return f'{self.name} => shockwave occurred at {self.position}'

class EventSortinghat(BaseEvent):
    name = 'Sortinghat event'

    def __init__(self, assailant: const.PlayerIds, victim: const.PlayerIds):
        super().__init__()
        self.assailant = assailant
        self.victim = victim

    def __str__(self):
        return f'{self.name} => Sorthinghat fly from {self.assailant} to {self.victim}'


class EventGhostKill(BaseEvent):
    name = 'GhostKill event'

    def __init__(self, ghost_id, victim_position: pg.Vector2, victim_id = 'Patronus', victim_effect = None):
        super().__init__()
        self.ghost_id = ghost_id
        self.victim_id = victim_id
        self.destination = victim_position
        self.victim_effect = victim_effect

class EventMuteMusic(BaseEvent):
    name = 'MuteMusic event'

    def __init__(self, type):
        super().__init__()
        self.type = type
