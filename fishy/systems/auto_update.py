"""
auto_update.py
checks version and auto updates
"""

import re
import subprocess
import sys
import urllib.request
from os import execl

import pkg_resources
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
    soup = BeautifulSoup(html.read(), "html5lib")
    versions = []
    for link in soup.find_all('a'):
        text = link.get_text()
        try:
            version = re.search(pkg + '-(.*)\.tar\.gz', text).group(1)
            versions.append(_normalize_version(version))
        except AttributeError:
            pass
    if len(versions) == 0:
        raise Exception  # no version
    return max(versions)


def _get_current_version(pkg):
    """
    Gets the current version of the package installed
    :param pkg: name of the installed backage
    :return: version normalized
    """
    return _normalize_version(pkg_resources.get_distribution(pkg).version)


def auto_upgrade():
    """
    public function,
    compares current version with the latest version (from web),
    if current version is older, then it updates and restarts the script
    """
    index = "https://pypi.python.org/simple"
    pkg = "fishy"
    if _get_highest_version(index, pkg) > _get_current_version(pkg):
        subprocess.call(["python", '-m', 'pip', 'install', '--upgrade', 'fishy', '--user'])
        execl(sys.executable, *([sys.executable] + sys.argv))
