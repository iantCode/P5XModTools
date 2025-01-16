import asyncio
import random
import sys
import webbrowser
import time

from const.enums import Region, Processing
from utils.custom_dialog import CustomDialog
from hotfix.hotfix_installer import HotfixPatcher
from launcher.launcher_installer import LauncherInstaller
from PyQt6.QtWidgets import QApplication,QWidget, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import QThreadPool
from utils.singleton import SingletonInstance
from ui.install_mod import ModInstallThread
from ui.uninstall_mod import ModUninstallThread
from ui.install_launcher import LauncherInstallThread
from ui.install_client import ClientInstallThread
from ui.install_hotfix import HotfixInstallThread
from utils.clean import remove_temp_files, environment_clean
from utils.download import Downloader
from utils.settings import Setting
from utils.worker import Worker
from threading import Thread, Event

forms = uic.loadUiType('main.ui')

class MainWindow(SingletonInstance, QWidget, forms[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.setFixedSize(640, 480)
        self.show()

        self.processing = Processing.NO
        self.stop_update_thread = False
        self.stop_event_thread= Event()
        self.threadpool = QThreadPool()
        self.worker = None

        update_status_thread = Worker(self.get_update_status)
        self.threadpool.start(update_status_thread)


    def init_ui(self):
        setting = Setting.instance()
        result = asyncio.run(setting.check_version())
        if result:
            warning_dlg = CustomDialog(self, "Update Needed", f"{result} version found, Please download and extract.")
            warning_dlg.exec()
            webbrowser.open("https://iant.kr/p5xmod/P5XModTools.zip", new=0, autoraise=True)
            sys.exit(0)
        self.modButton.clicked.connect(self.mod_button_clicked)
        self.launcherButton.clicked.connect(self.launcher_button_clicked)
        self.clientButton.clicked.connect(self.client_button_clicked)
        self.hotfixButton.clicked.connect(self.hotfix_button_clicked)
        self.infoButton.clicked.connect(self.info_clicked)
        self.uninstallModButton.clicked.connect(self.mod_uninstall_button_clicked)
        self.autoDetectLocation.clicked.connect(self.auto_detect_clicked)
        self.regionComboBox.currentTextChanged.connect(self.change_region)
        self.versionLabel.setText(f"v{setting.program_version}")

    
    def info_clicked(self):
        warning_dlg = CustomDialog(self, "Developer", "Developed by iant\nMod Maintaining by P5XWorldWide discord\nSpecial Thanks to DeathChaos25 who built vfileExtractor.\n\nPress the open button to join P5XWorldWide discord.\n", "https://discord.com/invite/p5xworldwide")
        warning_dlg.exec()


    def auto_detect_clicked(self):
        if self.processing == Processing.NO:
            setting = Setting.instance()
            if setting.try_auto_detect_location():
                self.locationEditor.setPlainText(setting.game_location)
            else:
                warning_dlg = CustomDialog(self, "Not Found", "I cannot find the location of client. Did you properly install the game?")
                warning_dlg.exec()

    
    def mod_button_clicked(self):
        if self.processing == Processing.NO:
            reply = QMessageBox.question(self, 'Message',
                        "Are you sure want to download Translation Mod?", 
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_browser_box()
                self.worker = ModInstallThread(self, self.stop_event_thread)
                self.worker.update_signal.connect(self.update_browser_box)
                self.worker.start()


    def mod_uninstall_button_clicked(self):
        if self.processing == Processing.NO:
            reply = QMessageBox.question(self, 'Message',
                        "Are you sure want to uninstall Translation Mod?", 
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_browser_box()
                self.worker = ModUninstallThread(self, self.stop_event_thread)
                self.worker.update_signal.connect(self.update_browser_box)
                self.worker.start()

    
    def launcher_button_clicked(self):
        if self.processing == Processing.NO:
            reply = QMessageBox.question(self, 'Message',
                        "It will take a lot of time to download launcher. If you close this program during downloading, you should remove temporary files yourself. Do you want to continue?", 
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_browser_box()
                self.worker = LauncherInstallThread(self, self.stop_event_thread)
                self.worker.update_signal.connect(self.update_browser_box)
                self.worker.start()


    def client_button_clicked(self):
        if self.processing == Processing.NO:
            reply = QMessageBox.question(self, 'Message',
                        "It will take a lot of time to download client.\nTHIS IS STILL IN BETA PHASE, SO IT WILL HAVE SOME ERROR WHILE DOWNLOADING IT.\nTHIS WILL REMOVE ALL OF CLIENT FILES.\nDo you want to continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.reset_browser_box()
                self.worker = ClientInstallThread(self, self.stop_event_thread)
                self.worker.update_signal.connect(self.update_browser_box)
                self.worker.start()

    
    def hotfix_button_clicked(self):
        if self.processing == Processing.NO:
            self.reset_browser_box()
            self.worker = HotfixInstallThread(self, self.stop_event_thread)
            self.worker.update_signal.connect(self.update_browser_box)
            self.worker.start()

    def update_browser_box(self, value):
        self.browserEditor.appendPlainText(value)
        self.browserEditor.verticalScrollBar().setValue(
            self.browserEditor.verticalScrollBar().maximum()
            )
        
    
    def reset_browser_box(self):
        self.browserEditor.setPlainText("")


    def change_region(self, value):
        setting = Setting.instance()
        if self.processing == Processing.NO:
            setting.region = Region[value]
            setting.game_location = ""
            self.locationEditor.setPlainText(setting.game_location)
        else:
            self.regionComboBox.setCurrentIndex(setting.region.value)
        

    def get_update_status(self):
        while True:
            time.sleep(random.randrange(30, 60) / 100)
            if self.stop_update_thread:
                break
            if self.processing == Processing.MOD or self.processing == Processing.CLIENT:
                download = Downloader.instance()
                result = download.check_download_status()
                self.downloadProgress.setValue(int(result))
            elif self.processing == Processing.LAUNCHER:
                launcher = LauncherInstaller.instance()
                result = launcher.check_launcher_download_status()
                self.downloadProgress.setValue(round(result))
            elif self.processing == Processing.HOTFIX:
                hotfix = HotfixPatcher.instance()
                result = hotfix.applied_files_num / hotfix.all_files_num * 100
                self.downloadProgress.setValue(round(result))


    def closeEvent(self, event):
        self.stop_update_thread = True
        remove_temp_files("./")
        environment_clean()
        setting = Setting.instance()
        self.stop_event_thread.set()
        time.sleep(2)
        remove_temp_files(setting.game_location)
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = MainWindow()
    sys.exit(app.exec())

# pyinstaller main.py -w --onefile