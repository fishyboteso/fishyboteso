import logging
import time

from fishy.engine.IEngine import IEngine


class FullAuto(IEngine):
    def run(self):
        self.gui.bot_started(True)
        while self.start:
            logging.debug("running full auto")
            time.sleep(0.5)
        self.gui.bot_started(False)
