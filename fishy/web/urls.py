import sys

if "--local-server" in sys.argv:
    domain = "http://127.0.0.1:5000"
elif "--test-server" in sys.argv:
    domain = "https://fishyeso-test.definex.in"
else:
    domain = "https://fishyeso.definex.in"

user = domain + "/api/user"
notify = domain + "/api/notify"
subscription = domain + "/api/notify_semifish"
hole_depleted = domain + "/api/hole_depleted"
session = domain + "/api/session"
terms = domain + "/terms.html"
discord = domain + "/api/discord"
beta = domain + "/api/beta"
ping = domain + "/api/ping"


def get_notification_page(uid):
    return domain + f"?uid={uid}"


def get_terms_page():
    return terms
