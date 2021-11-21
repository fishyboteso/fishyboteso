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


def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(state_num: int):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed
    """
    FishingMode.CurrentMode = State(state_num)

    if FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
