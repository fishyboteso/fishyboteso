"""Fishy

Usage:  
  fishy.py -h | --help
  fishy.py -v | --version
  fishy.py [--ip=<ipv4>] [--hook-threshold=<int>] [--check-frequency=<hz>] [--no-resize]

Options:
  -h, --help                Show this screen.
  -v, --version             Show version.
  --ip=<ipv4>               Local Ip Address of the android phone.
  --hook-threshold=<int>    Threshold amount for classifier after which label changes [default: 3].
  --check-frequency=<hz>    Sleep after loop in s [default: 10].
"""

VERSION = "0.1.0"
print("Fishy " + VERSION + " for Elder Scrolls Online")

try:
    from docopt import docopt

    arguments = docopt(__doc__)
    if arguments["--version"]:
        quit()

    print("Loading, Please Wait...")
    import imutils as imutils
    import numpy as np
    from PIL import ImageGrab
    import cv2
    import pyautogui
    import time
    import fishy_network as net
    from fishy_config import config_win
    from pynput.keyboard import Key, Listener
    from decimal import Decimal
    from win32api import GetSystemMetrics
    import pickle
except Exception:
    raise

controls = {"stop": [Key.f11, "f11"], "debug": [Key.f10, "f10"], "pause": [Key.f9, "f9"], "configPL": [Key.f8, "f8"]}

stop = False
pause = False
debug = False
configPL = False

IMG_SIZE = 100
LR = 1e-3
STICK_TIMEOUT = 30.0
NONE_TIMEOUT = 5.0
IP_ADDRESS = arguments["--ip"]
bbox = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

try:
    pixelLoc = pickle.load(open("pixelLoc.pickle", "rb"))
except (OSError, IOError) as e:
    pixelLoc = [[240, 31], [241, 32]]


def process_img(original_img):
    """
    Convert image into hsv and crop it to select the required pixel
    :param original_img: image grabbed from screen
    :return: processed image in hsv
    """
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)
    # y:y+h, x:x+w
    croped_img = original_img[pixelLoc[0][1]:pixelLoc[1][1], pixelLoc[0][0]:pixelLoc[1][0]]
    return croped_img


def process_show(original_img):
    """
    Converts image into rgb and crop it to select the required pixel then scale it up for debuging
    :param original_img: image grabbed from screen
    :return: proessed image in rgb
    """
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
    # y:y+h, x:x+w
    croped_img = original_img[pixelLoc[0][1]:pixelLoc[1][1], pixelLoc[0][0]:pixelLoc[1][0]]
    croped_img = imutils.resize(croped_img, width=200)
    return croped_img


def round_float(v, ndigits=2, rt_str=False):
    d = Decimal(v)
    v_str = ("{0:.%sf}" % ndigits).format(round(d, ndigits))
    if rt_str:
        return v_str
    return Decimal(v_str)


def pullStick(fishCaught, timeToHook):
    """
    Hooks the fish
    :param fishCaught: fish cout to be displayed
    :param timeToHook: time took to hook the fish
    :return: void
    """
    print("HOOOOOOOOOOOOOOOOOOOOOOOK....... " + str(fishCaught) + " caught " + " in " + str(
        round_float(timeToHook)) + " secs")
    pyautogui.press('e')
    # Timer(0.5, pressE).start()


def on_release(key):
    """
    Read input
    :param key: key released
    :return: void
    """
    global stop, pause, debug, configPL

    if controls["pause"][0] == key:
        pause = not pause
        if pause:
            print("PAUSED")
        else:
            print("STARTED")

    elif controls["debug"][0] == key:
        debug = not debug

    elif controls["stop"][0] == key:
        stop = True

    elif controls["configPL"][0] == key:
        configPL = not configPL


def updatePixelLoc():
    global pixelLoc
    x, y = pyautogui.position()
    pixelLoc = [[x, y], [x + 1, y + 1]]


def startFishing():
    """
    Starts the fishing codde
    :return: void
    """
    global stop, pause, debug

    pause = True
    showedControls = True
    debug = False
    stop = False
    holeDepleteSent = True
    timerStarted = False
    use_net = False
    hooked = False
    configPixelSave = True
    threwStick = False

    fishCaught = 0
    prevLabel = 0
    labelNum = 3
    hVals = [60, 18, 100]
    current_thresh = 0
    stickInitTime = time.time()

    if not arguments["--no-resize"]:
        config_win()

    ctrl_help = controls["configPL"][1] + ": config pixel value\n" + controls["pause"][1] + ": start or pause\n" + \
                controls["debug"][1] + ": start debug\n" + controls["stop"][1] + ": quit\n"
    print(ctrl_help)

    if IP_ADDRESS is not None:
        use_net = True
        net.initialize(IP_ADDRESS)

    threshold = int(arguments["--hook-threshold"])
    sleepFor = (1 / float(arguments["--check-frequency"]))

    with Listener(on_release=on_release):
        while not stop:
            time.sleep(sleepFor)
            # image grab
            screen = np.array(ImageGrab.grab(bbox=bbox))
            new_screen = process_img(screen)
            hueValue = new_screen[0][0][0]

            # find currentlable
            currentLabel = 3
            for i, val in enumerate(hVals):
                if hueValue == val:
                    currentLabel = i

            # check if it passes threshold, if so change labelNum
            if prevLabel == currentLabel:
                current_thresh += 1
            else:
                current_thresh = 0
            prevLabel = currentLabel
            if current_thresh >= threshold:
                labelNum = currentLabel

            # use label num
            if not pause:

                # fish caught
                if labelNum == 0:
                    if not hooked:
                        fishCaught += 1
                        timeToHook = time.time() - stickInitTime
                        pullStick(fishCaught, timeToHook)
                        hooked = True

                # fishing
                if labelNum == 1:
                    hooked = False
                    if not timerStarted:
                        stickInitTime = time.time()
                        timerStarted = True
                    if (time.time() - stickInitTime) >= STICK_TIMEOUT:
                        print("STICK TIMED OUT, THROWING AGAIN")
                        pyautogui.press('e')
                        timerStarted = False
                else:
                    timerStarted = False

                # looking on hole
                if labelNum == 2:
                    if not threwStick:
                        pyautogui.press('e')
                        threwStick = True
                else:
                    threwStick = False

                # not looking on hole
                if labelNum == 3:
                    if not holeDepleteSent:
                        if fishCaught > 0:
                            print("HOLE DEPLETED")
                            if use_net:
                                net.sendHoleDeplete(fishCaught)
                        fishCaught = 0
                        holeDepleteSent = True
                else:
                    holeDepleteSent = False

            if debug or configPL:
                print(str(labelNum) + ":" + str(hueValue))
                cv2.imshow('image', process_show(screen))
                showedControls = False
            else:
                if not showedControls:
                    showedControls = True
                    print(ctrl_help)
                    cv2.destroyAllWindows()

            if configPL:
                updatePixelLoc()
                configPixelSave = False
            elif not configPixelSave:
                pickle.dump(pixelLoc, open("pixelLoc.pickle", "wb"))
            cv2.waitKey(25)


if __name__ == "__main__":
    startFishing()
