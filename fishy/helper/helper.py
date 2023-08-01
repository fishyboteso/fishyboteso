import ctypes
import logging
import os
import shutil
import sys
import threading
import time
import traceback
import webbrowser
from datetime import datetime
from hashlib import md5
from io import BytesIO
from threading import Thread
from uuid import uuid1
from zipfile import ZipFile

import cv2
import requests
from playsound import playsound

import fishy
from fishy.constants import libgps, lam2, fishyqr, fishyfsm, libmapping, libdl, libchatmsg
from fishy.helper.config import config
from fishy.osservices.os_services import os_services


def playsound_multiple(path, count=2):
    if count < 1:
        logging.debug("Please don't make me beep 0 times or less.")
        return

    def _ps_m():
        for i in range(count - 1):
            playsound(path, True)
        playsound(path, False)

    Thread(target=_ps_m).start()


def not_implemented():
    logging.error("Not Implemented")


def empty_function():
    pass


def wait_until(func):
    while not func():
        time.sleep(0.1)


def sign(x):
    return -1 if x < 0 else 1


def open_web(website):
    """
    Opens a website on browser,
    uses multi-threading so that current thread doesnt get blocked
    :param website: url
    """
    logging.debug("opening web, please wait...")
    Thread(target=lambda: webbrowser.open(website, new=2)).start()


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


def get_savedvarsdir():
    eso_path = os_services.get_eso_config_path()
    return os.path.join(eso_path, "live", "SavedVariables")


def get_addondir():
    eso_path = os_services.get_eso_config_path()
    return os.path.join(eso_path, "live", "Addons")


def addon_exists(name, url=None, v=None):
    return os.path.exists(os.path.join(get_addondir(), name))


def get_addonversion(name, url=None, v=None):
    if addon_exists(name):
        txt = name + ".txt"
        # noinspection PyBroadException
        try:
            with open(os.path.join(get_addondir(), name, txt)) as f:
                for line in f:
                    if "AddOnVersion" in line:
                        return int(line.split(' ')[2])
        except Exception:
            pass
    return 0


def install_required_addons(force=False):
    addons_req = [libgps, lam2, fishyqr, fishyfsm, libmapping, libdl, libchatmsg]
    addon_version = config.get("addon_version", {})
    installed = False
    for addon in addons_req:
        if force or (addon_exists(*addon) and
                     (addon[0] not in addon_version or (
                             addon[0] in addon_version and addon_version[addon[0]] < addon[2]))):
            remove_addon(*addon)
            install_addon(*addon)
            addon_version[addon[0]] = addon[2]
            installed = True
    config.set("addon_version", addon_version)
    if installed:
        logging.info("Please make sure to enable \"Allow outdated addons\" in ESO")


# noinspection PyBroadException
def install_addon(name, url, v=None):
    try:
        r = requests.get(url, stream=True)
        z = ZipFile(BytesIO(r.content))
        z.extractall(path=get_addondir())
        logging.info("Add-On " + name + " installed successfully!")
        return 0
    except Exception:
        logging.error("Could not install Add-On " + name + ", try doing it manually")
        print_exc()
        return 1


def remove_addon(name, url=None, v=None):
    try:
        shutil.rmtree(os.path.join(get_addondir(), name))
        logging.info("Add-On " + name + " removed!")
    except FileNotFoundError:
        pass
    except PermissionError:
        logging.error("Fishy has no permission to remove " + name + " Add-On")
        return 1
    return 0


def log_raise(msg):
    logging.error(msg)
    raise Exception(msg)


# noinspection PyProtectedMember,PyUnresolvedReferences
def _get_id(thread):
    # returns id of the respective thread
    if hasattr(thread, '_thread_id'):
        return thread._thread_id
    for _id, thread in threading._active.items():
        if thread is thread:
            return _id


def kill_thread(thread):
    thread_id = _get_id(thread)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                     ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        print('Exception raise failure')


def print_exc():
    logging.error(traceback.format_exc())
    traceback.print_exc()


def save_img_path():
    return os.path.join(os_services.get_documents_path(), "fishy_debug", "imgs")


def save_img(show_name, img, half=False):
    img_path = os.path.join(save_img_path(), show_name)
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    if half:
        img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

    t = time.strftime("%Y.%m.%d.%H.%M.%S")
    cv2.imwrite(
        os.path.join(img_path, f"{t}.jpg"),
        img)
