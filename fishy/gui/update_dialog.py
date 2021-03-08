from multiprocessing import Process, Manager
from tkinter import *
import time

def show(currentversion, newversion, returns):
    top = Tk()
    top.title("A wild update appears!")

    dialogLabel = Label(top, text="There is a new update available ("+currentversion+"->"+newversion+"). Do you want to update now?")
    dialogLabel.grid(row=0, columnspan=2, padx=5, pady=5)

    cbVar = IntVar()
    dialogCheckbutton = Checkbutton(top, text="don't ask again", variable=cbVar)
    dialogCheckbutton.grid(row=1, columnspan=2, padx=5, pady=0)
    top.update()
    buttonWidth = int(dialogLabel.winfo_width()/2)-20

    def _clickYes():
        returns[0],returns[1]=True, False
        top.destroy()

    def _clickNo():
        returns[0],returns[1]=False, bool(cbVar.get())
        top.destroy()

    pixelVirtual = PhotoImage(width=1, height=1) # trick to use buttonWidth as pixels, not #symbols
    dialogBtnYes = Button(top, text="Yes " + str(chr(10003)),  fg='green', command=_clickYes, image=pixelVirtual, width=buttonWidth, compound="c")
    dialogBtnYes.grid(row=2, column=0, padx=5, pady=5)
    dialogBtnNo = Button(top, text="No " + str(chr(10005)),  fg='red', command=_clickNo, image=pixelVirtual, width=buttonWidth, compound="c")
    dialogBtnNo.grid(row=2, column=1, padx=5, pady=5)

    top.protocol('WM_DELETE_WINDOW', _clickNo)

    top.update()
    top.mainloop()


def start(currentversion, newversion):
    returns = Manager().dict()
    p = Process(target=show, args=(currentversion, newversion, returns))
    p.start()
    p.join()
    return returns[0], returns[1]
