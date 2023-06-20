__event_manager = None
__game_engine = None
__graphical_view = None


def register_event_manager(event_manager):
    global __event_manager
    __event_manager = event_manager


def get_event_manager():
    return __event_manager


def register_game_engine(game_engine):
    global __game_engine
    __game_engine = game_engine


def get_game_engine():
    return __game_engine


def register_graphical_view(graphical_view):
    global __graphical_view
    __graphical_view = graphical_view


def get_graphical_view():
    return __graphical_view
