import re
import subprocess
import sys
import urllib.request
from os import execl

import pkg_resources
from bs4 import BeautifulSoup


def _normalize_version(v):
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
    return _normalize_version(pkg_resources.get_distribution(pkg).version)


def auto_upgrade():
    index = "https://pypi.python.org/simple"
    pkg = "fishy"
    if _get_highest_version(index, pkg) > _get_current_version(pkg):
        subprocess.call(["python", '-m', 'pip', 'install', '--upgrade', 'fishy', '--user'])
        execl(sys.executable, *([sys.executable] + sys.argv))
