import subprocess
import re
import os
from Xlib import display
from typing import Tuple, Optional
from xdg.DesktopEntry import DesktopEntry

from fishy.osservices.os_services import IOSServices

class Linux(IOSServices):

    def hide_terminal(self):
        window_title = 'Terminal'
        command = f'wmctrl -r "{window_title}" -b add,hidden'
        subprocess.run(command, shell=True, check=True)

    def create_shortcut(self, anti_ghosting=False):
        try:
            desktop_file = os.path.expanduser("~/Desktop/Fishybot ESO.desktop")
            shortcut = DesktopEntry(desktop_file)
            shortcut.set("Type", "Application")

            if anti_ghosting:
                shortcut.set("Exec", "/usr/bin/python3 -m fishy")
            else:
                shortcut.set("Exec", "/usr/bin/python3 -m fishy")

            shortcut.set("Icon", "icon.png") # TODO : Fix icon address
            shortcut.write()

            print("Shortcut created")
        except Exception:
            print("Couldn't create shortcut")

    def get_documents_path(self) -> str:
        return os.path.join(os.path.expanduser('~'), "Documents")

    def is_admin(self) -> bool:
        return os.geteuid() == 0

    def get_eso_config_path(self) -> str:
        documents = os.path.expanduser("~/Documents")
        return os.path.join(documents, "Elder Scrolls Online")

    def is_eso_active(self) -> bool:
        d = display.Display()
        root = d.screen().root
        window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), display.X.AnyPropertyType).value[0]
        window = d.create_resource_object('window', window_id)
        window_name = window.get_wm_name()
        return window_name == "Elder Scrolls Online"

    def get_monitor_rect(self):
        try:
            output = subprocess.check_output(["xrandr"]).decode("utf-8")
            matches = re.findall(r"(\d+)x(\d+)\+(\d+)\+(\d+)", output)
            if matches:
                width, height, x, y = matches[0]
                return {
                    "width": int(width),
                    "height": int(height),
                    "x": int(x),
                    "y": int(y)
                }
            else:
                return None
        except subprocess.CalledProcessError:
            return None

    def get_game_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        d = display.Display()
        root = d.screen().root
        window_id = None

        # پیدا کردن پنجره با نام مشخص
        window_attributes = root.query_tree().children
        for window in window_attributes:
            window_name = window.get_wm_name()
            if window_name == "Elder Scrolls Online":
                window_id = window.id
                break

        if window_id is None:
            return None

        window_geometry = root.get_geometry()
        window_rect = window.get_geometry()
        game_rect = (
            window_rect.x,
            window_rect.y,
            window_rect.x + window_geometry.width,
            window_rect.y + window_geometry.height
        )

        return game_rect
