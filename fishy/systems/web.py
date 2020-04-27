import requests

from fishy.systems.globals import G
from fishy.systems.helper import disable_logging

domain = "https://fishyeso.herokuapp.com"

user = "/api/user"
notify = "/api/notify"
subscription = "/api/subscription/"


@disable_logging
def register_user(uid):
    body = {"uid": uid}
    response = requests.post(domain + user, json=body)
    print(response.status_code)
    return response.ok and response.json()["success"]


def get_notification_page(uid):
    return domain+f"?uid={uid}"


@disable_logging
def send_notification(uid, message):
    if not is_subbed(uid):
        return False

    body = {"uid": uid, "message": message}
    response = requests.post(domain + notify, json=body)
    return response.json()["success"], response.json()["error"]


def send_hole_deplete(uid, fishes_caught):
    send_notification(uid, f"Hole depleted, {fishes_caught} fishes caught!")


@disable_logging
def is_subbed(uid, lazy=True):
    if lazy and G._is_subbed is not None:
        return G._is_subbed

    if uid is None:
        return False

    body = {"uid": uid}
    response = requests.get(domain + subscription, params=body)
    G._is_subbed = response.json()["subbed"]
    return G._is_subbed


@disable_logging
def unsub(uid):
    G._is_subbed = False
    body = {"uid": uid}
    requests.delete(domain + subscription, json=body)
