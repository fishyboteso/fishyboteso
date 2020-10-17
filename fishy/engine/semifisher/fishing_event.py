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
from fishy.engine.semifisher.fishing_mode import State
from fishy.helper import helper
import keyboard

from fishy.helper.config import config


class FishEvent:
    fishCaught = 0
    totalFishCaught = 0
    stickInitTime = 0
    fish_times = []
    hole_start_time = 0
    FishingStarted = False
    previousState = State.IDLE

    # initialize these
    action_key = 'e'
    collect_r = False
    uid = None
    sound = False


def init():
    subscribe()
    FishEvent.action_key = config.get("action_key", 'e')
    FishEvent.uid = config.get("uid")
    FishEvent.sound = config.get("sound_notification", False)


def unsubscribe():
    if fisher_callback in fishing_mode.subscribers:
        fishing_mode.subscribers.remove(fisher_callback)


def subscribe():
    if fisher_callback not in fishing_mode.subscribers:
        fishing_mode.subscribers.append(fisher_callback)


def fisher_callback(event: State):
    callbacks_map = {State.HOOK: on_hook, State.LOOK: on_look, State.IDLE: on_idle, State.STICK: on_stick}
    callbacks_map[event]()
    FishEvent.previousState = event


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

    if FishEvent.collect_r:
        time.sleep(0.1)
        keyboard.press_and_release('r')
        time.sleep(0.1)


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
        if FishEvent.sound:
            playsound(helper.manifest_file("sound.mp3"), False)

    if FishEvent.previousState == State.HOOK:
        logging.info("HOLE DEPLETED")
    else:
        logging.info("FISHING INTERRUPTED")


def on_stick():
    FishEvent.stickInitTime = time.time()
    FishEvent.FishingStarted = True

    if FishEvent.fishCaught == 0:
        FishEvent.hole_start_time = time.time()
        FishEvent.fish_times = []
