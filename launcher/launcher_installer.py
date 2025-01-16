import asyncio
import os
import shutil
import time
import xml.etree.ElementTree as ET
from const.tables import REGION_MAP
from utils.settings import Setting
from utils.download import Downloader
from utils.clean import safe_remove
from utils.singleton import SingletonInstance
from threading import Event

class LauncherInstaller(SingletonInstance):
    def __init__(self):
        self.download_file_list = []
        self.downloading = False
        self.finished_file_count = 0
        self.filesize = 1


    def get_latest_launcher_version(self, event: Event):
        setting = Setting.instance()
        downloader = Downloader.instance()

        desired_path = os.path.join(setting.game_location, REGION_MAP[setting.region]["launcher_folder"])
        if not os.path.exists(desired_path):
            os.makedirs(desired_path)
            
        asyncio.run(downloader.download(REGION_MAP[setting.region]["launcher_version"], "version.ini", event))
        time.sleep(0.7)
        with open("version.ini", 'r', encoding="utf-8") as f:
            f.readline()
            version = f.readline().split('=')[1]
            f.readline()
            xml_dest = f.readline().split('=')[1]

            self.xml_url = xml_dest
            return version
        
    
    async def install_launcher_from_server(self, event: Event):
        await self.get_baseurl_and_version(event)

        self.finished_file_count = 0
        self.downloading = True
        gathered_func = []
        threads = 16
        for i in range(threads):
            start = 3 + self.filesize // threads * i
            if i == threads - 1:
                end = 3 + self.filesize
            else:
                end = 3 + self.filesize // threads * (i + 1)
            gathered_func.append(asyncio.ensure_future(self.install_launcher_thread(start, end, event)))
        
        download_result = await asyncio.gather(*gathered_func)
        self.downloading = False
        safe_remove('AllFiles.xml')
        return not False in download_result


    async def get_baseurl_and_version(self, event: Event):
        downloader = Downloader.instance()
        await downloader.download(self.xml_url, "AllFiles.xml", event)

        tree = ET.parse('AllFiles.xml')
        self.allfiles_xml = tree.getroot()

        self.baseUrl = self.allfiles_xml[2].get("BaseUrl")
        self.version = self.allfiles_xml[1].get('Version')
        self.filesize = len(self.allfiles_xml) - 4


    def check_launcher_download_status(self):
        return self.finished_file_count/self.filesize * 100


    async def install_launcher_thread(self, start, end, event: Event):
        downloader = Downloader()
        try:
            setting = Setting.instance()
            for child in self.allfiles_xml[start:end]:
                destination = os.path.join(setting.game_location, REGION_MAP[setting.region]["launcher_folder"])
                os.makedirs(destination + '\\'.join(child.get('Path').split('/')[0:-1]), exist_ok=True)

                await downloader.download(f'{self.baseUrl}/{self.version}{child.get('Path')}.zip', destination + child.get('Path') + '.zip', event)
                shutil.unpack_archive(destination + child.get('Path') + '.zip', destination + '\\'.join(child.get('Path').split('/')[0:-1]), 'zip')
                self.finished_file_count += 1
                safe_remove(destination + child.get('Path') + '.zip')
            return True
        except:
            return False