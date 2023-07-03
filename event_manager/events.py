import pygame as pg

import const
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


class EventEveryTick(BaseEvent):
    name = 'Tick event'


class EventTimesUp(BaseEvent):
    name = "Time's Up event"


class EventPlayerMove(BaseEvent):
    name = 'PlayerMove event'

    def __init__(self, player_id: int, direction):
        super().__init__()
        self.player_id = player_id
        self.direction = direction

    def __str__(self):
        return f'{self.name} => player_id {self.player_id} move {self.direction}'


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

class EventGhostTeleport(BaseEvent):
    name = 'GhostTeleport event'

    def __init__(self, ghost_id, position: pg.Vector2, destination: pg.Vector2):
        super().__init__()
        self.ghost_id = ghost_id
        self.position = position
        self.destination = destination

    def __str__(self):
        return f'{self.name} => ghost_id {self.ghost_id} teleport from {self.position} to {self.destination}'

class EventSortinghat(BaseEvent):
    name = 'Sortinghat event'

    def __init__(self, assailant: const.PLAYER_IDS, victim: const.PLAYER_IDS):
        super().__init__()
        self.assailant = assailant
        self.victim = victim

    def __str__(self):
        return f'{self.name} => Sorthinghat fly from {self.assailant} to {self.victim}'

class EventMuteMusic(BaseEvent):
    name = 'MuteMusic event'