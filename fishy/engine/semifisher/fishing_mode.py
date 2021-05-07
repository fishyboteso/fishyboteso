import time
from enum import Enum

subscribers = []


class State(Enum):
    IDLE     =  0
    LOOKAWAY =  1
    LOOKING  =  2
    DEPLETED =  3
    NOBAIT   =  5
    FISHING  =  6
    REELIN   =  7
    LOOT     =  8
    INVFULL  =  9
    FIGHT    = 14
    DEAD     = 15

Colors = {
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
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(rgb):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param rgb: rgb read by the bot
    """
    FishingMode.CurrentMode = State.IDLE
    for s in State:
        if all(rgb == Colors[s.name]):
            FishingMode.CurrentMode = s

    if FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
