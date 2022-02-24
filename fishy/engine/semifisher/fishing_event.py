"""
fishing_event.py
Defines different fishing modes (states) which acts as state for state machine
also implements callbacks which is called when states are changed
"""
import logging
import random
import time

import keyboard
from playsound import playsound

from fishy import web
from fishy.engine.semifisher import fishing_mode
from fishy.engine.semifisher.fishing_mode import FishingMode, State
from fishy.helper import helper
from fishy.helper.config import config
from fishy.helper.helper import is_eso_active


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
    collect_key = 'r'
    sound = False


def _fishing_sleep(waittime, lower_limit_ms=16, upper_limit_ms=1375):
    reaction = 0.0
    if FishEvent.jitter and upper_limit_ms > lower_limit_ms:
        reaction = float(random.randrange(lower_limit_ms, upper_limit_ms)) / 1000.0
    max_wait_t = waittime + reaction if waittime + reaction <= 2.5 else 2.5
    time.sleep(max_wait_t)


def if_eso_is_focused(func):
    def wrapper():
        if not is_eso_active():
            logging.warning("ESO window is not focused")
            return
        func()
    return wrapper


def _sound_and_send_fishy_data():
    if FishEvent.fishCaught > 0:
        web.send_fish_caught(FishEvent.fishCaught, time.time() - FishEvent.hole_start_time, FishEvent.fish_times)
        FishEvent.fishCaught = 0

    if FishEvent.sound:
        playsound(helper.manifest_file("sound.mp3"), False)


def init():
    subscribe()
    FishEvent.jitter = config.get("jitter", False)
    FishEvent.action_key = config.get("action_key", 'e')
    FishEvent.collect_key = config.get("collect_key", 'r')
    FishEvent.uid = config.get("uid")
    FishEvent.sound = config.get("sound_notification", False)


def unsubscribe():
    if fisher_callback in fishing_mode.subscribers:
        fishing_mode.subscribers.remove(fisher_callback)


def subscribe():
    if fisher_callback not in fishing_mode.subscribers:
        fishing_mode.subscribers.append(fisher_callback)


def fisher_callback(event: State):
    callbacks_map = {
        State.IDLE: on_idle,
        State.LOOKAWAY: on_idle,
        State.LOOKING: on_looking,
        State.DEPLETED: on_depleted,
        State.NOBAIT: lambda: on_user_interact("You need to equip bait!"),
        State.FISHING: on_fishing,
        State.REELIN: on_reelin,
        State.LOOT: on_loot,
        State.INVFULL: lambda: on_user_interact("Inventory is full!"),
        State.FIGHT: lambda: on_user_interact("Character is FIGHTING!"),
        State.DEAD: lambda: on_user_interact("Character died!")
    }

    try:
        callbacks_map[event]()
        FishEvent.previousState = event
    except KeyError:
        logging.error("KeyError: State " + str(event) + " is not known.")
    except TypeError:
        logging.error("TypeError when reading state: " + str(event))


def on_idle():
    if FishEvent.previousState == State.REELIN:
        logging.info("HOLE DEPLETED")
        _sound_and_send_fishy_data()
    elif FishEvent.previousState == State.FISHING:
        logging.info("FISHING INTERRUPTED")
        _sound_and_send_fishy_data()


def on_depleted():
    logging.info("HOLE DEPLETED")
    _sound_and_send_fishy_data()


@if_eso_is_focused
def on_looking():
    """
    presses e to throw the fishing rod
    """
    _fishing_sleep(0.0)
    keyboard.press_and_release(FishEvent.action_key)


def on_user_interact(msg):
    logging.info(msg)
    web.send_notification(msg)

    if FishEvent.sound:
        playsound(helper.manifest_file("sound.mp3"), False)


def on_fishing():
    FishEvent.stickInitTime = time.time()
    FishEvent.FishingStarted = True

    if FishEvent.fishCaught == 0:
        FishEvent.hole_start_time = time.time()
        FishEvent.fish_times = []


@if_eso_is_focused
def on_reelin():
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

    _fishing_sleep(0.0)
    keyboard.press_and_release(FishEvent.action_key)
    _fishing_sleep(0.5)


def on_loot():
    _fishing_sleep(0)
    keyboard.press_and_release(FishEvent.collect_key)
    _fishing_sleep(0)
