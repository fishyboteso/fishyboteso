from pixel_loc import *


def on_release(key):
    """
    Read input
    :param key: key released
    :return: void
    """

    if G.controls["pause"][0] == key:
        G.pause = not G.pause
        if G.pause:
            print("PAUSED")
        else:
            print("STARTED")

    elif G.controls["debug"][0] == key:
        G.debug = not G.debug

    elif G.controls["stop"][0] == key:
        G.stop = True

    elif G.controls["configPL"][0] == key:
        G.configPL = not G.configPL


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

    fishPixWindow = Window("fishPixWindow", PixelLoc.val, 1, cv2.COLOR_BGR2HSV)
    fishPixDebugWindow = Window("fishPixDebugWindow", PixelLoc.val, 200, cv2.COLOR_BGR2RGB)

    Log.ctrl()
    # todo
    with Listener(on_release=on_release):
        while not G.stop:
            time.sleep(sleepFor)
            Window.Loop()
            Log.Loop()

            pixelVal = (PixelLoc.val[0], PixelLoc.val[1], PixelLoc.val[0] + 1, PixelLoc.val[1] + 1)
            fishPixWindow.crop = pixelVal
            fishPixDebugWindow.crop = pixelVal
            hueValue = fishPixWindow.getCapture()[0][0][0]
            FishingMode.Loop(hueValue, G.pause)
            fishPixDebugWindow.show(G.debug or G.configPL)
            if G.debug or G.configPL:
                Log.ou(str(FishingMode.CurrentMode.label) + ":" + str(hueValue))
            PixelLoc.Loop()

            Log.LoopEnd()
            Window.LoopEnd()


if __name__ == "__main__":
    startFishing()
