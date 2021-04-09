import time

subscribers = []


State = {
    "IDLE"     : [255, 255, 255],
    "LOOKAWAY" : [ 76,   0,  76],
    "LOOKING"  : [101,  69,   0],
    "DEPLETED" : [  0,  76,  76],
    "NOBAIT"   : [255, 204,   0],
    "FISHING"  : [ 75, 156, 213],
    "REELIN"   : [  0, 204,   0],
    "LOOT"     : [  0,   0, 204],
    "INVFULL"  : [  0,   0,  51],
    "FIGHT"    : [204,   0,   0],
    "DEAD"     : [ 51,  51,  51]
}


def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = "IDLE"
    PrevMode = "IDLE"


def loop(rgb):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param rgb: rgb read by the bot
    """
    FishingMode.CurrentMode = "IDLE"
    for s in State:
        if all(rgb == State[s]):
            FishingMode.CurrentMode = s

    if FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
