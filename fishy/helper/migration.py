import logging

import fishy
from fishy.helper.auto_update import _normalize_version

from .config import config


class Migration:
    @staticmethod
    def up_to_0_5_3():
        config.delete("addoninstalled")

    @staticmethod
    def migrate():
        prev_version = _normalize_version(config.get("prev_version", "0.0.0"))
        current_version = _normalize_version(fishy.__version__)

        if current_version > prev_version:
            for v, f in migration_code:
                if prev_version < _normalize_version(v) <= current_version:
                    logging.info(f"running migration for {v}")
                    f()
            config.set("prev_version", fishy.__version__)



migration_code = [
    # version, upgrade_code
    ("0.5.3", Migration.up_to_0_5_3)
]
