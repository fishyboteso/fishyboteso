from logging import StreamHandler

import typing

if typing.TYPE_CHECKING:
    from . import GUI


class GUIStreamHandler(StreamHandler):
    def __init__(self, gui):
        StreamHandler.__init__(self)
        self.gui = gui

    def emit(self, record):
        from .comms import GUIFunction
        msg = self.format(record)
        self.gui.call(GUIFunction.LOG, (msg,))


def _write_to_console(root: 'GUI', msg):
    numlines = root._console.index('end - 1 line').split('.')[0]
    root._console['state'] = 'normal'
    if int(numlines) >= 50:  # delete old lines
        root._console.delete(1.0, 2.0)
    if root._console.index('end-1c') != '1.0':  # new line for each log
        root._console.insert('end', '\n')
    root._console.insert('end', msg)
    root._console.see("end")  # scroll to bottom
    root._console['state'] = 'disabled'
