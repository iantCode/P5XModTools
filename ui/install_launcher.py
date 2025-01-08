import asyncio
from const.enums import Processing
from launcher.launcher_install import LauncherInstaller
from utils.clean import environment_clean, safe_remove
from utils.settings import Setting
from threading import Event

def launcher_download_and_install(dialog, event: Event):
    setting = Setting.instance()
    launcher_installer = LauncherInstaller.instance()

    try:
        if setting.game_location == "":
            dialog.update_browser_box(f"You need to set the location of the game!")
            return
            
        dialog.processing = Processing.LAUNCHER
        dialog.update_browser_box(f"Cleaning Environment...")
        environment_clean()
        dialog.update_browser_box(f"Checking launcher version")
        version = launcher_installer.get_latest_launcher_version(event)
        if version:
            dialog.update_browser_box(f"Newest version: {version}")
            dialog.update_browser_box(f"Now Downloading the launcher. It will take some time.")
            safe_remove('./version.ini')
            result = asyncio.run(launcher_installer.install_launcher_from_server(event))
            if result:
                dialog.update_browser_box(f"Finish installing the launcher.")
            else:
                dialog.update_browser_box(f"There was some problem downloading the launcher. Please try once more!")
            dialog.processing = Processing.NO
        else:
            dialog.update_browser_box(f"Something bad happened while getting launcher version")
            dialog.processing = Processing.NO
    except Exception as e:
        dialog.update_browser_box(str(e))
        dialog.processing = Processing.NO