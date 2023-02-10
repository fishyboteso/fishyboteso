import os
from pathlib import Path


# this prevents importing from package while setup
def main():
    from fishy.__main__ import main as actual_main
    actual_main()


__version__ = (Path(os.path.dirname(__file__)) / "version.txt").read_text()
