import logging
from fishy.engine import SemiFisherEngine
from fishy.engine.fullautofisher.engine import FullAuto


class EngineEventHandler:
    def __init__(self, config, gui_ref):
        self.event_handler_running = True
        self.event = []

        self.semi_fisher_engine = SemiFisherEngine(config, gui_ref)
        self.full_fisher_engine = FullAuto(config, gui_ref)

    def start_event_handler(self):
        while self.event_handler_running:
            while len(self.event) > 0:
                event = self.event.pop(0)
                event()

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
            self.semi_fisher_engine.start = False
            self.event_handler_running = False

        self.event.append(func)
