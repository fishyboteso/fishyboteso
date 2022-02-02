import ctypes
import logging
import os
import sys

import win32con
import win32gui

import fishy
from fishy import gui, helper, web
from fishy.engine.common.event_handler import EngineEventHandler
from fishy.gui import GUI, splash, update_dialog
from fishy.helper import hotkey, auto_update
from fishy.helper.active_poll import active
from fishy.helper.config import config
from fishy.helper.helper import print_exc
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
    helper.initialize_uid()

    new_session = web.get_session()
    if new_session is None:
        logging.error("Couldn't create a session, some features might not work")
    print(f"created session {new_session}")

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


def main():
    config.init()
    if not gui.check_eula():
        return

    config.start_backup_scheduler()
    active.init()
    finish_splash = splash.start()
    hotkey.init()

    def on_gui_load():
        finish_splash()
        update_dialog.check_update(gui_window)

    print("launching please wait...")

    info_logger = ["comtypes", "PIL"]
    for i in info_logger:
        pil_logger = logging.getLogger(i)
        pil_logger.setLevel(logging.INFO)

    window_to_hide = win32gui.GetForegroundWindow()

    bot = EngineEventHandler(lambda: gui_window)
    gui_window = GUI(lambda: bot, on_gui_load)

    hotkey.start()

    logging.info(f"Fishybot v{fishy.__version__}")
    initialize(window_to_hide)

    gui_window.start()
    active.start()

    bot.start_event_handler()   # main thread loop

    hotkey.stop()
    active.stop()
    config.stop()
    bot.stop()


if __name__ == "__main__":
    main()
