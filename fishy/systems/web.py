import logging
from functools import wraps

import requests
from whatsmyip.ip import get_ip
from whatsmyip.providers import GoogleDnsProvider

from fishy.systems.globals import G

# domain = "https://fishyeso.herokuapp.com"
domain = "http://127.0.0.1:5000"

user = "/api/user"
notify = "/api/notify"
subscription = "/api/subscription/"
hole_depleted = "/api/hole_depleted"
session = "/api/session"
terms = "/terms.html"


def uses_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if get_session(args[0]) is None:
            logging.error("Couldn't create a session")
            return None
        else:
            return f(*args, **kwargs)

    return wrapper


def fallback(default):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                return default

        return wrapper

    return inner


def get_notification_page(uid):
    return domain + f"?uid={uid}"


def get_terms_page():
    return domain + terms


@fallback(False)
def register_user(uid):
    ip = get_ip(GoogleDnsProvider)
    body = {"uid": uid, "ip": ip}
    response = requests.post(domain + user, json=body)
    return response.ok and response.json()["success"]


@fallback(None)
def send_notification(uid, message):
    if not is_subbed(uid):
        return False

    body = {"uid": uid, "message": message}
    requests.post(domain + notify, json=body)


@uses_session
@fallback(None)
def send_hole_deplete(uid, fish_caught, hole_time, fish_times):
    hole_data = {
        "fish_caught": fish_caught,
        "hole_time": hole_time,
        "fish_times": fish_times,
        "session": get_session(uid)
    }

    body = {"uid": uid, "hole_data": hole_data}
    requests.post(domain + hole_depleted, json=body)


@fallback(False)
def is_subbed(uid, lazy=True):
    if lazy and G._is_subbed is not None:
        return G._is_subbed

    if uid is None:
        return False

    body = {"uid": uid}
    response = requests.get(domain + subscription, params=body)
    G._is_subbed = response.json()["subbed"]
    return G._is_subbed


@fallback(None)
def unsub(uid):
    G._is_subbed = False
    body = {"uid": uid}
    requests.delete(domain + subscription, json=body)


@fallback(None)
def get_session(uid, lazy=True):
    if lazy and G._session_id is not None:
        return G._session_id

    body = {"uid": uid}
    response = requests.post(domain + session, params=body)
    G._session_id = response.json()["session_id"]
    return G._session_id
