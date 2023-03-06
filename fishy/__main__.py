import logging
import sys

import fishy
from fishy.gui import GUI, splash, update_dialog, check_eula
from fishy import helper, web
from fishy.engine.common.event_handler import EngineEventHandler
from fishy.gui.log_config import GuiLogger
from fishy.helper import hotkey
from fishy.helper.active_poll import active
from fishy.helper.config import config
from fishy.helper.hotkey.hotkey_process import hotkey
from fishy.helper.migration import Migration
from fishy.osservices.os_services import os_services


# noinspection PyBroadException
def initialize():
    Migration.migrate()

    if not config.get("shortcut_created", False):
        os_services.create_shortcut(False)
        config.set("shortcut_created", True)

    new_session = web.get_session()

    if new_session is None:
        logging.error("Couldn't create a session, some features might not work")
    logging.debug(f"created session {new_session}")

    if os_services.is_admin():
        logging.info("Running with admin privileges")

    if not config.get("debug", False):
        os_services.hide_terminal()
        helper.install_thread_excepthook()
        sys.excepthook = helper.unhandled_exception_logging

    helper.install_required_addons()


def main():
    print("launching please wait...")

    if not os_services.init():
        print("platform not supported")
        return

    config.init()
    if not check_eula():
        return

    finish_splash = splash.start()
    logger = GuiLogger()
    config.start_backup_scheduler()
    active.init()
    hotkey.init()

    def on_gui_load():
        finish_splash()
        update_dialog.check_update(gui)
        logger.connect(gui)

    bot = EngineEventHandler(lambda: gui)
    gui = GUI(lambda: bot, on_gui_load)

    hotkey.start()

    logging.info(f"Fishybot v{fishy.__version__}")
    initialize()

    gui.start()
    active.start()

    bot.start_event_handler()  # main thread loop

    hotkey.stop()
    active.stop()
    config.stop()
    bot.stop()


if __name__ == "__main__":
    main()
