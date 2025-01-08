import aiohttp      
import aiofiles
import asyncio
import os
import yarl
from singleton.singleton import SingletonInstance
from threading import Event
from utils.clean import safe_remove

class Downloader(SingletonInstance):
    def __init__(self):
        self.url = ""
        self.filename = ""
        self.filesize = 1
        self.downloaded_filesize = 0


    async def download(self, url: str, filename: str, event: Event | None = None):
        self.url = yarl.URL(url, encoded=True)
        self.filename = filename
        self.thread_event = event
        task = asyncio.create_task(self._download_internal())
        await task


    async def get_json_from_url(self, url: str, event: Event | None = None):
        self.url = yarl.URL(url, encoded=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status < 300:
                    return await resp.json()


    def check_download_status(self):
        return self.downloaded_filesize / self.filesize * 100


    async def _download_internal(self):
        async with aiohttp.ClientSession() as session:
            resp = await session.head(self.url)
            self.filesize = resp.content_length

            if os.path.dirname(self.filename) != '' and not os.path.exists(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename))\
            
            self.downloaded_filesize = 0
            if not self.filesize or self.filesize < 50 * 1000 * 1000:
                result = await self.singlethread_download()
            else:
                result = await self.multithread_download()

            return result
        

    async def multithread_download(self):
        try:
            gathered_func = []
            threads = 12
            for i in range(threads):
                start = self.filesize // threads * i
                if i == threads - 1:
                    end = self.filesize
                else:
                    end = self.filesize // threads * (i + 1) - 1
                gathered_func.append(asyncio.ensure_future(self.download_split_files(i, start, end)))

            result = await asyncio.gather(*gathered_func)
            if not False in result:
                with open(self.filename, 'a+b') as f:
                    for i in range(threads):
                        with open(f"{self.filename}.fragment{i}", 'rb') as f2:
                            f.write(f2.read())
                        safe_remove(f"{self.filename}.fragment{i}")
                return True
            else:
                return False
        except:
            return False


    async def download_split_files(self, idx, start, end):
        try:
            header = {"Range": f"bytes={start}-{end}"}
            chunk_size = 8192

            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=header) as resp:
                    if resp.status < 300:
                        async with aiofiles.open(f"{self.filename}.fragment{idx}", mode="wb") as f:
                            async for data in resp.content.iter_chunked(chunk_size):
                                if self.thread_event.is_set():
                                    break
                                self.downloaded_filesize += len(data)
                                await f.write(data)
            return True
        except Exception as e:
            return False

    
    async def singlethread_download(self):
        try:
            chunk_size = 8192
            safe_remove(self.filename)
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as resp:
                    if resp.status < 300:
                        async with aiofiles.open(f"{self.filename}", mode="wb") as f:
                            async for data in resp.content.iter_chunked(chunk_size):
                                if self.thread_event.is_set():
                                    break
                                self.downloaded_filesize += len(data)
                                await f.write(data)
            return True
        except Exception as e:
            return False

if __name__ == "__main__":
    setting = Downloader()