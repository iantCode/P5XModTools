import os
import shutil
from const.enums import Processing
from utils.clean import environment_clean, safe_remove
from utils.settings import Setting
from utils.filesystem import is_client_installed

def mod_uninstall(dialog, event):
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
        dialog.update_browser_box(f"Checking Your Client")
        client_location = os.path.join(setting.game_location, "client\\pc")
        if is_mod_installed(client_location):
            remove_mod_from_client(client_location)
            dialog.update_browser_box(f"Translation mod has been removed successfully.")
            dialog.processing = Processing.NO
        else:
            dialog.update_browser_box(f"You didn't install the mod!")
            dialog.processing = Processing.NO
                
    except:
        dialog.processing = Processing.NO


def is_mod_installed(client_location: str):
    return os.path.exists(os.path.join(client_location, "BepInEx"))\
        or os.path.exists(os.path.join(client_location, "winhttp.dll"))

def remove_mod_from_client(client_location: str):
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