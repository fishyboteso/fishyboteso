"""
fishing_event.py
Defines different fishing modes (states) which acts as state for state machine
also implements callbacks which is called when states are changed
"""
import logging
import time

from fishy.engine.semifisher import fishing_mode
from playsound import playsound

from fishy import web
from fishy.engine.semifisher.fishing_mode import State, FishingMode
from fishy.helper import helper
import keyboard
from win32gui import GetWindowText, GetForegroundWindow

from fishy.helper.config import config

import random


class FishEvent:
    fishCaught = 0
    totalFishCaught = 0
    stickInitTime = 0
    fish_times = []
    hole_start_time = 0
    FishingStarted = False
    jitter = False
    previousState = State.IDLE

    # initialize these
    action_key = 'e'
    collect_allow_auto = False
    uid = None
    sound = False


def _fishing_sleep(waittime, lower_limit_ms = 16, upper_limit_ms = 2500):
    reaction = 0.0
    if FishEvent.jitter and upper_limit_ms > lower_limit_ms:
        reaction = float( random.randrange(lower_limit_ms, upper_limit_ms) )/1000.0
    max_wait_t = waittime+reaction if waittime+reaction <= 2.5 else 2.5
    time.sleep(max_wait_t)


def if_eso_is_focused(func):
    def wrapper():
        if GetWindowText(GetForegroundWindow()) != "Elder Scrolls Online":
            logging.warning("ESO window is not focused")
            return
        func()
    return wrapper


def init():
    subscribe()
    FishEvent.jitter = config.get("jitter", False)
    FishEvent.action_key = config.get("action_key", 'e')
    FishEvent.collect_key = config.get("collect_key", 'r')
    FishEvent.collect_allow_auto = config.get("collect_allow_auto", False)
    FishEvent.uid = config.get("uid")
    FishEvent.sound = config.get("sound_notification", False)


def unsubscribe():
    if fisher_callback in fishing_mode.subscribers:
        fishing_mode.subscribers.remove(fisher_callback)


def subscribe():
    if fisher_callback not in fishing_mode.subscribers:
        fishing_mode.subscribers.append(fisher_callback)

        if FishingMode.CurrentMode == State.LOOK:
            fisher_callback(FishingMode.CurrentMode)


def fisher_callback(event: State):
    callbacks_map = {State.HOOK: on_hook, State.LOOK: on_look, State.IDLE: on_idle, State.STICK: on_stick}
    callbacks_map[event]()
    FishEvent.previousState = event


@if_eso_is_focused
def on_hook():
    """
    called when the fish hook is detected
    increases the `fishCaught`  and `totalFishCaught`, calculates the time it took to catch
    presses e to catch the fish
    """

    FishEvent.fishCaught += 1
    FishEvent.totalFishCaught += 1
    time_to_hook = time.time() - FishEvent.stickInitTime
    FishEvent.fish_times.append(time_to_hook)
    logging.info("HOOOOOOOOOOOOOOOOOOOOOOOK....... " + str(FishEvent.fishCaught) + " caught " + "in " + str(
        round(time_to_hook, 2)) + " secs.  " + "Total: " + str(FishEvent.totalFishCaught))

    keyboard.press_and_release(FishEvent.action_key)

    if FishEvent.collect_allow_auto:
        _fishing_sleep(0.15)
        keyboard.press_and_release(FishEvent.collect_key)
        _fishing_sleep(0.1)
    _fishing_sleep(0.0)


@if_eso_is_focused
def on_look():
    """
    presses e to throw the fishing rod
    """
    keyboard.press_and_release(FishEvent.action_key)


def on_idle():
    if FishEvent.fishCaught > 0:
        web.send_hole_deplete(FishEvent.uid, FishEvent.fishCaught, time.time() - FishEvent.hole_start_time,
                              FishEvent.fish_times)
        FishEvent.fishCaught = 0

    if FishEvent.previousState == State.HOOK:
        logging.info("HOLE DEPLETED")
    else:
        logging.info("FISHING INTERRUPTED")

    if FishEvent.sound:
        playsound(helper.manifest_file("sound.mp3"), False)


def on_stick():
    FishEvent.stickInitTime = time.time()
    FishEvent.FishingStarted = True

    if FishEvent.fishCaught == 0:
        FishEvent.hole_start_time = time.time()
        FishEvent.fish_times = []
