import ctypes
import logging
import os
import sys
import time
from tkinter import messagebox

import win32con
import win32gui
from threading import Thread

import cv2
import pywintypes
import fishy
from fishy.systems.fishing_event import HookEvent, StickEvent, LookEvent, IdleEvent
from fishy.systems.fishing_mode import FishingMode
from fishy.systems.globals import G
from fishy.systems.pixel_loc import PixelLoc
from fishy.systems.window import Window
from fishy.systems.auto_update import auto_upgrade
from fishy.systems import helper, web
from fishy.systems.config import Config
from fishy.systems.gui import GUI, GUIEvent, GUIFunction
from fishy.systems.terms_gui import check_eula


class Fishy:
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
        try:
            Window.Init(borderless)
        except pywintypes.error:
            logging.info("Game window not found")
            self.start = False
            return

        # initializes fishing modes and their callbacks
        FishingMode("hook", 0, HookEvent(action_key, collect_r))
        FishingMode("stick", 1, StickEvent())
        FishingMode("look", 2, LookEvent())
        FishingMode("idle", 3, IdleEvent(self.config.get("uid")))

        self.fishPixWindow = Window(color=cv2.COLOR_RGB2HSV)

        # check for game window and stuff
        self.gui.call(GUIFunction.STARTED, (True,))
        logging.info("Starting the bot engine, look at the fishing hole to start fishing")
        Thread(target=wait_and_check, args=(self.gui,)).start()
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


def create_shortcut_first(gui, c):
    if not c.get("shortcut_created", False):
        helper.create_shortcut(gui)
        c.set("shortcut_created", True)


def initialize_uid(config: Config):
    if config.get("uid") is not None:
        return

    new_uid = helper.create_new_uid()
    if web.register_user(new_uid):
        config.set("uid", new_uid)
    else:
        logging.error("Couldn't register uid, some features might not work")


def initialize(gui, c: Config):
    create_shortcut_first(gui, c)
    initialize_uid(c)

    new_session = web.get_session(c)
    if new_session is None:
        logging.error("Couldn't create a session, some features might not work")
    print(f"created session {new_session}")

    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if is_admin and c.get("debug"):
        logging.info("Running with admin privileges")

    try:
        auto_upgrade()
    except Exception:
        pass

    if not c.get("debug", False):
        The_program_to_hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(The_program_to_hide, win32con.SW_HIDE)
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    helper.check_addon()


def wait_and_check(gui):
    time.sleep(10)
    if not G.FishingStarted:
        gui.call(GUIFunction.SHOW_ERROR, ("Doesn't look like fishing has started\n\n"
                                          "Make sure ProvisionsChalutier addon is visible clearly on top "
                                          "left corner of the screen, either,\n"
                                          "1) Outdated addons are disabled\n"
                                          "2) Other addons are overlapping ProvisionsChalutier\n"
                                          "3) Post processing (re shader) is on\n\n"
                                          "If fixing those doesnt work, try running the bot as admin",))


def ask_terms():
    messagebox.askquestion("Terms and Condition", )


def main():
    print("launching please wait...")

    c = Config()

    if not check_eula(c):
        return

    events_buffer = []
    gui = GUI(c, lambda a, b=None: events_buffer.append((a, b)))
    gui.start()

    logging.info(f"Fishybot v{fishy.__version__}")
    initialize(gui, c)

    bot = Fishy(gui, events_buffer, c)
    bot.start_event_handler()


if __name__ == "__main__":
    main()
