import time
import typing
import logging
from threading import Thread
from typing import Callable
from typing import Optional
from playsound import playsound

from fishy.engine.common.window import WindowClient
from fishy.engine.semifisher.fishing_mode import Colors, FishingMode

from fishy.engine.common.IEngine import IEngine
from fishy.engine.semifisher.fishing_event import FishEvent
from fishy.engine.semifisher import fishing_mode, fishing_event
from fishy.engine.semifisher.pixel_loc import PixelLoc
from fishy.helper import helper

from fishy.helper.luaparser import sv_color_extract

if typing.TYPE_CHECKING:
    from fishy.gui import GUI


class SemiFisherEngine(IEngine):
    def __init__(self, gui_ref: Optional['Callable[[], GUI]']):
        super().__init__(gui_ref)
        self.fishPixWindow = None

    def run(self):
        """
        Starts the fishing
        code explained in comments in detail
        """
        fishing_event.init()
        self.fishPixWindow = WindowClient()

        # check for game window and stuff
        self.gui.bot_started(True)

        sv_color_extract(Colors)

        if self.get_gui:
            logging.info("Starting the bot engine, look at the fishing hole to start fishing")
            Thread(target=self._wait_and_check).start()

        while self.start and WindowClient.running():
            capture = self.fishPixWindow.get_capture()

            if capture is None:
                # if window server crashed
                self.gui.bot_started(False)
                self.toggle_start()
                continue

            self.fishPixWindow.crop = PixelLoc.val
            fishing_mode.loop(capture[0][0])
            time.sleep(0.1)

        logging.info("Fishing engine stopped")
        self.gui.bot_started(False)
        fishing_event.unsubscribe()
        self.fishPixWindow.destory()

    def _wait_and_check(self):
        time.sleep(10)
        if not FishEvent.FishingStarted and self.start:
            logging.warning("Doesn't look like fishing has started \nCheck out #read-me-first on our discord channel to troubleshoot the issue")

    def show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode) + ":" + str(self.fishPixWindow.get_capture()[0][0]))
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

