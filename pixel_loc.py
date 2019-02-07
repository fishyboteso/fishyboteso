from fishing_event import *


class PixelLoc:
    configPixelSaved = True

    try:
        val = pickle.load(open("pixelLoc.pickle", "rb"))
    except (OSError, IOError) as e:
        val = (240, 31)

    @staticmethod
    def Loop():
        if G.configPL:
            x, y = pyautogui.position()
            PixelLoc.val = (x, y)
            PixelLoc.configPixelSaved = False
        elif not PixelLoc.configPixelSaved:
            pickle.dump(PixelLoc.val, open("pixelLoc.pickle", "wb"))
            PixelLoc.configPixelSaved = True
