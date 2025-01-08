import os
from utils.settings import Setting

def is_client_installed():
    setting = Setting.instance()
    return os.path.exists(os.path.join(setting.game_location, "client", "pc"))