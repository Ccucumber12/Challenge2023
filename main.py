import pygame as pg

import InstancesManager
from Controller.Controller import Controller
from EventManager.EventManager import EventManager
from Model.Model import GameEngine
from View.View import GraphicalView


def main():
    # Initialization
    pg.init()

    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    InstancesManager.register_event_manager(ev_manager)
    model = GameEngine()
    InstancesManager.register_game_engine(model)
    Controller()
    GraphicalView()

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
