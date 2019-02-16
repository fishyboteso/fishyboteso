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

        if not G.pause:
            print("PAUSED")
            G.pause = True
            return

        if PixelLoc.config():
            print("STARTED")
            G.pause = False
        else:
            print("look on a fishing hole before starting")

    elif c[0] == Control.Keywords.Debug:
        G.debug = not G.debug

    elif c[0] == Control.Keywords.Stop:
        G.stop = True

    elif c[0] == Control.Keywords.SwitchMode:
        Control.nextState()
        Log.ctrl()

    elif c[0] == Control.Keywords.ClearPrintOnce:
        Log.clearPrintIds()


def hsv2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)


def startFishing():
    """
    Starts the fishing codde
    :return: void
    """

    use_net = arguments["--ip"] is not None
    if use_net:
        net.initialize(arguments["--ip"])

    sleepFor = (1 / float(arguments["--check-frequency"]))

    FishingMode("hook", 0, HookEvent())
    FishingMode("stick", 1, StickEvent())
    FishingMode("look", 2, LookEvent())
    FishingMode("idle", 3, IdleEvent(use_net))

    Log.ctrl()

    fishPixWindow = Window(color=cv2.COLOR_RGB2HSV)

    Window.Init()
    with Listener(on_release=on_release):
        while not G.stop:
            current_time = time.time()
            Window.Loop()
            Log.Loop()

            fishPixWindow.crop = PixelLoc.val
            hueValue = fishPixWindow.getCapture()[0][0][0]
            FishingMode.Loop(hueValue, G.pause)

            if G.debug:
                fishPixWindow.show("pixloc", resize=200, func=hsv2rgb)
                Log.ou(str(FishingMode.CurrentMode.label) + ":" + str(fishPixWindow.getCapture()[0][0]))

            Log.LoopEnd()
            Window.LoopEnd()

            frameTime = time.time() - current_time
            if frameTime < sleepFor:
                time.sleep(sleepFor - frameTime)
            else:
                Log.po(231, "Program taking more time than expected, this might slow your computer try increasing "
                            "\"--check-frequency\".")


if __name__ == "__main__":
    startFishing()
