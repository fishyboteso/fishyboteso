from controls import *


class Log:
    """
    Simple logging script
    """
    ouUsed = False
    prevOuUsed = False
    printIds = []

    @staticmethod
    def Loop():
        """
        Method to be called in the start of the main loop
        """
        Log.ouUsed = False

    @staticmethod
    def LoopEnd():
        """
        method to be called in the end of the main loop
        """
        if Log.prevOuUsed and not Log.ouUsed:
            Log.ctrl()
        Log.prevOuUsed = Log.ouUsed

    @staticmethod
    def ctrl():
        """
        Logs the control manual for the current control state
        """
        print(Control.getControlHelp())

    @staticmethod
    def ou(s):
        """
        Logging output which is supposed to dumps alot of data,
        so that after it ends, controls help is printed again
        :param s: stirng to log
        """
        Log.ouUsed = True
        print(s)

    @staticmethod
    def po(id, s):
        """
        print once
        logs the stirng passed only once event if it is called multiple times
        :param id: unique integer
        :param s: string to log
        """
        if id not in Log.printIds:
            print(s)
            Log.printIds.append(id)

    @staticmethod
    def clearPrintIds():
        """
        clears print id for print once, so that it is printed again
        """
        Log.printIds = []

