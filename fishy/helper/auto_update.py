"""
auto_update.py
checks version and auto updates
"""
import logging
import re
import subprocess
import sys
from os import execl
from fishy.web import web


def _normalize_version(v):
    """
    converts version string into an "normalized" of versions which is a list of version codes,
    eg, input: '0.3.0', output: [0,3,0]
    this is done so that, versions can be compared easily
    :param v: string
    :return: list
    """
    rv = []
    for x in v.split("."):
        try:
            rv.append(int(x))
        except ValueError:
            for y in re.split("([0-9]+)", x):
                try:
                    if y != '':
                        rv.append(int(y))
                except ValueError:
                    rv.append(y)
    return rv


def _get_current_version():
    """
    Gets the current version of the package installed
    """
    import fishy
    return fishy.__version__


def versions():
    return _get_current_version(), web.get_highest_version()


def upgrade_avail():
    """
    Checks if update is available
    :return: boolean
    """

    highest_version_normalized = _normalize_version(web.get_highest_version())
    current_version_normalized = _normalize_version(_get_current_version())

    return current_version_normalized < highest_version_normalized


def update_now(version):
    """
    calling this function updates fishy,
    should be the last thing to be executed as this function will restart fishy
    the flaw is handed by `EngineEventHandler.update_flag` which is the last thing to be stopped
    """
    logging.info(f"Updating to v{version}, Please Wait...")
    subprocess.call(["python", '-m', 'pip', 'install', '--upgrade', 'fishy', '--user'])
    execl(sys.executable, *([sys.executable, '-m', 'fishy'] + sys.argv[1:]))
