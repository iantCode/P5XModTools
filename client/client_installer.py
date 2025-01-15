import asyncio
import os
import shutil
import xml.etree.ElementTree as ET
from const.tables import REGION_MAP
from utils.clean import safe_remove
from utils.download import Downloader
from utils.settings import Setting
from utils.filesystem import md5
from utils.singleton import SingletonInstance
from threading import Event


class ClientInstaller(SingletonInstance):
    
    def get_client_version(self, event: Event):
        setting = Setting.instance()
        downloader = Downloader.instance()

        desired_path = os.path.join(setting.game_location, "client")
        os.makedirs(desired_path, exist_ok=True)
        
        asyncio.run(downloader.download(REGION_MAP[setting.region]["game_version"], "config.xml", event))
        tree = ET.parse('config.xml')
        root = tree.getroot()
        self.version = root[1].text
        self.fullsize = int(root[4].text)
        
        return root[1].text
        
    
    async def install_client(self, event: Event):
        try:
            downloader = Downloader.instance()
            setting = Setting.instance()
            res_list_url = REGION_MAP[setting.region]["res_list"].format(self.version)
            await downloader.download(res_list_url, "ResList.zip", event)

            shutil.unpack_archive("ResList.zip")
            safe_remove("ResList.zip")
            safe_remove("lastdiff.xml")

            tree = ET.parse('ResList.xml')
            self.reslist_xml_root = tree.getroot()

            shutil.rmtree(os.path.join(setting.game_location, "client"), ignore_errors=True)
            result1 = await self.download_large_files(event)
            if result1:
                result2 = await self.download_pak(event)
            return result1 and result2
        except Exception as e:
            print(e)

    
    async def download_pak(self, event: Event):
        try:
            setting = Setting.instance()
            downloader = Downloader.instance()

            package = self.reslist_xml_root[-1]
            for pak in package:
                dlLink = f'{REGION_MAP[setting.region]["res_url"]}/{pak.get('md5')[0]}/{pak.get('md5')}.{pak.get('filesize')}'
                await downloader.download(dlLink, "temp.bytes", event)
                
                tempFile = open('temp.bytes', 'rb')
                tempFileData = tempFile.read()
                for entry in pak:
                    filename = entry.get('name')
                    filename = os.path.join(setting.game_location, filename)
                    if not os.path.exists('/'.join(filename.split('/')[0:-1])):
                        os.makedirs('/'.join(filename.split('/')[0:-1]))
                    newfile = open(filename, 'wb')
                    newfile.write(tempFileData[int(entry.get('offset')):int(entry.get('offset')) + int(entry.get('size'))])
                    newfile.close()
                    calculated_md5 = md5(filename)
                    if calculated_md5 != entry.get('md5'):
                        return False
                tempFile.close()
                safe_remove("temp.bytes")
            return True
        except:
            return False


    async def download_large_files(self, event: Event):
        try:
            setting = Setting.instance()
            downloader = Downloader.instance()

            for idx, child in enumerate(self.reslist_xml_root[0:-1]):
                filename = child.get('filename')
                os.makedirs(os.path.join(setting.game_location, os.path.dirname(filename)), exist_ok=True)
                dlLink = f'{REGION_MAP[setting.region]["res_url"]}/{child.get('md5')[0]}/{child.get('md5')}.{child.get('filesize')}'
                await downloader.download(dlLink, os.path.join(setting.game_location, filename), event)
                calculated_md5 = md5(os.path.join(setting.game_location, filename))
                if calculated_md5 != child.get('md5'):
                    return False
            return True
        except:
            return False