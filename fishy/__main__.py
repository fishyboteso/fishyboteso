import time
from threading import Thread

import cv2
import pywintypes

from fishy.systems import *
import logging

from fishy.systems.config import Config
from fishy.systems.gui import GUI, GUIStreamHandler, GUIEvent, GUIFunction


class Fishy:
    def __init__(self, gui_ref, gui_event_buffer):
        self.gui_events = gui_event_buffer
        self.start = False
        self.fishPixWindow = None
        self.fishy_thread = None
        self.gui = gui_ref

    def start_fishing(self, ip: str, action_key: str, borderless: bool, collect_r: bool):
        """
        Starts the fishing
        code explained in comments in detail
        """

        if ip != "":
            net.initialize(ip)

        # initialize widow
        try:
            Window.Init(borderless)
        except pywintypes.error:
            logging.info("Game window not found")
            self.start = False
            return

        # initializes fishing modes and their callbacks
        FishingMode("hook", 0, HookEvent(collect_r))
        FishingMode("stick", 1, StickEvent())
        FishingMode("look", 2, LookEvent())
        FishingMode("idle", 3, IdleEvent(ip != ""))

        logging.info("Starting the bot engine, look at the fishing hole to start fishing")

        self.fishPixWindow = Window(color=cv2.COLOR_RGB2HSV)

        # check for game window and stuff
        self.gui.call(GUIFunction.STARTED, (True,))
        while self.start:
            # Services to be ran in the start of the main loop
            Window.Loop()

            # get the PixelLoc and find the color values, to give it to `FishingMode.Loop`
            self.fishPixWindow.crop = PixelLoc.val
            hueValue = self.fishPixWindow.getCapture()[0][0][0]
            FishingMode.Loop(hueValue)

            # Services to be ran in the end of the main loop
            Window.LoopEnd()
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
                        self.show_pixel_vals()
                    else:
                        logging.debug("Start the engine first before running this command")
                elif event[0] == GUIEvent.QUIT:
                    self.start = False
                    return

    def show_pixel_vals(self):
        def show():
            freq = 0.5
            t = 0
            while t < 10.0:
                t += freq
                logging.debug(str(FishingMode.CurrentMode.label) + ":" + str(self.fishPixWindow.getCapture()[0][0]))
                time.sleep(freq)

        logging.debug("Will display pixel values for 10 seconds")
        time.sleep(5)
        Thread(target=show, args=()).start()


def main():
    events_buffer = []
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)

    gui = GUI(Config(), lambda a, b=None: events_buffer.append((a, b)))
    gui.start()

    new_console = GUIStreamHandler(gui)
    rootLogger.addHandler(new_console)

    fishy = Fishy(gui, events_buffer)
    fishy.start_event_handler()


if __name__ == "__main__":
    main()
