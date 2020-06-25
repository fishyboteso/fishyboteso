import ctypes
import logging
import os
import sys

import win32con
import win32gui

import fishy
from fishy import web, helper, gui
from fishy.engine.event_handler import EngineEventHandler
from fishy.gui import GUI
from fishy.helper import Config


# noinspection PyBroadException
def initialize(c: Config, window_to_hide):
    helper.create_shortcut_first(c)
    helper.initialize_uid(c)

    new_session = web.get_session(c)
    if new_session is None:
        logging.error("Couldn't create a session, some features might not work")
    print(f"created session {new_session}")

    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if is_admin:
        logging.info("Running with admin privileges")

    try:
        helper.auto_upgrade()
    except Exception:
        pass

    if not c.get("debug", False):
        win32gui.ShowWindow(window_to_hide, win32con.SW_HIDE)
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    helper.check_addon("ProvisionsChalutier")

    if c.get("debug", False):
        helper.check_addon("FooAddon")


def main():
    print("launching please wait...")

    window_to_hide = win32gui.GetForegroundWindow()
    c = Config()

    if not gui.check_eula(c):
        return

    bot = EngineEventHandler(c, lambda: gui_window)
    gui_window = GUI(c, lambda: bot)

    gui_window.start()

    logging.info(f"Fishybot v{fishy.__version__}")
    initialize(c, window_to_hide)

    bot.start_event_handler()


if __name__ == "__main__":
    main()
