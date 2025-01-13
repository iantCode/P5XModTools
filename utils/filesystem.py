import os
import winreg
from const.tables import REGION_MAP
from utils.settings import Setting

def is_client_installed():
    setting = Setting.instance()
    return os.path.exists(os.path.join(setting.game_location, "client", "pc"))


def get_filelocation_from_reg():
    try:
        setting = Setting.instance()

        keypath = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGION_MAP[setting.region]["reg_location"], 0, winreg.KEY_READ)
        return os.path.dirname(winreg.QueryValueEx(keypath, "DisplayIcon")[0])
    except:
        return None