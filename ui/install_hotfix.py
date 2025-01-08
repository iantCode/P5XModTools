import asyncio
from const.enums import Processing
from hotfix.hotfix import HotfixPatcher
from utils.clean import environment_clean
from utils.settings import Setting
from threading import Event

def hotfix_download_and_install(dialog, event: Event):
    setting = Setting.instance()
    hotfix_patcher = HotfixPatcher.instance()

    try:
        if setting.game_location == "":
            dialog.update_browser_box(f"You need to set the location of the game!")
            return
        
        dialog.processing = Processing.HOTFIX
        dialog.update_browser_box(f"Cleaning Environment...")
        environment_clean()
        dialog.update_browser_box(f"Checking hotfix version")
        line, version = hotfix_patcher.get_version()
        dialog.update_browser_box(f"Detected Line: {line} Version: {version}")
        target_version = asyncio.run(hotfix_patcher.get_target_version())

        if target_version > 0:
            dialog.update_browser_box(f"New Version {target_version} has been found. Downloading the hotfix.")
            dialog.processing = Processing.MOD # for enabling progress bar tracks download bar.
            target_version = asyncio.run(hotfix_patcher.download_hotfix(event))
            dialog.update_browser_box(f"Downloading hotfix has finished, now extracting and patching the game.")
            dialog.processing = Processing.HOTFIX
            hotfix_patcher.apply_patch(event)
            dialog.update_browser_box(f"Hotfix was successfully updated")
            dialog.update_browser_box(f"Please try hotfix update once more to make sure there are no available hotfixes.")
            dialog.processing = Processing.NO
        elif target_version == -2:
            dialog.update_browser_box(f"Timeout reached. Please try it later.")
        else:
            dialog.update_browser_box(f"No new hotfix available.")
        dialog.processing = Processing.NO
    except Exception as e:
        dialog.processing = Processing.NO