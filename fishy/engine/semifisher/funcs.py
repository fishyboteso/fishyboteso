import logging
from threading import Thread


# noinspection PyProtectedMember
class SemiFisherFuncs:
    def __init__(self, engine):
        self.engine = engine

    def start_button_pressed(self, *params):
        def func():
            self.engine.start = not self.engine.start
            if self.engine.start:
                self.engine.fishy_thread = Thread(target=self.engine.start_fishing, args=(*params,))
                self.engine.fishy_thread.start()

        self.engine.gui_events.append(func)

    def check_pixel_val(self):
        def func():
            if self.engine.start:
                self.engine._show_pixel_vals()
            else:
                logging.debug("Start the engine first before running this command")

        self.engine.gui_events.append(func)

    def quit(self):
        def func():
            self.engine.start = False
            self.engine.event_handler_running = False

        self.engine.gui_events.append(func)
