from PyQt6.QtCore import QThread, pyqtSignal
from const.enums import Processing
from mod.mod_installer import ModInstaller
from utils.clean import environment_clean
from utils.settings import Setting
from utils.filesystem import is_client_installed

class ModUninstallThread(QThread):
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
            self.update_signal.emit(f"Checking Your Client")
            if mod_installer.is_mod_installed():
                mod_installer.uninstall()
                self.update_signal.emit(f"Translation mod has been removed successfully.")
                self.dialog.processing = Processing.NO
            else:
                self.update_signal.emit(f"You didn't install the mod!")
                self.dialog.processing = Processing.NO
                    
        except Exception as e:
            self.update_signal.emit(str(e))
            self.dialog.processing = Processing.NO