from init import *


class Control:
    current = 1 if arguments["--debug"] else 0

    class Keywords(Enum):
        SwitchMode = "switch mode"
        StartPause = "start/pause"
        Debug = "debug"
        Stop = "stop"
        ClearPrintOnce = "clear print once"

    controls = [
        {
            "name": "SYSTEM",
            "controls": [
                [Keywords.SwitchMode, Key.f8],
                [Keywords.StartPause, Key.f9],
                [Keywords.Stop, Key.f11]
            ]
        },
        {
            "name": "DEBUG",
            "controls": [
                [Keywords.SwitchMode, Key.f8],
                [Keywords.ClearPrintOnce, Key.f9],
                [Keywords.Debug, Key.f10],
            ]
        }
    ]


    @staticmethod
    def getControlHelp():
        s = "\n\nCurrent Mode: " + Control.get()["name"]+"\n"
        for c in Control.controls[Control.current]["controls"]:
            s += c[0].value + ": " + c[1].name + "\n"

        return s

    @staticmethod
    def get():
        return Control.controls[Control.current]

    @staticmethod
    def find(key):
        for c in Control.get()["controls"]:
            if key == c[1]:
                return c

        return None

    @staticmethod
    def nextState():
        Control.current += 1

        if Control.current >= len(Control.controls):
            Control.current = 0
