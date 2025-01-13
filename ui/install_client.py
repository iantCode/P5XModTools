import asyncio
from client.client_installer import ClientInstaller
from const.enums import Processing
from utils.clean import environment_clean, safe_remove
from utils.settings import Setting
from threading import Event

def client_download_and_install(dialog, event: Event):
    setting = Setting.instance()
    client_installer = ClientInstaller.instance()

    try:
        if setting.game_location == "":
            dialog.update_browser_box(f"You need to set the location of the game!")
            return

        dialog.processing = Processing.CLIENT
        dialog.update_browser_box(f"Cleaning Environment...")
        environment_clean()
        dialog.update_browser_box(f"Checking client version")
        version = client_installer.get_client_version(event)
        if version:
            dialog.update_browser_box(f"Newest version: {version}")
            dialog.update_browser_box(f"Now Downloading the client. It will take a lot of time.")
            safe_remove("config.xml")
            result = asyncio.run(client_installer.install_client(event))
            if result:
                dialog.update_browser_box(f"Finish downloading the client.")
            else:
                dialog.update_browser_box(f"There was some problem downloading the client. Please try once more!")
            safe_remove("ResList.xml")
            dialog.processing = Processing.NO
        else:
            dialog.update_browser_box(f"Something bad happened while getting client version")
            dialog.processing = Processing.NO
    except:
        dialog.processing = Processing.NO