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


def _get_highest_version(index, pkg):
    """
    Crawls web for latest version name then returns latest version
    :param index: website to check
    :param pkg: package name
    :return: latest version normalized
    """
    url = "{}/{}/".format(index, pkg)
    html = urllib.request.urlopen(url)
    if html.getcode() != 200:
        raise Exception  # not found
    soup = BeautifulSoup(html.read(), "html.parser")
    versions = []
    for link in soup.find_all('a'):
        text = link.get_text()
        try:
            version = re.search(pkg + r'-(.*)\.tar\.gz', text).group(1)
            versions.append(_normalize_version(version))
        except AttributeError:
            pass
    if len(versions) == 0:
        raise Exception  # no version
    return max(versions)


def _get_current_version():
    """
    Gets the current version of the package installed
    :return: version normalized
    """
    import fishy
    return _normalize_version(fishy.__version__)


def auto_upgrade():
    """
    public function,
    compares current version with the latest version (from web),
    if current version is older, then it updates and restarts the script
    """
    index = "https://pypi.python.org/simple"
    pkg = "fishy"
    hightest_version = _get_highest_version(index, pkg)
    if hightest_version > _get_current_version():
        version = '.'.join([str(x) for x in hightest_version])
        logging.info(f"Updating to v{version}, Please Wait...")
        subprocess.call(["python", '-m', 'pip', 'install', '--upgrade', 'fishy', '--user'])
        execl(sys.executable, *([sys.executable] + sys.argv))
