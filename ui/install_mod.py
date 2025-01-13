import asyncio
import os
import shutil
from const.enums import Processing
from const.tables import MOD_LINK
from utils.clean import environment_clean, safe_remove
from utils.download import Downloader
from utils.settings import Setting
from utils.filesystem import is_client_installed

def mod_install(dialog, event):
    download = Downloader.instance()
    setting = Setting.instance()

    try:
        if setting.game_location == "":
            dialog.update_browser_box(f"You need to set the location of the game!")
            return
        
        if not is_client_installed():
            dialog.update_browser_box(f"I cannot find P5X Client files. Make sure you download the game!")
            return
        
        dialog.processing = Processing.MOD
        dialog.update_browser_box(f"Cleaning Environment...")
        environment_clean()
        dialog.update_browser_box(f"Downloading Translation MOD")
        asyncio.run(download.download(MOD_LINK[setting.region], "p5xmod.zip"))
        dialog.update_browser_box(f"Extracting and installing the Translation MOD")
        shutil.unpack_archive("p5xmod.zip", os.path.join(setting.game_location, "client", "pc"), "zip")
        safe_remove('./p5xmod.zip')
        dialog.update_browser_box(f"Installing Done!")
        dialog.processing = Processing.NO
    except:
        dialog.processing = Processing.NO