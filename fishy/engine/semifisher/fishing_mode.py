from enum import Enum
import logging

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
    State.IDLE     : [255, 255, 255],
    State.LOOKAWAY : [ 76,   0,  76],
    State.LOOKING  : [101,  69,   0],
    State.DEPLETED : [  0,  76,  76],
    State.NOBAIT   : [255, 204,   0],
    State.FISHING  : [ 75, 156, 213],
    State.REELIN   : [  0, 204,   0],
    State.LOOT     : [  0,   0, 204],
    State.INVFULL  : [  0,   0,  51],
    State.FIGHT    : [204,   0,   0],
    State.DEAD     : [ 51,  51,  51]
}


def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(rgb, currentmode=FishingMode.CurrentMode):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param rgb: rgb read by the bot
    """
    # FishingMode.CurrentMode = State.IDLE
    for s in State:

        if all(rgb == Colors[s]):
            # logging.error("state found")
            FishingMode.PrevMode = FishingMode.CurrentMode
            # logging.error("PrevMode set to {0}".format(FishingMode.CurrentMode))
            FishingMode.CurrentMode = s
            # logging.error("state set to {0}".format(s))
            
            if FishingMode.CurrentMode != FishingMode.PrevMode:
                logging.error("state change, notify({0}). previous: {1}".format(FishingMode.CurrentMode, FishingMode.PrevMode))
                _notify(FishingMode.CurrentMode)
            else:
                # logging.error("State did not change, prev: {0} current {0}".format(FishingMode.CurrentMode, FishingMode.PrevMode))
                pass
        else:
            # logging.error("state was not found, rgb: {}".format(rgb))
            # FishingMode.CurrentMode = State.IDLE
            pass
