from window import *


class FishingMode:
    HValues = [60, 18, 100]
    Threshold = int(arguments["--hook-threshold"])

    CurrentCount = 0
    PrevLabel = -1
    CurrentMode = None
    PrevMode = None

    Modes = []

    def __init__(self, name, label, event):
        self.name = name
        self.label = label
        self.event = event

        FishingMode.Modes.append(self)

    @staticmethod
    def GetByLabel(label):
        for m in FishingMode.Modes:
            if m.label == label:
                return m

    @staticmethod
    def Loop(hueValue, pause):
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

