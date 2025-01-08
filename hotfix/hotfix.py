import os
import json
import subprocess
import aiohttp
import zstandard
from pathlib import Path
import tempfile
import tarfile
import shutil
from const.enums import Region
from const.tables import REGION_MAP
from utils.settings import Setting
from utils.download import Downloader
from singleton.singleton import SingletonInstance
from vfile.vfile import VFile

from threading import Event
from utils.clean import safe_remove

class HotfixPatcher(SingletonInstance):
    def __init__(self):
        self.all_files_num = 1
        self.applied_files_num = 0

    def get_version(self):
        self.applied_files_num = 0
        setting = Setting.instance()
        zeus_data = os.path.join(setting.game_location, "client\\OuterPackage\\HotFixTemp\\zeus-hf-data.json")
        if os.path.exists(zeus_data):
            with open(zeus_data, "r", encoding="utf-8") as w:
                zeus = json.load(w)
                self.channel = zeus['ChannelID']
                self.version = zeus["ResVersion"]

            return self.channel, self.version
        else:
            hotfix_file = os.path.join(setting.game_location, "client\\pc\\P5X_Data\\StreamingAssets\\ZeusSetting\\BuildinSetting\\HotfixLocalConfig.json")
            with open(hotfix_file, "r", encoding="utf-8") as w:
                zeus = json.load(w)
                self.channel = zeus['channelId']
                self.version = zeus["ver"]
                os.makedirs(os.path.dirname(zeus_data))
                with open(zeus_data, 'w', encoding='utf-8') as w:
                    json.dump({"ChannelID": self.channel, "ResVersion": self.version}, w)

            return self.channel, self.version
    

    async def get_target_version(self):
        setting = Setting.instance()
        downloader = Downloader.instance()
        resp_json = await downloader.get_json_from_url(self.get_json_url())
        if not resp_json:
            self.target_version = -2
            return -2
        if "PatchConfigData" in resp_json:
            self.target_version = resp_json["PatchConfigData"]["TargetVersion"]
            self.target_url = self.get_zpf_baseurl() + resp_json["PatchConfigData"]["PatchPath"]
        else:
            self.target_version = -1
        
        return int(self.target_version)
    

    def get_json_url(self):
        setting = Setting.instance()
        if setting.region == Region.CN:
            return REGION_MAP[setting.region]["hotfix_url"].format(self.channel, self.version, self.version)
        else:
            return REGION_MAP[setting.region]["hotfix_url"].format(self.channel, self.channel, self.version, self.version)
        
    
    def get_zpf_baseurl(self):
        setting = Setting.instance()
        if setting.region == Region.CN:
            return REGION_MAP[setting.region]["hotfix_base"]
        else:
            return REGION_MAP[setting.region]["hotfix_base"].format(self.channel)
        

    async def download_hotfix(self, event: Event):
        downloader = Downloader.instance()
        await downloader.download(self.target_url, "temp.zpf", event)
        extract_zst("temp.zpf", "./temp")
        safe_remove("./temp.zpf")
    

    def apply_patch(self):
        setting = Setting.instance()
        self.vfile = VFile.instance()
        self.vfile.read()

        self.all_files_num = sum([len(files) for r, d, files in os.walk("./temp")])
        self.applied_files_num = 0

        for root, dirs, files in os.walk("./temp"):
            for name in files:
                self.applied_files_num += 1
                filename_with_folder = os.path.join(root.replace("./temp", ""), name)[1:]
                if filename_with_folder.endswith(".patch"):
                    self.apply_patch_to_file(filename_with_folder)
                        
        move(os.path.join('./temp',), os.path.join(setting.game_location, "client\\OuterPackage"))
        shutil.rmtree('./temp')
        zeus_data = os.path.join(setting.game_location, "client\\OuterPackage\\HotFixTemp\\zeus-hf-data.json")
        with open(zeus_data, "r", encoding="utf-8") as w:
            zeus = json.load(w)
            zeus["ResVersion"] = self.target_version
        with open(zeus_data, "w", encoding="utf-8") as w:
            json.dump(zeus, w)

    
    def apply_patch_to_file(self, filename_with_folder: str):
        setting = Setting.instance()

        new_path = os.path.dirname(os.path.join('./temp', filename_with_folder))
        os.makedirs(new_path, exist_ok=True)

        if os.path.exists(os.path.join(setting.game_location, "client\\bin", filename_with_folder.replace(".patch", ""))):
            old_filename = os.path.join(setting.game_location, "client\\bin", filename_with_folder.replace(".patch", ""))

        elif os.path.exists(os.path.join(setting.game_location, "client\\OuterPackage", filename_with_folder.replace(".patch", ""))):
            old_filename = os.path.join(setting.game_location, "client\\OuterPackage", filename_with_folder.replace(".patch", ""))

        elif os.path.exists(os.path.join(setting.game_location, "client\\pc\\P5X_Data\\StreamingAssets", filename_with_folder.replace(".patch", ""))):
            old_filename = os.path.join(setting.game_location, "client\\pc\\P5X_Data\\StreamingAssets", filename_with_folder.replace(".patch", ""))
        else:
            self.vfile.extract(filename_with_folder.replace('.patch', '').replace('\\', '/'))
            old_filename = "temp.bytes"

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        #si.wShowWindow = subprocess.SW_HIDE # default
        new_filename = os.path.join("temp", filename_with_folder)
        target_filename = os.path.join("temp", filename_with_folder.replace('.patch', ""))
        subprocess.call(f'.\\hpatchz.exe {old_filename} {new_filename} {target_filename}', startupinfo=si)
        safe_remove(os.path.join("temp", filename_with_folder))

        if os.path.exists('./temp.bytes'):
            safe_remove(path="./temp.bytes")


def extract_zst(archive: Path, out_path: Path):
    if zstandard is None:
        raise ImportError("pip install zstandard")

    archive = Path(archive).expanduser()
    out_path = Path(out_path).expanduser().resolve()
    # need .resolve() in case intermediate relative dir doesn't exist

    dctx = zstandard.ZstdDecompressor()

    with tempfile.TemporaryFile(suffix=".tar") as ofh:
        with archive.open("rb") as ifh:
            dctx.copy_stream(ifh, ofh)
        ofh.seek(0)
        with tarfile.open(fileobj=ofh) as z:
            z.extractall(out_path)

def move(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                safe_remove(dst_file)
            shutil.move(src_file, dst_dir)
            