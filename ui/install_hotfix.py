import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from const.enums import Processing
from hotfix.hotfix_installer import HotfixPatcher
from utils.clean import environment_clean
from utils.settings import Setting

class HotfixInstallThread(QThread):
    update_signal = pyqtSignal(str)  # 신호 정의

    def __init__(self, dialog, event):
        super().__init__()
        self.dialog = dialog
        self.my_event = event

    def run(self):
        setting = Setting.instance()
        hotfix_patcher = HotfixPatcher.instance()

        try:
            if setting.game_location == "":
                self.update_signal.emit(f"You need to set the location of the game!")
                return
            
            self.dialog.processing = Processing.HOTFIX
            self.update_signal.emit(f"Cleaning Environment...")
            # environment_clean()
            self.update_signal.emit(f"Checking hotfix version")
            line, version = hotfix_patcher.get_version()
            self.update_signal.emit(f"Detected Line: {line} Version: {version}")
            target_version = asyncio.run(hotfix_patcher.get_target_version())

            if target_version > 0:
                self.update_signal.emit(f"New Version {target_version} has been found. Downloading the hotfix.")
                self.dialog.processing = Processing.MOD # for enabling progress bar tracks download bar.
                target_version = asyncio.run(hotfix_patcher.download_hotfix(self.my_event))
                self.update_signal.emit(f"Downloading hotfix has finished, now extracting and patching the game.")
                self.dialog.processing = Processing.HOTFIX
                hotfix_patcher.apply_patch(self.my_event)
                self.update_signal.emit(f"Verifying the Patch...")
                result, filename = hotfix_patcher.verify_checksum(self.my_event)
                if not result:
                    self.update_signal.emit(f"{filename} was badly patched. Please try it once again!")
                    environment_clean()
                    return
                self.update_signal.emit(f"Verifying Completed. Now moving the files")
                hotfix_patcher.move_patch_to_client()
                self.update_signal.emit(f"Hotfix was successfully updated")
                self.update_signal.emit(f"Please try hotfix update once more to make sure there are no available hotfixes.")
                self.dialog.processing = Processing.NO
            elif target_version == -2:
                self.update_signal.emit(f"Timeout reached. Please try it later.")
            else:
                self.update_signal.emit(f"No new hotfix available.")
            self.dialog.processing = Processing.NO
        except Exception as e:
            self.dialog.processing = Processing.NO