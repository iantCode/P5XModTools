import os
import winreg
import hashlib
import shutil
from const.tables import REGION_MAP
from utils.settings import Setting
from utils.clean import safe_remove

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


def move(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                safe_remove(dst_file)
            shutil.move(src_file, dst_dir)
            

def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()