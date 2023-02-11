import re
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

from PIL import Image, ImageTk

from fishy import helper, web
from fishy.helper.config import config

hyperlinkPattern = re.compile(r'\[(?P<title>.*?)\]\((?P<address>.*?)\)')


def check_eula():
    if not config.get("eula", False):
        _run_terms_window()
        return config.get("eula", False)

    return config.get("eula", False)


def _run_terms_window():
    def accept():
        config.set("eula", True)
        root.destroy()

    def disable_enable_button():
        accept_button.config(state=tk.NORMAL if check_value.get() else tk.DISABLED)

    root = tk.Tk()
    message = f'I agree to the [Terms of Service and Privacy Policy]({web.get_terms_page()})'
    root.title("EULA")
    root.resizable(False, False)
    root.iconbitmap(helper.manifest_file('icon.ico'))

    f = ttk.Frame(root)
    canvas = tk.Canvas(f, width=300, height=200)
    canvas.pack()
    root.image = Image.open(helper.manifest_file('fishybot_logo.png')).resize((300, 200))
    root.image = ImageTk.PhotoImage(root.image)
    canvas.create_image(0, 0, anchor=tk.NW, image=root.image)

    check_value = tk.IntVar()

    g1 = ttk.Frame(f)
    ttk.Checkbutton(g1, command=disable_enable_button, variable=check_value).pack(side=tk.LEFT)
    text = tk.Text(g1, width=len(hyperlinkPattern.sub(r'\g<title>', message)),
                   height=1, borderwidth=0, highlightthickness=0)
    text["background"] = root["background"]

    _format_hyper_link(text, message)
    text.config(state=tk.DISABLED)
    text.pack(side=tk.LEFT)
    g1.pack()

    f.pack(padx=(10, 10), pady=(20, 20))

    g2 = ttk.Frame(f)
    accept_button = ttk.Button(g2, text="Accept",
                               command=accept)
    accept_button.grid(row=0, column=0)
    ttk.Button(g2, text="Deny",
               command=lambda: root.destroy()).grid(row=0, column=1)
    g2.pack(pady=(5, 0))
    disable_enable_button()

    root.mainloop()


def _format_hyper_link(text, message):
    start = 0
    for index, match in enumerate(hyperlinkPattern.finditer(message)):
        groups = match.groupdict()
        text.insert("end", message[start: match.start()])
        # insert hyperlink tag here
        text.insert("end", groups['title'])
        text.tag_add(str(index),
                     "end-%dc" % (len(groups['title']) + 1),
                     "end", )
        text.tag_config(str(index),
                        foreground="blue",
                        underline=1)
        text.tag_bind(str(index),
                      "<Enter>",
                      lambda *a, **k: text.config(cursor="hand2"))
        text.tag_bind(str(index),
                      "<Leave>",
                      lambda *a, **k: text.config(cursor="arrow"))
        text.tag_bind(str(index),
                      "<Button-1>",
                      lambda x: webbrowser.open(groups['address']))
        start = match.end()
    else:
        text.insert("end", message[start:])
