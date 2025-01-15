import time
from const.enums import Processing
from mod.mod_installer import ModInstaller
from utils.clean import environment_clean
from utils.settings import Setting
from utils.filesystem import is_client_installed

def mod_uninstall(dialog, event):
    setting = Setting.instance()
    mod_installer = ModInstaller.instance()
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
        if mod_installer.is_mod_installed():
            mod_installer.uninstall()
            dialog.update_browser_box(f"Translation mod has been removed successfully.")
            dialog.processing = Processing.NO
        else:
            dialog.update_browser_box(f"You didn't install the mod!")
            dialog.processing = Processing.NO
                
    except Exception as e:
        dialog.update_browser_box(str(e))
        dialog.processing = Processing.NO