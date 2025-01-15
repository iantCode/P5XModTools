from const.enums import Processing
from mod.mod_installer import ModInstaller
from utils.clean import environment_clean
from utils.settings import Setting
from utils.filesystem import is_client_installed

def mod_install(dialog, event):
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
        if mod_installer.is_mod_installed():
            dialog.update_browser_box(f"You already installed the mod. Please remove it first!")
            dialog.processing = Processing.NO
            return
        dialog.update_browser_box(f"Downloading Translation MOD")
        mod_installer.download()
        dialog.update_browser_box(f"Extracting and installing the Translation MOD")
        mod_installer.extract()
        dialog.update_browser_box(f"Checking the Program... Please Wait")
        if not mod_installer.is_mod_installed():
            dialog.update_browser_box(f"Looks like we had some error. Please try it again.")
            dialog.processing = Processing.NO
            return
        environment_clean()
        dialog.update_browser_box(f"Installing Done!")
        dialog.processing = Processing.NO
    except Exception as e:
        dialog.update_browser_box(str(e))
        dialog.processing = Processing.NO