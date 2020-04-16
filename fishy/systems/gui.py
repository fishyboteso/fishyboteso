from tkinter import *


def start():
    writeToLog(console, "yo")


def writeToLog(log, msg):
    numlines = log.index('end - 1 line').split('.')[0]
    log['state'] = 'normal'
    if int(numlines) >= 50:  # delete old lines
        log.delete(1.0, 2.0)
    if log.index('end-1c') != '1.0':  # new line for each log
        log.insert('end', '\n')
    log.insert('end', msg)
    log.see("end")  # scroll to bottom
    log['state'] = 'disabled'


root = Tk()
root.title("Fiishybot for Elder Scrolls Online")
root.geometry('600x600')

# region menu
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Create Shortcut", command=start)
menubar.add_cascade(label="File", menu=filemenu)

debug_menu = Menu(menubar, tearoff=0)
debug_menu.add_command(label="Check PixelVal", command=start)
debug_menu.add_command(label="LogDump", command=start)
menubar.add_cascade(label="Debug", menu=debug_menu)
root.config(menu=menubar)
# endregion

# region console
console = Text(root, state='disabled', wrap='none')
console.pack(fill=BOTH, expand=True, pady=(15, 15), padx=(5, 5))
console.mark_set("sentinel", INSERT)
console.config(state=DISABLED)

controls_frame = Frame(root)
# endregion

# region controls
left_frame = Frame(controls_frame)

Label(left_frame, text="IP").grid(row=0, column=0)
ip = Entry(left_frame)
ip.grid(row=0, column=1)

Label(left_frame, text="Fullscreen: ").grid(row=1, column=0, pady=(5, 5))
borderless = Checkbutton(left_frame)
borderless.grid(row=1, column=1)

left_frame.grid(row=0, column=0)

right_frame = Frame(controls_frame)

Label(right_frame, text="Action Key:").grid(row=0, column=0)
action_key_entry = Entry(right_frame)
action_key_entry.grid(row=0, column=1)
action_key_entry.insert(0, "e")

Label(right_frame, text="Press start").grid(row=1, columnspan=2, pady=(5, 5))

right_frame.grid(row=0, column=1, padx=(50, 0))

controls_frame.pack()
Button(root, text="START", width=25, command=start).pack(pady=(15, 15))
# endregion

# root.update()

# root.minsize(root.winfo_width(), root.winfo_height())
root.mainloop()
