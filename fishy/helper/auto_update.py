"""
auto_update.py
checks version and auto updates
"""
import logging
import re
import subprocess
import sys
import urllib.request
from os import execl

from bs4 import BeautifulSoup


def _hr_version(v):
    return '.'.join([str(x) for x in v])


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


def _get_highest_version(_index, _pkg):
    """
    Crawls web for latest version name then returns latest version
    :param _index: website to check
    :param _pkg: package name
    :return: latest version normalized
    """
    url = "{}/{}/".format(_index, _pkg)
    html = urllib.request.urlopen(url)
    if html.getcode() != 200:
        raise Exception  # not found
    soup = BeautifulSoup(html.read(), "html.parser")
    _versions = []
    for link in soup.find_all('a'):
        text = link.get_text()
        try:
            version = re.search(_pkg + r'-(.*)\.tar\.gz', text).group(1)
            _versions.append(_normalize_version(version))
        except AttributeError:
            pass
    if len(_versions) == 0:
        raise Exception  # no version
    return max(_versions)


def _get_current_version():
    """
    Gets the current version of the package installed
    :return: version normalized
    """
    import fishy
    return _normalize_version(fishy.__version__)


index = "https://pypi.python.org/simple"
pkg = "fishy"


def versions():
    return _hr_version(_get_current_version()), _hr_version(_get_highest_version(index, pkg))


def upgrade_avail():
    """
    Checks if update is available
    :return: boolean
    """
    return _get_current_version() < _get_highest_version(index, pkg)


def update_now(version):
    """
    public function,
    compares current version with the latest version (from web),
    if current version is older, then it updates and restarts the script
    """
    logging.info(f"Updating to v{version}, Please Wait...")
    subprocess.call(["python", '-m', 'pip', 'install', '--upgrade', 'fishy', '--user'])
    execl(sys.executable, *([sys.executable, '-m', 'fishy'] + sys.argv[1:]))
