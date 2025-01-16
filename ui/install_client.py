import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from client.client_installer import ClientInstaller
from const.enums import Processing
from utils.clean import environment_clean, safe_remove
from utils.settings import Setting
from threading import Event

class ClientInstallThread(QThread):
    update_signal = pyqtSignal(str)  # 신호 정의

    def __init__(self, dialog, event):
        super().__init__()
        self.dialog = dialog
        self.my_event = event

    def run(self):
        setting = Setting.instance()
        client_installer = ClientInstaller.instance()

        try:
            if setting.game_location == "":
                self.update_signal.emit(f"You need to set the location of the game!")
                return

            self.dialog.processing = Processing.CLIENT
            self.update_signal.emit(f"Cleaning Environment...")
            environment_clean()
            self.update_signal.emit(f"Checking client version")
            version = client_installer.get_client_version(self.my_event)
            if version:
                self.update_signal.emit(f"Newest version: {version}")
                self.update_signal.emit(f"Now Downloading the client. It will take a lot of time.")
                safe_remove("config.xml")
                result = asyncio.run(client_installer.install_client(self.my_event))
                if result:
                    self.update_signal.emit(f"Finish downloading the client.")
                else:
                    self.update_signal.emit(f"There was some problem downloading the client. Please try once more!")
                safe_remove("ResList.xml")
                self.dialog.processing = Processing.NO
            else:
                self.update_signal.emit(f"Something bad happened while getting client version")
                self.dialog.processing = Processing.NO
        except:
            self.dialog.processing = Processing.NO