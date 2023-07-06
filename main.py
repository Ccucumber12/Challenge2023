import argparse
import sys

import pygame as pg

import instances_manager
from controller.controller import Controller
from event_manager.event_manager import EventManager
from model.model import GameEngine
from sound.sound import BackGroundMusic
from view.view import GraphicalView


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
            pass  # Windows XP doesn't support monitor scaling, so just do nothing.

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    parser.add_argument('map')
    parser.add_argument('ai1', nargs='?', default='manual')
    parser.add_argument('ai2', nargs='?', default='manual')
    parser.add_argument('ai3', nargs='?', default='manual')
    parser.add_argument('ai4', nargs='?', default='manual')
    args = parser.parse_args()

    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)
    model = GameEngine(args.map, [args.ai1, args.ai2, args.ai3, args.ai4])
    instances_manager.register_game_engine(model)
    Controller()
    GraphicalView()
    BackGroundMusic()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
