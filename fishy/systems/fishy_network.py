import logging
import socket
import json

PORT = 8023
MESSAGE = "yo"
RETRY_LIMIT = 5
IP = 0
s = None


def initialize(ip):
    global s, IP
    IP = ip


def send_message(message, count=1):
    try:
        sock = socket.socket()
        sock.connect((IP, PORT))
        sock.send(bytes(message, "utf-8"))
        sock.close()
    except ConnectionRefusedError:
        logging.info("Connection Refused, please turn on service on mobile")
    except TimeoutError:
        logging.info("Timeout Error")

        if count < RETRY_LIMIT:
            send_message(message, count+1)
        

def sendHoleDeplete(count):
    message = {"action": "holeDeplete", "fishCount": count}
    jsonString = json.dumps(message)
    send_message(jsonString)


if __name__ == "__main__":
    initialize("192.168.0.192")
    sendHoleDeplete(2)
