from pixel_loc import *


def on_release(key):
    """
    Read input
    :param key: key released
    :return: void
    """

    c = Control.find(key)
    if c is None:
        return

    if c[0] == Control.Keywords.StartPause:
        G.pause = not G.pause
        if G.pause:
            print("PAUSED")
        else:
            print("STARTED")

    elif c[0] == Control.Keywords.Debug:
        G.debug = not G.debug

    elif c[0] == Control.Keywords.Stop:
        G.stop = True

    elif c[0] == Control.Keywords.ConfigPixLoc:
        G.configPL = not G.configPL

    elif c[0] == Control.Keywords.SwitchMode:
        Control.nextState()
        Log.ctrl()

    elif c[0] == Control.Keywords.ClearPrintOnce:
        Log.clearPrintIds()


def ipDebug(img):
    # Setup SimpleBlobDetector parameters.
    hsvImg = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = (99, 254, 100)
    upper = (100, 255, 101)
    mask = cv2.inRange(hsvImg, lower, upper)
    #mask = cv2.bitwise_not(mask)

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 255

    params.filterByColor = True
    params.blobColor = 255

    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False

    params.filterByArea = True
    params.minArea = 10.0

    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    keypoints = detector.detect(mask)

    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    draw_keypoints(img, keypoints)

    return img


def hsv2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)


def startFishing():
    """
    Starts the fishing codde
    :return: void
    """

    if not arguments["--no-resize"]:
        config_win()

    use_net = arguments["--ip"] is not None
    if use_net:
        net.initialize(arguments["--ip"])

    sleepFor = (1 / float(arguments["--check-frequency"]))

    FishingMode("hook", 0, HookEvent())
    FishingMode("stick", 1, StickEvent())
    FishingMode("look", 2, LookEvent())
    FishingMode("idle", 3, IdleEvent(use_net))

    fishPixWindow = Window("fishPixWindow", PixelLoc.val, cv2.COLOR_BGR2HSV)

    try:
        hwnd = win32gui.FindWindow(None, "Elder Scrolls Online")

        rect = win32gui.GetWindowRect(hwnd)
        clientRect = win32gui.GetClientRect(hwnd)
        windowOffset = math.floor(((rect[2] - rect[0]) - clientRect[2]) / 2)
        titleOffset = ((rect[3] - rect[1]) - clientRect[3]) - windowOffset
        windowLoc = (rect[0] + windowOffset, rect[1] + titleOffset, rect[2] - windowOffset, rect[3] - windowOffset)

        gameScreen = Window("game", windowLoc, cv2.COLOR_BGR2RGB)

    except pywintypes.error:
        print("Game window not found")
        return

    Log.ctrl()
    # todo
    time.time()

    with Listener(on_release=on_release):
        while not G.stop:
            current_time = time.time()

            Window.Loop()
            Log.Loop()
            PixelLoc.Loop()

            pixelVal = (PixelLoc.val[0], PixelLoc.val[1], PixelLoc.val[0] + 1, PixelLoc.val[1] + 1)
            fishPixWindow.crop = pixelVal
            hueValue = fishPixWindow.getCapture()[0][0][0]
            FishingMode.Loop(hueValue, G.pause)

            if G.configPL:
                fishPixWindow.show(resize=200, func=hsv2rgb)
                Log.ou(str(FishingMode.CurrentMode.label) + ":" + str(fishPixWindow.getCapture()[0][0]))

            if G.debug:
                rect = win32gui.GetWindowRect(hwnd)
                gameScreen.crop = (rect[0] + windowOffset, rect[1] + titleOffset, rect[2] - windowOffset,
                                   rect[3] - windowOffset)
                gameScreen.show(func=ipDebug)

            Log.LoopEnd()
            Window.LoopEnd()

            frameTime = time.time() - current_time
            if frameTime < sleepFor:
                time.sleep(sleepFor - frameTime)


if __name__ == "__main__":
    startFishing()
