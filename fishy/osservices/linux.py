import os
from Xlib import *
from typing import Tuple, Optional

from fishy.osservices.os_services import IOSServices


class Linux(IOSServices):
    def hide_terminal(self):
        pass

    def create_shortcut(self):
        pass

    def get_documents_path(self) -> str:
        pass

    def is_admin(self) -> bool:
        if os.geteuid() == 0:
            return "The program is running as root"
        else:
            return "The program is not running as root"


    def get_eso_config_path(self) -> str:
        pass

    def is_eso_active(self) -> bool:
        d = display.Display()
        root = d.screen().root
        window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), X.AnyPropertyType).value[0]
        window = d.create_resource_object('window', window_id)
        window_name = window.get_wm_name()
        return window_name == "Elder Scrolls Online"

    def get_monitor_rect(self):
        pass

    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        pass
