import logging
from logging import StreamHandler, Formatter

from fishy.helper.config import config


class GuiLogger(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)

        self.renderer = None
        self._temp_buffer = []

        formatter = Formatter('%(levelname)s - %(message)s')
        self.setFormatter(formatter)
        logging_config = {"comtypes": logging.INFO,
                          "PIL": logging.INFO,
                          "urllib3": logging.WARNING,
                          "": logging.DEBUG}
        for name, level in logging_config.items():
            _logger = logging.getLogger(name)
            _logger.setLevel(level)
        self.setLevel(logging.DEBUG if config.get("debug", False) else logging.INFO)
        logging.getLogger("").addHandler(self)

    def emit(self, record):
        msg = self.format(record)
        if self.renderer:
            self.renderer(msg)
        else:
            self._temp_buffer.append(msg)

    def connect(self, gui):
        self.renderer = lambda m: gui.call_in_thread(lambda: gui.write_to_console(m))
        while self._temp_buffer:
            self.renderer(self._temp_buffer.pop(0))
