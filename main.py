import pygame as pg

from EventManager.EventManager import EventManager
from Model.Model import GameEngine
from Controller.Controller import Controller
from View.View import GraphicalView

def main():
    # Initialization
    pg.init()
    
    # EventManager listen to events and notice model, controller, view
    ev_manager = EventManager()
    model      = GameEngine(ev_manager)
    controller = Controller(ev_manager, model)
    view       = GraphicalView(ev_manager, model)

    # Main loop
    model.run()


if __name__ == "__main__":
    main()
