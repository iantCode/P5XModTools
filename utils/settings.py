import aiohttp
import configparser
import os
import string
from const.enums import Region
from const.tables import REGION_MAP
from ctypes import windll
from singleton.singleton import SingletonInstance

# https://www.daniweb.com/programming/software-development/threads/518063/how-to-list-the-name-and-the-size-of-hard-driver-in-python
def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


class Setting(SingletonInstance):
    def __init__(self):
        self.program_version = "0.1.5"

        self.game_location: str = ""
        self.region: Region = Region.CN

    
    async def check_version(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://iant.kr/p5xmod/version.json") as resp:
                if resp.status < 300:
                    resp_json = await resp.json()
                    new_version = resp_json["version"]
                    if new_version != self.program_version:
                        return new_version
        
        return None


    def try_auto_detect_location(self):
        from utils.filesystem import get_filelocation_from_reg
        dirname = get_filelocation_from_reg()
        if dirname and self.verify_client_location(dirname):
            self.game_location = dirname
            return True
        
        # Try old code if there's no Registry
        filename = REGION_MAP[self.region]["exe_name"]
        for drive in get_drives():
            for root, dirs, files in os.walk(f"{drive}:\\"):
                if root.startswith("C:\\Windows"):
                    continue
                if filename in files:
                    if self.verify_client_location(root):
                        self.game_location = root
                        return True
        return False

    def verify_client_location(self, root: str):
        if REGION_MAP[self.region]["launcher_folder"] in os.listdir(root):
            config = configparser.ConfigParser()
            config.read(os.path.join(root\
                                    ,REGION_MAP[self.region]["launcher_folder"]\
                                    ,"Config"\
                                    ,"Config.ini"))
            if config["General"]["GameID"] == REGION_MAP[self.region]["game_id"]:
                return True
            else:
                return False
        else:
            return False
            
if __name__ == "__main__":
    setting = Setting()