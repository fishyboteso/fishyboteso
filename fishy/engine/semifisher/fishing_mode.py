import time
from enum import Enum

subscribers = []


class State(Enum):
    IDLE     = [  0,   0, 255]
    LOOKAWAY = [150, 255,  76]
    LOOKING  = [100, 255, 101]
    DEPLETED = [ 30, 255,  76]
    NOBAIT   = [ 96, 255, 255]
    FISHING  = [ 18, 165, 213]
    REELIN   = [ 60, 255, 204]
    LOOT     = [  0, 255, 204]
    INVFULL  = [  0, 255,  51]
    FIGHT    = [120, 255, 204]
    DEAD     = [  0,   0,  51]

def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(hsv):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param hsv: hsv read by the bot
    """
    FishingMode.CurrentMode = State.IDLE
    for s in State:
        if all(hsv == s.value):
            FishingMode.CurrentMode = s

    if FishingMode.CurrentMode == State.LOOKING:
        _notify(FishingMode.CurrentMode)
        time.sleep(1)
    elif FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
