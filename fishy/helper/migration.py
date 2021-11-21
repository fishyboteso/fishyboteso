import logging

from fishy.helper.auto_update import _normalize_version

from fishy.constants import chalutier, version
from fishy.helper import helper
from .config import config


class Migration:
    @staticmethod
    def up_to_0_5_3():
        helper.remove_addon(*chalutier)
        config.delete("addoninstalled")

    @staticmethod
    def migrate():
        prev_version = _normalize_version(config.get("prev_version", "0.0.0"))
        current_version = _normalize_version(version)

        if current_version > prev_version:
            for v, f in migration_code:
                if prev_version < _normalize_version(v) <= current_version:
                    logging.info(f"running migration for {v}")
                    f()
            config.set("prev_version", version)



migration_code = [
    # version, upgrade_code
    ("0.5.3", Migration.up_to_0_5_3)
]
