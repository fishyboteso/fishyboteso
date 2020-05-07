import json
import os
from threading import Thread

filename = os.path.expanduser(r"~/Documents/fishy_config.json")


class Config:

    def __init__(self):
        self.config_dict = json.loads(open(filename).read()) if os.path.exists(filename) else dict()

    def get(self, key, default=None):
        if key in self.config_dict:
            return self.config_dict[key]
        return default

    def set(self, key, value, save=True):
        self.config_dict[key] = value
        if save:
            self.save_config()

    def delete(self, key):
        del self.config_dict[key]
        self.save_config()

    def save_config(self):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.config_dict))

