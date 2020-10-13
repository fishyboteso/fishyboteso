import logging
import os
import sys
import threading
import traceback
import webbrowser
import win32gui
from threading import Thread
from zipfile import ZipFile

from uuid import uuid1
from hashlib import md5

from win32com.client import Dispatch

import fishy
import winshell

from fishy import web
from . import Config


def not_implemented():
    logging.error("Not Implemented")


def empty_function():
    pass


def open_web(website):
    """
    Opens a website on browser,
    uses multi-threading so that current thread doesnt get blocked
    :param website: url
    """
    logging.debug("opening web, please wait...")
    Thread(target=lambda: webbrowser.open(website, new=2)).start()


def initialize_uid(config: Config):
    if config.get("uid") is not None:
        return

    new_uid = _create_new_uid()
    if web.register_user(new_uid):
        config.set("uid", new_uid)
    else:
        logging.error("Couldn't register uid, some features might not work")


def _create_new_uid():
    """
    Creates a unique id for user
    """
    return md5(str(uuid1()).encode()).hexdigest()


def install_thread_excepthook():
    """
    Workaround for sys.excepthook thread bug
    https://bugs.python.org/issue1230540
    (https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470).
    Call once from __main__ before creating any threads.
    If using psyco, call psycho.cannotcompile(threading.Thread.run)
    since this replaces a new-style class method.
    """
    import sys
    run_old = threading.Thread.run

    # noinspection PyBroadException
    def run(*args, **kwargs):
        try:
            run_old(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            sys.excepthook(*sys.exc_info())

    threading.Thread.run = run


def unhandled_exception_logging(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))
    logging.error("Unhandled exception: %s", text)


def manifest_file(rel_path):
    """
    returns a file from the manifest files,
    used to get the files which are installed along with the scripts
    :param rel_path: relative path from `__init__.py`
    :return: abs path of the file
    """
    return os.path.join(os.path.dirname(fishy.__file__), rel_path)


def create_shortcut_first(c):
    if not c.get("shortcut_created", False):
        create_shortcut()
        c.set("shortcut_created", True)


# noinspection PyBroadException
def create_shortcut(anti_ghosting: bool):
    """
    creates a new shortcut on desktop
    """
    try:
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Fishybot ESO.lnk")

        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)

        if anti_ghosting:
            shortcut.TargetPath = r"C:\Windows\System32\cmd.exe"
            python_dir = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            shortcut.Arguments = f"/C start /affinity 1 /low {python_dir} -m fishy"
        else:
            shortcut.TargetPath = os.path.join(os.path.dirname(sys.executable), "python.exe")
            shortcut.Arguments = "-m fishy"

        shortcut.IconLocation = manifest_file("icon.ico")
        shortcut.save()

        logging.info("Shortcut created")
    except Exception:
        traceback.print_exc()
        logging.error("Couldn't create shortcut")


# noinspection PyBroadException
def check_addon(name):
    """
    Extracts the addon from zip and installs it into the AddOn folder of eso
    """
    try:
        user = os.path.expanduser("~")
        addon_dir = os.path.join(user, "Documents", "Elder Scrolls Online", "live", "Addons")
        if not os.path.exists(os.path.join(addon_dir, name)):
            logging.info(f"{name} Addon not found, installing it...")
            with ZipFile(manifest_file(f"{name}.zip"), 'r') as z:
                z.extractall(path=addon_dir)
            logging.info("Please make sure you enable \"Allow outdated addons\" in-game")
    except Exception:
        logging.error("couldn't install addon, try doing it manually")


def restart():
    os.execl(sys.executable, *([sys.executable] + sys.argv))
