import os
import winreg
import hashlib
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
    

def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()