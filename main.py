import argparse
import os
import platform

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame as pg
del os.environ['PYGAME_HIDE_SUPPORT_PROMPT']

import const
import event_manager.events
import instances_manager
from controller.controller import Controller
from event_manager.event_manager import EventManager
from model.model import GameEngine
from sound.sound import BackGroundMusic
from view.view import GraphicalView


def main():
    # Initialization
    pg.init()

    if platform.system() == 'Windows':
        # On Windows, the monitor scaling can be set to something besides normal 100%.
        # PyScreeze and Pillow needs to account for this to make accurate screenshots.
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass  # Windows XP doesn't support monitor scaling, so just do nothing.

    # Argument parser
    parser = argparse.ArgumentParser(prog='Challenge2023')
    parser.add_argument(
        'map', help='The name of tmaps. It can be snow, azkaban or river(for test)')
    parser.add_argument('ai1', nargs='?', default='manual')
    parser.add_argument('ai2', nargs='?', default='manual')
    parser.add_argument('ai3', nargs='?', default='manual')
    parser.add_argument('ai4', nargs='?', default='manual')
    parser.add_argument('-m', '--mute', action='store_true', help='mute the BGM')
    parser.add_argument('-s', '--show-ai-target', action='store_true',
                        help='show returned positions of AIs')
    parser.add_argument('-n', '--no-error-message', action='store_true',
                        help='disable the traceback message')
    parser.add_argument('-r', '--r18g', action='store_true', help='add some violent taste...')
    parser.add_argument('-c', '--coordinate', type=int, 
                        help='set the interval of the coordinate and show it when playing (can be canceled using F3)')
    args = parser.parse_args()

    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    instances_manager.register_event_manager(ev_manager)
    model = GameEngine(args.map, [args.ai1, args.ai2, args.ai3, args.ai4],
                       args.show_ai_target, args.no_error_message)
    instances_manager.register_game_engine(model)
    Controller()
    GraphicalView(args.r18g)
    if not args.mute:
        BackGroundMusic()

    if args.coordinate is not None:
        const.COORDINATE_UNIT = args.coordinate
        ev_manager.post(event_manager.events.EventShowCoordinate(args.coordinate))

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
