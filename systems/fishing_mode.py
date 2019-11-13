from systems.window import *


class FishingMode:
    """
    State machine for fishing modes

    HValues         hue values for each fishing mode
    CuurentCount    number of times same hue color is read before it changes state
    CurrentMode     current mode of the state machine
    PrevMode        previous mode of the state machine
    FishingStarted  probably does nothing (not sure though)
    Modes           list of states
    """
    HValues = [60, 18, 100]
    Threshold = int(arguments["--hook-threshold"])

    CurrentCount = 0
    PrevLabel = -1
    CurrentMode = None
    PrevMode = None
    FishingStarted = False

    Modes = []

    def __init__(self, name, label, event):
        """
        create a new state
        :param name: name of the state
        :param label: integer, label of the state (int)
        :param event: object of class containing onEnterCallback & onExitCallback functions
                        which are called when state is changed
        """
        self.name = name
        self.label = label
        self.event = event

        FishingMode.Modes.append(self)

    @staticmethod
    def GetByLabel(label):
        """
        find a state using label
        :param label: label integer
        :return: state
        """
        for m in FishingMode.Modes:
            if m.label == label:
                return m

    @staticmethod
    def Loop(hueValue, pause):
        """
        Executed in the start of the main loop in fishy.py
        Changes modes, calls mode events (callbacks) when mode is changed

        :param hueValue: huevValue read by the bot
        :param pause: true if bot is paused or not started
        """
        current_label = 3
        for i, val in enumerate(FishingMode.HValues):
            if hueValue == val:
                current_label = i

        # check if it passes threshold, if so change labelNum
        if FishingMode.PrevLabel == current_label:
            FishingMode.CurrentCount += 1
        else:
            FishingMode.CurrentCount = 0
        FishingMode.PrevLabel = current_label

        if FishingMode.CurrentCount >= FishingMode.Threshold:
            FishingMode.CurrentMode = FishingMode.GetByLabel(current_label)

        if not pause and FishingMode.CurrentMode != FishingMode.PrevMode and FishingMode.PrevMode is not None:

            if FishingMode.PrevMode.event is not None:
                FishingMode.PrevMode.event.onExitCallback(FishingMode.CurrentMode)

            if FishingMode.CurrentMode.event is not None:
                FishingMode.CurrentMode.event.onEnterCallback(FishingMode.PrevMode)

        FishingMode.PrevMode = FishingMode.CurrentMode
