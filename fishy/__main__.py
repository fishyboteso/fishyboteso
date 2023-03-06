import ctypes
import logging
import os
import sys

import win32con
import win32gui

import fishy
from fishy.gui import GUI, update_dialog, check_eula
from fishy import helper, web
from fishy.engine.common.event_handler import EngineEventHandler
from fishy.gui.log_config import GuiLogger
from fishy.gui.splash import Splash
from fishy.helper import hotkey
from fishy.helper.active_poll import active
from fishy.helper.config import config
from fishy.helper.hotkey.hotkey_process import hotkey
from fishy.helper.migration import Migration


def check_window_name(title):
    titles = ["Command Prompt", "PowerShell", "Fishy"]
    for t in titles:
        if t in title:
            return True
    return False


# noinspection PyBroadException
def initialize(window_to_hide):
    Migration.migrate()

    helper.create_shortcut_first()

    new_session = web.get_session()

    if new_session is None:
        logging.error("Couldn't create a session, some features might not work")
    logging.debug(f"created session {new_session}")

    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if is_admin:
        logging.info("Running with admin privileges")

    if not config.get("debug", False) and check_window_name(win32gui.GetWindowText(window_to_hide)):
        win32gui.ShowWindow(window_to_hide, win32con.SW_HIDE)
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    helper.install_required_addons()


def on_gui_load(gui, splash, logger):
    splash.finish()
    update_dialog.check_update(gui)
    logger.connect(gui)


def main():
    print("launching please wait...")
    bot = EngineEventHandler(lambda: gui)
    gui = GUI(lambda: bot, lambda: on_gui_load(gui, splash, logger))
    window_to_hide = win32gui.GetForegroundWindow()
    logger = GuiLogger()
    hotkey.init()
    active.init()

    try:
        config.init()
        if not check_eula():
            return

        logging.info(f"Fishybot v{fishy.__version__}")

        splash = Splash().start()
        config.start_backup_scheduler()

        initialize(window_to_hide)

        hotkey.start()
        gui.start()
        active.start()

        bot.start_event_handler()  # main thread loop
    except KeyboardInterrupt:
        print("caught KeyboardInterrupt, Stopping main thread")
    finally:
        gui.stop()
        hotkey.stop()
        active.stop()
        config.stop()
        bot.stop()


if __name__ == "__main__":
    main()
