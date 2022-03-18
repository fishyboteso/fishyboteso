import logging

import requests
from whatsmyip.ip import get_ip
from whatsmyip.providers import GoogleDnsProvider

from ..constants import apiversion
from ..helper.config import config
from . import urls
from .decorators import fallback, uses_session

_session_id = None


@fallback(-1)
def is_logged_in():
    if config.get("uid") is None:
        return -1

    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.get(urls.discord, params=body)
    logged_in = response.json()["discord_login"]
    return 1 if logged_in else 0


@fallback(False)
def login(uid, login_code):
    body = {"uid": uid, "login_code": login_code, "apiversion": apiversion}
    reponse = requests.post(urls.discord, json=body)
    result = reponse.json()

    if "new_id" in result:
        config.set("uid", result["new_id"])

    return result["success"]


@fallback(False)
def logout():
    body = {"uid": config.get("uid"), "apiversion": apiversion}
    reponse = requests.delete(urls.discord, json=body)
    result = reponse.json()
    return result["success"]


@fallback(None)
def register_user():
    ip = get_ip(GoogleDnsProvider)
    body = {"ip": ip, "apiversion": apiversion}
    response = requests.post(urls.user, json=body)
    result = response.json()
    return result["uid"]


@fallback(None)
def send_notification(message):
    if not is_subbed()[0]:
        return False

    body = {"uid": config.get("uid"), "message": message, "apiversion": apiversion}
    requests.post(urls.notify, json=body)


@uses_session
@fallback(None)
def send_fish_caught(fish_caught, hole_time, fish_times):
    hole_data = {
        "fish_caught": fish_caught,
        "hole_time": hole_time,
        "fish_times": fish_times,
        "session": get_session()
    }

    body = {"uid": config.get("uid"), "hole_data": hole_data, "apiversion": apiversion}
    requests.post(urls.hole_depleted, json=body)


@fallback(False)
def sub():
    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.post(urls.subscription, json=body)
    result = response.json()
    return result["success"]


@fallback((False, False))
def is_subbed():
    """
    :return: Tuple[is_subbed, success]
    """

    if config.get("uid") is None:
        return False, False

    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.get(urls.subscription, params=body)

    if response.status_code != 200:
        return False, False

    _is_subbed = response.json()["subbed"]
    return _is_subbed, True


@fallback(None)
def unsub():
    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.delete(urls.subscription, json=body)
    result = response.json()
    return result["success"]


def get_session(lazy=True):
    global _session_id

    # lazy loading logic
    if lazy and _session_id is not None:
        return _session_id

    # check if user has uid
    uid = config.get("uid")

    # then create session
    if uid:
        _session_id, online = _create_new_session(uid)
    # if not, create new id then try creating session again
    else:
        uid = register_user()
        config.set("uid", uid, True)
        logging.debug(f"New User, generated new uid: {uid}")
        if uid:
            _session_id, online = _create_new_session(uid)
        else:
            online = False

    # when the user is already registered but session is not created as uid is not found
    if online and not _session_id:
        logging.error("user not found, generating new uid.. contact dev if you don't want to loose data")
        new_uid = register_user()
        _session_id, online = _create_new_session(new_uid)
        config.set("uid", new_uid, True)
        config.set("old_uid", uid, True)

    return _session_id


@fallback((None, False))
def _create_new_session(uid):
    body = {"uid": uid, "apiversion": apiversion}
    response = requests.post(urls.session, params=body)

    if response.status_code == 405:
        return None, True

    return response.json()["session_id"], True


@fallback(False)
def has_beta():
    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.get(urls.beta, params=body)
    result = response.json()

    if not result["success"]:
        return False

    return response.json()["beta"]


@fallback(None)
def ping():
    body = {"uid": config.get("uid"), "apiversion": apiversion}
    response = requests.post(urls.ping, params=body)
    logging.debug(f"ping response: {response.json()}")
