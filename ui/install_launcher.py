import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from const.enums import Processing
from launcher.launcher_installer import LauncherInstaller
from utils.clean import environment_clean, safe_remove
from utils.settings import Setting
from threading import Event

class LauncherInstallThread(QThread):
    update_signal = pyqtSignal(str)  # 신호 정의

    def __init__(self, dialog, event):
        super().__init__()
        self.dialog = dialog
        self.my_event = event

    def run(self):
        setting = Setting.instance()
        launcher_installer = LauncherInstaller.instance()

        try:
            if setting.game_location == "":
                self.update_signal.emit(f"You need to set the location of the game!")
                return
                
            self.dialog.processing = Processing.LAUNCHER
            self.update_signal.emit(f"Cleaning Environment...")
            environment_clean()
            self.update_signal.emit(f"Checking launcher version")
            version = launcher_installer.get_latest_launcher_version(self.my_event)
            if version:
                self.update_signal.emit(f"Newest version: {version}")
                self.update_signal.emit(f"Now Downloading the launcher. It will take some time.")
                safe_remove('./version.ini')
                result = asyncio.run(launcher_installer.install_launcher_from_server(self.my_event))
                if result:
                    self.update_signal.emit(f"Finish installing the launcher.")
                else:
                    self.update_signal.emit(f"There was some problem downloading the launcher. Please try once more!")
                self.dialog.processing = Processing.NO
            else:
                self.update_signal.emit(f"Something bad happened while getting launcher version")
                self.dialog.processing = Processing.NO
        except Exception as e:
            self.update_signal.emit(str(e))
            self.dialog.processing = Processing.NO