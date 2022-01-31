from fishy import constants


# this prevents importing from package while setup
def main():
    from fishy.__main__ import main as actual_main
    actual_main()


__version__ = constants.version
