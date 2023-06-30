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
