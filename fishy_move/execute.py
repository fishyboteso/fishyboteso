import pynput

import time
from threading import Timer

offsetTime = 3.0

fo = open("record.txt", "r")

keys = {"w":'w', "a":'a', "s":'s', "d":'d', "space":pynput.keyboard.Key.space, "up":pynput.keyboard.Key.up, "down":pynput.keyboard.Key.down, "left":pynput.keyboard.Key.left, "right":pynput.keyboard.Key.right}

recordList = []

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()


class Record:

    def __init__(self, c, dt, ut):
        self.char = c
        self.downTime = dt
        self.upTime = ut
        self.obj = keys[c]

    def shedule(self):
        Timer(offsetTime+self.downTime, keyboard.press, [self.obj]).start()
        Timer(offsetTime+self.upTime, keyboard.release, [self.obj]).start()

    def __str__(self):
        return "press "+self.char+" from "+str(self.downTime)+ " to "+str(self.upTime)

def moveMouse(x,y):
    mouse.position = (x,y)

def sheduleMouse(x,y,t):
    Timer(offsetTime+t, moveMouse, [x,y]).start() 

strInst = fo.read()

instList = strInst.split("\n")

for i in instList:
    if i == "":
        break
    instParts = i.split(":")

    if instParts[0] == "mouse" :
        sheduleMouse(int(instParts[1]),int(instParts[2]),float(instParts[3]))
    else:
        recordList.append(Record(instParts[0], float(instParts[1]), float(instParts[2])))

for i in recordList:
    i.shedule()


Timer(offsetTime, print, ["gooooooooooo!!!!"]).start()


fo.close()

        
