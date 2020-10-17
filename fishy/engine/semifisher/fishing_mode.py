from enum import Enum

subscribers = []


class State(Enum):
    HOOK = 60,
    STICK = 18,
    LOOK = 100,
    IDLE = -1


def _notify(event):
    for subscriber in subscribers:
        subscriber(event)


class FishingMode:
    CurrentMode = State.IDLE
    PrevMode = State.IDLE


def loop(hue_values):
    """
    Executed in the start of the main loop in fishy.py
    Changes modes, calls mode events (callbacks) when mode is changed

    :param hue_values: hue_values read by the bot
    """
    FishingMode.CurrentMode = State.IDLE
    for s in State:
        if hue_values == s.value:
            FishingMode.CurrentMode = s

    if FishingMode.CurrentMode != FishingMode.PrevMode:
        _notify(FishingMode.CurrentMode)

    FishingMode.PrevMode = FishingMode.CurrentMode
