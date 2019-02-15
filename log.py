from controls import *


class Log:
    ouUsed = False
    prevOuUsed = False
    printIds = []

    @staticmethod
    def Loop():
        Log.ouUsed = False

    @staticmethod
    def LoopEnd():
        if Log.prevOuUsed and not Log.ouUsed:
            Log.ctrl()
        Log.prevOuUsed = Log.ouUsed

    @staticmethod
    def ctrl():
        print(Control.getControlHelp())

    @staticmethod
    def ou(s):
        Log.ouUsed = True
        print(s)

    @staticmethod
    def po(id, s):
        if id not in Log.printIds:
            print(s)
            Log.printIds.append(id)

    @staticmethod
    def clearPrintIds():
        Log.printIds = []

