import cv2
from docopt import docopt
from pynput.keyboard import Listener

from fishy.systems import *
import logging

from fishy.systems.config import Config
from fishy.systems.gui import GUI, GUIStreamHandler, GUICallback

"""
Start reading from `init.py`
"""


def on_release(key):
    """
    Reads input, finds out the resultant action and performs it

    :param key: key pressed
    """

    c = Control.find(key)
    if c is None:
        return

    if c[0] == Control.Keywords.StartPause:

        if not G.pause:
            logging.info("PAUSED")
            G.pause = True
            return

        if PixelLoc.config():
            logging.info("STARTED")
            G.pause = False
        else:
            logging.info("addon properly not installed, if it is installed try restarting the game.")

    elif c[0] == Control.Keywords.Debug:
        G.debug = not G.debug

    elif c[0] == Control.Keywords.Stop:
        G.stop = True

    elif c[0] == Control.Keywords.SwitchMode:
        Control.nextState()
        logging.info(Control.getControlHelp())


def hsv2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)


def startFishing(ip: str, action_key: str, borderless: bool):
    """
    Starts the fishing
    code explained in comments in detail
    """

    if ip != "":
        net.initialize(ip)

    # initializes fishing modes and their callbacks
    FishingMode("hook", 0, HookEvent())
    FishingMode("stick", 1, StickEvent())
    FishingMode("look", 2, LookEvent())
    FishingMode("idle", 3, IdleEvent(ip != ""))

    logging.info("Starting the bot engine, look at the fishing hole to start fishing")

    fishPixWindow = Window(color=cv2.COLOR_RGB2HSV)

    # initialize widow
    Window.Init()
    with Listener(on_release=on_release):
        while not G.stop:
            # record the time to calculate time taken to execute one loop

            # Services to be ran in the start of the main loop
            Window.Loop()

            # get the PixelLoc and find the color values, to give it to `FishingMode.Loop`
            fishPixWindow.crop = PixelLoc.val
            hueValue = fishPixWindow.getCapture()[0][0][0]
            FishingMode.Loop(hueValue, G.pause)

            # if debug is on, show the color on the PixelLoc in a window and print the hue values of it
            if G.debug:
                fishPixWindow.show("pixloc", resize=200, func=hsv2rgb)
                logging.debug(str(FishingMode.CurrentMode.label) + ":" + str(fishPixWindow.getCapture()[0][0]))

            # Services to be ran in the end of the main loop
            Window.LoopEnd()


def main():
    events_buffer = []
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)

    gui = GUI(Config(), lambda a, b: events_buffer.append((a, b)))
    gui.start()

    new_console = GUIStreamHandler(gui)
    rootLogger.addHandler(new_console)
    G.arguments = docopt(__doc__)


if __name__ == "__main__":
    main()
