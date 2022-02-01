import logging
import time

from fishy.engine import SemiFisherEngine
from fishy.engine.fullautofisher.engine import FullAuto


# to test only gui without engine code interfering
class IEngineHandler:
    def __init__(self):
        ...

    def start_event_handler(self):
        ...

    def toggle_semifisher(self):
        ...

    def toggle_fullfisher(self):
        ...

    def check_pixel_val(self):
        ...

    def quit(self):
        ...


class EngineEventHandler(IEngineHandler):
    def __init__(self, gui_ref):
        super().__init__()
        self.event_handler_running = True
        self.event = []

        self.semi_fisher_engine = SemiFisherEngine(gui_ref)
        self.full_fisher_engine = FullAuto(gui_ref)

    def start_event_handler(self):
        while self.event_handler_running:
            while len(self.event) > 0:
                event = self.event.pop(0)
                event()
            time.sleep(0.1)

    def toggle_semifisher(self):
        self.event.append(self.semi_fisher_engine.toggle_start)

    def toggle_fullfisher(self):
        self.event.append(self.full_fisher_engine.toggle_start)

    def check_pixel_val(self):
        def func():
            if self.semi_fisher_engine.start:
                self.semi_fisher_engine.show_pixel_vals()
            else:
                logging.debug("Start the engine first before running this command")

        self.event.append(func)

    def quit(self):
        def func():
            if self.semi_fisher_engine.start:
                self.semi_fisher_engine.turn_off()
            if self.full_fisher_engine.start:
                self.semi_fisher_engine.turn_off()

            self.event_handler_running = False

        self.event.append(func)
