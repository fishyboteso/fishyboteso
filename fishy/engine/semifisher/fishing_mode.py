from enum import Enum

subscribers = []


class State(Enum):
    IDLE      = 0  #Running around, neither looking at an interactable nor fighting
    LOOKAWAY  = 1  #Looking at an interactable which is NOT a fishing hole
    LOOKING   = 2  #Looking at a fishing hole
    NOBAIT    = 5  #Looking at a fishing hole, with NO bait equipped
    FISHING   = 6  #Fishing
    REELIN    = 7  #Reel in!
    LOOT      = 8  #Lootscreen open, only right after Reel in!
    INVFULL   = 9  #No free inventory slots
    FIGHT     = 14 #Fighting / Enemys taunted
    DEAD      = 15 #Dead


def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(state):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param state: state read by the bot from qr code
    """
    FishingMode.CurrentMode = State.IDLE
    for s in State:
        if state == s.value:
            FishingMode.CurrentMode = s

    if FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
