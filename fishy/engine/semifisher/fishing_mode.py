class FishingMode:
    """
    State machine for fishing modes

    HValues         hue values for each fishing mode
    CurrentCount    number of times same hue color is read before it changes state
    CurrentMode     current mode of the state machine
    PrevMode        previous mode of the state machine
    FishingStarted  probably does nothing (not sure though)
    Modes           list of states
    """
    HValues = [60, 18, 100]
    Threshold = 1

    CurrentCount = 0
    PrevLabel = -1
    CurrentMode = None
    PrevMode = None

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
    def get_by_label(label):
        """
        find a state using label
        :param label: label integer
        :return: state
        """
        for m in FishingMode.Modes:
            if m.label == label:
                return m

    @staticmethod
    def loop(hue_values):
        """
        Executed in the start of the main loop in fishy.py
        Changes modes, calls mode events (callbacks) when mode is changed

        :param hue_values: hue_values read by the bot
        """
        current_label = 3
        for i, val in enumerate(FishingMode.HValues):
            if hue_values == val:
                current_label = i

        # check if it passes threshold, if so change labelNum
        if FishingMode.PrevLabel == current_label:
            FishingMode.CurrentCount += 1
        else:
            FishingMode.CurrentCount = 0
        FishingMode.PrevLabel = current_label

        if FishingMode.CurrentCount >= FishingMode.Threshold:
            FishingMode.CurrentMode = FishingMode.get_by_label(current_label)

        if FishingMode.CurrentMode != FishingMode.PrevMode and FishingMode.PrevMode is not None:

            if FishingMode.PrevMode.event is not None:
                FishingMode.PrevMode.event.on_exit_callback(FishingMode.CurrentMode)

            if FishingMode.CurrentMode.event is not None:
                FishingMode.CurrentMode.event.on_enter_callback(FishingMode.PrevMode)

        FishingMode.PrevMode = FishingMode.CurrentMode
