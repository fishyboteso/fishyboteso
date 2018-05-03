import socket
import json
from socket import timeout
import time

PORT = 8023
MESSAGE = "yo"
RETRY_LIMIT = 5
IP = 0

def initialize(ip):
    global s, IP
    IP = ip

def send_message(message, count=1):
    try:
        s = socket.socket()
        s.connect((IP,PORT))
        s.send(bytes(message, "utf-8"))
        s.close()
    except ConnectionRefusedError:
        print("Connection Refused, please turn on service on mobile")
    except TimeoutError:
        print("Timeout Error")

        if count < RETRY_LIMIT:
            send_message(message, count+1)
        

def sendHoleDeplete(count):
    message = {"action":"holeDeplete", "fishCount": count}
    jsonString = json.dumps(message)
    send_message(jsonString)


##initialize("192.168.0.192")
##sendHoleDeplete(2)
