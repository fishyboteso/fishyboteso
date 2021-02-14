import ctypes
import logging
import os
import sys
import traceback
import win32con
import win32gui

import fishy
from fishy import web, helper, gui
from fishy.engine.common.event_handler import EngineEventHandler
from fishy.gui import GUI, splash
from fishy.helper import hotkey
from fishy.helper.config import config


def check_window_name(title):
    titles = ["Command Prompt", "PowerShell", "Fishy"]
    for t in titles:
        if t in title:
            return True
    return False


# noinspection PyBroadException
def initialize(window_to_hide):
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

    try:
        helper.auto_upgrade()
    except Exception:
        logging.error(traceback.format_exc())

    if not config.get("debug", False) and check_window_name(win32gui.GetWindowText(window_to_hide)):
        win32gui.ShowWindow(window_to_hide, win32con.SW_HIDE)
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    helper.check_addon("ProvisionsChalutier")


def main():
    splash.start()
    print("launching please wait...")

    pil_logger = logging.getLogger('PIL')
    pil_logger.setLevel(logging.INFO)

    window_to_hide = win32gui.GetForegroundWindow()

    if not gui.check_eula():
        return

    bot = EngineEventHandler(lambda: gui_window)
    gui_window = GUI(lambda: bot)

    hotkey.initalize()

    logging.info(f"Fishybot v{fishy.__version__}")
    initialize(window_to_hide)

    gui_window.start()

    bot.start_event_handler()


if __name__ == "__main__":
    main()
