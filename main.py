import sys

import pygame as pg

import instances_manager
from controller.controller import Controller
from event_manager.event_manager import EventManager
from model.model import GameEngine
from view.view import GraphicalView
from sound.sound import BackGroundMusic


def main():
    # Initialization
    pg.init()

    if sys.platform == 'win32':
        # On Windows, the monitor scaling can be set to something besides normal 100%.
        # PyScreeze and Pillow needs to account for this to make accurate screenshots.
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass # Windows XP doesn't support monitor scaling, so just do nothing.

    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)
    model = GameEngine()
    instances_manager.register_game_engine(model)
    Controller()
    GraphicalView()
    BackGroundMusic()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
