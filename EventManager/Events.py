from EventManager.EventManager import BaseEvent


class EventInitialize(BaseEvent):
    name = 'Initialize event'


class EventQuit(BaseEvent):
    name = 'Quit event'


class EventStateChange(BaseEvent):
    name = 'StateChange event'

    def __init__(self, state):
        self.state = state

    def __str__(self):
        return f'{self.name} => StateTo: {self.state}'


class EventEveryTick(BaseEvent):
    name = 'Tick event'


class EventTimesUp(BaseEvent):
    name = "Time's Up event"


class EventPlayerMove(BaseEvent):
    name = 'PlayerMove event'

    def __init__(self, player_id, direction):
        self.player_id = player_id
        self.direction = direction

    def __str__(self):
        return f'{self.name} => player_id {self.player_id} move {self.direction}'


class EventGhostMove(BaseEvent):
    name = 'GhostMove event'

    def __init__(self, ghost_id, direction):
        self.ghost_id = ghost_id
        self.direction = direction
    def __str__(self):
        return f'{self.name} => ghost_id {self.ghost_id} move {self.direction}'
