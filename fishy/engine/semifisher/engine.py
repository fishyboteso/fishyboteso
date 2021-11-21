import logging
import time
import typing
from threading import Thread
from typing import Callable, Optional

import cv2
from fishy.engine.semifisher.fishing_mode import FishingMode

from fishy.helper.helper import log_raise
from playsound import playsound

from fishy.engine.common.IEngine import IEngine
from fishy.engine.common.qr_detection import get_qr_location, get_values_from_image, image_pre_process
from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher import fishing_event, fishing_mode
from fishy.engine.semifisher.fishing_event import FishEvent
from fishy.helper import helper
from fishy.helper.luaparser import sv_color_extract

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class SemiFisherEngine(IEngine):
    def __init__(self, gui_ref: Optional['Callable[[], GUI]']):
        super().__init__(gui_ref)
        self.window = None

    def run(self):
        """
        Starts the fishing
        code explained in comments in detail
        """
        fishing_event.init()
        self.window = WindowClient(color=cv2.COLOR_RGB2GRAY, show_name="semifisher debug")

        # check for game window and stuff
        self.gui.bot_started(True)

        if self.get_gui:
            logging.info("Starting the bot engine, look at the fishing hole to start fishing")
            Thread(target=self._wait_and_check).start()

        self.window.crop = get_qr_location(self.window.get_capture())
        if self.window.crop is None:
            log_raise("FishyQR not found")

        while self.start and WindowClient.running():
            capture = self.window.processed_image(func=image_pre_process)

            # if window server crashed
            if capture is None:
                self.gui.bot_started(False)
                self.toggle_start()
                continue

            # crop qr and get the values from it
            values = get_values_from_image(capture)
            if values is None:
                self.gui.bot_started(False)
                self.toggle_start()
                continue

            fishing_mode.loop(values[3])
            time.sleep(0.1)

        self.window.show(False)
        logging.info("Fishing engine stopped")
        self.gui.bot_started(False)
        fishing_event.unsubscribe()
        self.window.destory()

    def _wait_and_check(self):
        time.sleep(10)
        if not FishEvent.FishingStarted and self.start:
            logging.warning("Doesn't look like fishing has started \n"
                            "Check out #faqs on our discord channel to troubleshoot the issue")

    def show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode) + ":" + str(self.window.get_capture()[0][0]))
                time.sleep(freq)

        logging.debug("Will display pixel values for 10 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()

    def toggle_start(self):
        self.start = not self.start
        if self.start:
            self.thread = Thread(target=self.run)
            self.thread.start()
            playsound(helper.manifest_file("beep.wav"), False)
        else:
            helper.playsound_multiple(helper.manifest_file("beep.wav"))


if __name__ == '__main__':
    logging.getLogger("").setLevel(logging.DEBUG)
    # noinspection PyTypeChecker
    fisher = SemiFisherEngine(None)
    fisher.toggle_start()
