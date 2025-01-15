import asyncio
import shutil
import os
from const.tables import MOD_LINK
from utils.clean import safe_remove
from utils.settings import Setting
from utils.singleton import SingletonInstance
from utils.download import Downloader
from utils.filesystem import move

class ModInstaller(SingletonInstance):
    def download(self):
        download = Downloader.instance()
        setting = Setting.instance()

        asyncio.run(download.download(MOD_LINK[setting.region], "p5xmod.zip"))

    def extract(self):
        setting = Setting.instance()

        shutil.unpack_archive("p5xmod.zip", "temp", "zip")
        safe_remove('./p5xmod.zip')
        move("temp", os.path.join(setting.game_location, "client", "pc"))


    def uninstall(self):
        setting = Setting.instance()
        client_location = os.path.join(setting.game_location, "client\\pc")

        shutil.rmtree(os.path.join(client_location, "BepInEx"), ignore_errors=True)
        shutil.rmtree(os.path.join(client_location, "dotnet"), ignore_errors=True)
        safe_remove(os.path.join(client_location, ".doorstop_version"))
        safe_remove(os.path.join(client_location, "changelog.txt"))
        safe_remove(os.path.join(client_location, "doorstop_config.ini"))
        safe_remove(os.path.join(client_location, "winhttp.dll"))
        safe_remove(os.path.join(client_location, "Credits.txt"))
        safe_remove(os.path.join(client_location, "IF YOU HAVE ISSUES WITH THE AUTODOWNLOADER.txt"))
        safe_remove(os.path.join(client_location, "ReadMe.txt"))
        safe_remove(os.path.join(client_location, "Troubleshooting.pdf"))

    def is_mod_installed(self):
        setting = Setting.instance()
        client_location = os.path.join(setting.game_location, "client\\pc")

        return os.path.exists(os.path.join(client_location, "BepInEx"))\
            and os.path.exists(os.path.join(client_location, "winhttp.dll"))\
            and os.path.exists(os.path.join(client_location, "BepInEx\\unity-libs\\UnityEngine.dll"))\
            and os.path.exists(os.path.join(client_location, "BepInEx\\interop\\Assembly-CSharp.dll"))