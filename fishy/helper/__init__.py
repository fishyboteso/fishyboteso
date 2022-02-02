from .config import Config
from .helper import (addon_exists, create_shortcut, create_shortcut_first,
                     get_addonversion, get_savedvarsdir, initialize_uid,
                     install_addon, install_thread_excepthook, manifest_file,
                     not_implemented, open_web, playsound_multiple,
                     remove_addon, restart, unhandled_exception_logging,
                     update, install_required_addons)
from .luaparser import sv_color_extract
