import requests
from whatsmyip.ip import get_ip
from whatsmyip.providers import GoogleDnsProvider

from fishy import helper
from . import urls
from .decorators import fallback, uses_session
from ..helper.config import config
from .constants import apiversion

_session_id = None


@fallback(-1)
def is_logged_in():
    if config.get("uid") is None:
        return -1

    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.get(urls.discord, params=body)
    logged_in = response.json()["discord_login"]
    return 1 if logged_in else 0


@fallback(False)
def login(uid, login_code):
    body = {"uid": uid, "login_code": login_code, "apiversion":apiversion}
    reponse = requests.post(urls.discord, json=body)
    result = reponse.json()

    if "new_id" in result:
        config.set("uid", result["new_id"])

    return result["success"]


@fallback(False)
def logout():
    body = {"uid": config.get("uid"), "apiversion":apiversion}
    reponse = requests.delete(urls.discord, json=body)
    result = reponse.json()
    return result["success"]


@fallback(False)
def register_user(new_uid):
    ip = get_ip(GoogleDnsProvider)
    body = {"uid": new_uid, "ip": ip, "apiversion":apiversion}
    response = requests.post(urls.user, json=body)
    return response.ok and response.json()["success"]


@fallback(None)
def send_notification(uid, message):
    # todo clean dead code
    if not is_subbed(uid):
        return False

    body = {"uid": uid, "message": message, "apiversion":apiversion}
    requests.post(urls.notify, json=body)


@uses_session
@fallback(None)
def send_hole_deplete(fish_caught, hole_time, fish_times):
    hole_data = {
        "fish_caught": fish_caught,
        "hole_time": hole_time,
        "fish_times": fish_times,
        "session": get_session()
    }

    body = {"uid": config.get("uid"), "hole_data": hole_data, "apiversion":apiversion}
    requests.post(urls.hole_depleted, json=body)


@fallback(False)
def sub():
    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.post(urls.subscription, json=body)
    result = response.json()
    return result["success"]


@fallback((False, False))
def is_subbed():
    """
    :param uid:
    :param lazy:
    :return: Tuple[is_subbed, success]
    """

    if config.get("uid") is None:
        return False, False

    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.get(urls.subscription, params=body)

    if response.status_code != 200:
        return False, False

    is_subbed = response.json()["subbed"]
    return is_subbed, True


@fallback(None)
def unsub():
    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.delete(urls.subscription, json=body)
    result = response.json()
    return result["success"]


@fallback(None)
def get_session(lazy=True):
    global _session_id

    if lazy and _session_id is not None:
        return _session_id

    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.post(urls.session, params=body)

    if response.status_code == 405:
        config.delete("uid")
        helper.restart()
        return None

    _session_id = response.json()["session_id"]
    return _session_id


@fallback(False)
def has_beta():
    body = {"uid": config.get("uid"), "apiversion":apiversion}
    response = requests.get(urls.beta, params=body)
    result = response.json()

    if not result["success"]:
        return False

    return response.json()["beta"]
