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
from fishy.gui import GUI, splash, update_dialog
from fishy.helper import hotkey
from fishy.helper.config import config
from fishy.constants import chalutier, lam2


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
        if helper.upgrade_avail() and not config.get("dont_ask_update", False):
            cv,hv = helper.versions()
            update_now, dont_ask_update = update_dialog.start(cv,hv)
            if dont_ask_update:
                config.set("dont_ask_update", dont_ask_update)
            else:
                config.delete("dont_ask_update")

            if update_now:
                helper.auto_upgrade()
    except Exception:
        logging.error(traceback.format_exc())

    if not config.get("debug", False) and check_window_name(win32gui.GetWindowText(window_to_hide)):
        win32gui.ShowWindow(window_to_hide, win32con.SW_HIDE)
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    if not config.get("addoninstalled", False) and not helper.addon_exists(chalutier[0]):
        helper.install_addon(*chalutier)
        helper.install_addon(*lam2)
    config.set("addoninstalled", True)


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
