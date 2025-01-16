from const.enums import Processing
from PyQt6.QtCore import QThread, pyqtSignal
from mod.mod_installer import ModInstaller
from utils.clean import environment_clean
from utils.settings import Setting
from utils.filesystem import is_client_installed

class ModInstallThread(QThread):
    update_signal = pyqtSignal(str)  # 신호 정의

    def __init__(self, dialog, event):
        super().__init__()
        self.dialog = dialog
        self.my_event = event

    def run(self):
        setting = Setting.instance()
        mod_installer = ModInstaller.instance()

        try:
            if setting.game_location == "":
                self.update_signal.emit(f"You need to set the location of the game!")
                return
            
            if not is_client_installed():
                self.update_signal.emit(f"I cannot find P5X Client files. Make sure you download the game!")
                return
            
            self.dialog.processing = Processing.MOD
            self.update_signal.emit(f"Cleaning Environment...")
            environment_clean()
            if mod_installer.is_mod_installed():
                self.update_signal.emit(f"You already installed the mod. Please remove it first!")
                self.dialog.processing = Processing.NO
                return
            self.update_signal.emit(f"Downloading Translation MOD")
            mod_installer.download()
            self.update_signal.emit(f"Extracting and installing the Translation MOD")
            mod_installer.extract()
            self.update_signal.emit(f"Checking the Program... Please Wait")
            if not mod_installer.is_mod_installed():
                self.update_signal.emit(f"Looks like we had some error. Please try it again.")
                self.dialog.processing = Processing.NO
                return
            environment_clean()
            self.update_signal.emit(f"Installing Done!")
            self.dialog.processing = Processing.NO
        except Exception as e:
            self.update_signal.emit(str(e))
            self.dialog.processing = Processing.NO