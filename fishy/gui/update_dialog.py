import logging
import tkinter as tk

from fishy.helper import helper, auto_update
from fishy.helper.config import config
from fishy.helper.popup import PopUp


def _show(gui, currentversion, newversion, returns):

    def _clickYes():
        returns[0], returns[1] = True, False
        top.quit_top()

    def _clickNo():
        returns[0], returns[1] = False, bool(cbVar.get())
        top.quit_top()

    top = PopUp(helper.empty_function, gui._root)
    top.title("A wild fishy update appeared!")

    dialogLabel = tk.Label(top, text="There is a new fishy update available (" +
                           currentversion + "->" + newversion + "). Do you want to update now?")
    dialogLabel.grid(row=0, columnspan=2, padx=5, pady=5)

    cbVar = tk.IntVar()
    dialogCheckbutton = tk.Checkbutton(top, text="don't ask again", variable=cbVar)
    dialogCheckbutton.grid(row=1, columnspan=2, padx=5, pady=0)
    top.update()
    buttonWidth = int(dialogLabel.winfo_width() / 2) - 20

    pixelVirtual = tk.PhotoImage(width=1, height=1)  # trick to use buttonWidth as pixels, not #symbols
    dialogBtnNo = tk.Button(top, text="No " + str(chr(10005)), fg='red4', command=_clickNo, image=pixelVirtual,
                            width=buttonWidth, compound="c")
    dialogBtnNo.grid(row=2, column=0, padx=5, pady=5)
    dialogBtnYes = tk.Button(top, text="Yes " + str(chr(10003)), fg='green', command=_clickYes, image=pixelVirtual,
                             width=buttonWidth, compound="c")
    dialogBtnYes.grid(row=2, column=1, padx=5, pady=5)
    dialogBtnYes.focus_set()
    dialogBtnYes.update()

    top.protocol('WM_DELETE_WINDOW', _clickNo)
    top.start()


def check_update(gui, manual_check=False):
    if not auto_update.upgrade_avail() or config.get("dont_ask_update", False):
        if manual_check:
            logging.info("No update is available.")
        return

    cv, hv = auto_update.versions()
    returns = [None, None]
    _show(gui, cv, hv, returns)
    [update_now, dont_ask_update] = returns
    if dont_ask_update:
        config.set("dont_ask_update", dont_ask_update)
    else:
        config.delete("dont_ask_update")

    if update_now:
        gui.engine.set_update(hv)
