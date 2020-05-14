import time
from threading import Thread

import cv2
import logging

import pywintypes

from fishy.gui import GUIFunction, GUIEvent
from . import fishing_event
from .fishing_event import HookEvent, StickEvent, LookEvent, IdleEvent
from .fishing_mode import FishingMode
from .pixel_loc import PixelLoc
from .window import Window


def _wait_and_check(gui):
    time.sleep(10)
    if not fishing_event._FishingStarted:
        gui.call(GUIFunction.SHOW_ERROR, ("Doesn't look like fishing has started\n\n"
                                          "Make sure ProvisionsChalutier addon is visible clearly on top "
                                          "left corner of the screen, either,\n"
                                          "1) Outdated addons are disabled\n"
                                          "2) Other addons are overlapping ProvisionsChalutier\n"
                                          "3) Post processing (re shader) is on\n\n"
                                          "If fixing those doesnt work, try running the bot as admin",))


class Engine:
    def __init__(self, gui_ref, gui_event_buffer, config):
        self.gui_events = gui_event_buffer
        self.start = False
        self.fishPixWindow = None
        self.fishy_thread = None
        self.gui = gui_ref
        self.config = config

    def start_fishing(self, action_key: str, borderless: bool, collect_r: bool):
        """
        Starts the fishing
        code explained in comments in detail
        """

        # initialize widow
        # noinspection PyUnresolvedReferences
        try:
            Window.init(borderless)
        except pywintypes.error:
            logging.info("Game window not found")
            self.start = False
            return

        # initializes fishing modes and their callbacks
        FishingMode("hook", 0, HookEvent(action_key, collect_r))
        FishingMode("stick", 1, StickEvent())
        FishingMode("look", 2, LookEvent(action_key))
        FishingMode("idle", 3, IdleEvent(self.config.get("uid")))

        self.fishPixWindow = Window(color=cv2.COLOR_RGB2HSV)

        # check for game window and stuff
        self.gui.call(GUIFunction.STARTED, (True,))
        logging.info("Starting the bot engine, look at the fishing hole to start fishing")
        Thread(target=_wait_and_check, args=(self.gui,)).start()
        while self.start:
            # Services to be ran in the start of the main loop
            Window.loop()

            # get the PixelLoc and find the color values, to give it to `FishingMode.Loop`
            self.fishPixWindow.crop = PixelLoc.val
            hue_value = self.fishPixWindow.get_capture()[0][0][0]
            FishingMode.loop(hue_value)
            # Services to be ran in the end of the main loop
            Window.loop_end()
        logging.info("Fishing engine stopped")
        self.gui.call(GUIFunction.STARTED, (False,))

    def start_event_handler(self):
        while True:
            while len(self.gui_events) > 0:
                event = self.gui_events.pop(0)

                if event[0] == GUIEvent.START_BUTTON:
                    self.start = not self.start
                    if self.start:
                        self.fishy_thread = Thread(target=self.start_fishing, args=(*event[1],))
                        self.fishy_thread.start()
                elif event[0] == GUIEvent.CHECK_PIXELVAL:
                    if self.start:
                        self._show_pixel_vals()
                    else:
                        logging.debug("Start the engine first before running this command")
                elif event[0] == GUIEvent.QUIT:
                    self.start = False
                    return

    def _show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode.label) + ":" + str(self.fishPixWindow.get_capture()[0][0]))
                time.sleep(freq)

        logging.debug("Will display pixel values for 10 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()
