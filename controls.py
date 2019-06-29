from init import *


class Control:
    """
    Input system for the bot.

    variables
    current:    current mode of the input
    controls:   Maps different key to different keyword depending on the current mode
    """
    current = 1 if arguments["--debug"] else 0

    class Keywords(Enum):
        """
        Enums which define different functionality to be called
        used in `fishy.py` to run different code depending on which keyword is used
        """
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
        """
        creates a control help string depending on the current mode
        :return: string
        """
        s = "\n\nCurrent Mode: " + Control.get()["name"]+"\n"
        for c in Control.controls[Control.current]["controls"]:
            s += c[0].value + ": " + c[1].name + "\n"

        return s

    @staticmethod
    def get():
        """
        returns the controls current mode control array
        :return:  control array
        """
        return Control.controls[Control.current]

    @staticmethod
    def find(key):
        """
        converts key into the control keyword
        :param key: key pressed
        :return: corresponding keyword
        """
        for c in Control.get()["controls"]:
            if key == c[1]:
                return c

        return None

    @staticmethod
    def nextState():
        """
        Changes the current mode
        """
        Control.current += 1

        if Control.current >= len(Control.controls):
            Control.current = 0
