import json
import os

filename = "config.json"


class Config:

    def __init__(self):
        self.config_dict = json.loads(open(filename).read()) if os.path.exists(filename) else dict()

    def get(self, key, default=None):
        if key in self.config_dict:
            return self.config_dict[key]
        return default

    def set(self, key, value):
        self.config_dict[key] = value
        self.save_config()

    def save_config(self):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.config_dict))
