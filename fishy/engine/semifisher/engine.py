import logging
import time
import typing
from threading import Thread
from typing import Callable, Optional

from fishy.engine.common import qr_detection

from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.engine.common.IEngine import IEngine
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_event, fishing_mode
from fishy.engine.semifisher.fishing_event import FishEvent
from fishy.helper.helper import print_exc

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class SemiFisherEngine(IEngine):
    def __init__(self, gui_ref: Optional['Callable[[], GUI]']):
        super().__init__(gui_ref)
        self.window = None
        self.values = None
        self.name = "SemiFisher"
        self.first_loop_done = False

    def run(self):
        """
        Starts the fishing
        code explained in comments in detail
        """
        if self.get_gui:
            logging.info("Starting the bot engine, look at the fishing hole to start fishing")
            Thread(target=self._wait_and_check).start()

        time.sleep(0.2)

        fishing_event.init()
        # noinspection PyBroadException
        try:
            self._engine_loop()
        except Exception:
            logging.error("exception occurred while running engine loop")
            print_exc()

        fishing_event.unsubscribe()
        self.first_loop_done = False

    def _engine_loop(self):
        skip_count = 0
        while self.state == 1 and WindowClient.running():
            # crop qr and get the values from it
            self.values = qr_detection.get_values(self.window)

            # if fishyqr fails to get read multiple times, stop the bot
            if not self.values:
                if skip_count >= 5:
                    logging.error("Couldn't read values from FishyQR, Stopping engine...")
                    return
                skip_count += 1
                time.sleep(0.1)
            else:
                skip_count = 0

            if self.values:
                fishing_mode.loop(self.values[3])
            self.first_loop_done = True
            time.sleep(0.1)

    def _wait_and_check(self):
        time.sleep(10)
        if not FishEvent.FishingStarted and self.state == 1:
            logging.warning("Doesn't look like fishing has started \n"
                            "Check out #faqs on our discord channel to troubleshoot the issue")

    # TODO: remove this, no longer needed
    def show_qr_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 25.0:
                t += freq
                logging.info(str(self.values))
                time.sleep(freq)
            logging.info("Displaying QR values stopped")

        logging.info("Will display QR values for 25 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    fisher = SemiFisherEngine(None)
    fisher.toggle_start()
