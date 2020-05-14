import sys

domain = "http://127.0.0.1:5000" if "--local-server" in sys.argv else "https://fishyeso.herokuapp.com"

user = domain + "/api/user"
notify = domain + "/api/notify"
subscription = domain + "/api/subscription/"
hole_depleted = domain + "/api/hole_depleted"
session = domain + "/api/session"
terms = domain + "/terms.html"


def get_notification_page(uid):
    return domain + f"?uid={uid}"


def get_terms_page():
    return terms
