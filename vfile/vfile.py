import os
from singleton.singleton import SingletonInstance
from utils.settings import Setting

class VFile(SingletonInstance):
    def read(self):
        setting = Setting.instance()
        vfile = open(os.path.join(setting.game_location, "client/bin", "_vfileIndexV2.fb"), "rb")
        header = FileHeader(vfile)
        self.all_entries = []
        self.name_entry_map = {}

        for section_ptr in header.section_ptrs:
            vfile.seek(section_ptr)
            content_header = FileContentHeader(vfile)
            for content_section_ptr in content_header.content_section_ptrs:
                vfile.seek(content_section_ptr)
                content_entry = FileContentEntry(vfile)
                content_entry.vfile_index = content_header.file_content_size
                content_header.entries.append(content_entry)
                self.name_entry_map[content_entry.name] = content_entry
            self.all_entries.append(content_header)
    
    def extract(self, name):
        setting = Setting.instance()
        if name in self.name_entry_map:
            target = self.name_entry_map[name]
            vfile = open(os.path.join(setting.game_location, "client/bin", target.vfile_index), 'rb')
            vfile.seek(target.content_file_offset)
            new_file = open('./temp.bytes', 'wb')
            new_file.write(vfile.read(target.content_file_size))


class FileHeader:
    def __init__(self, file):
        self.header_pre1 = int.from_bytes(file.read(4), "little")
        file.read(self.header_pre1)
        self.field_08 = int.from_bytes(file.read(4), "little")
        self.field_0C = int.from_bytes(file.read(4), "little")
        self.num_of_ptrs = int.from_bytes(file.read(4), "little")
        self.section_ptrs = []

        for i in range(self.num_of_ptrs):
            self.section_ptrs.append(file.tell() + int.from_bytes(file.read(4), "little"))


class FileContentHeader:
    def __init__(self, file):
        self.hash = int.from_bytes(file.read(4), "little")
        self.section_total_size = file.tell() + int.from_bytes(file.read(4), "little")
        self.ptr_to_ptr_list = int.from_bytes(file.read(4), "little")
        self.num_of_content_entries = int.from_bytes(file.read(4), "little")
        self.content_section_ptrs = []

        for i in range(self.num_of_content_entries):
            self.content_section_ptrs.append(file.tell() + int.from_bytes(file.read(4), "little"))

        self.entries = []

        current_position = file.tell()

        file.seek(self.section_total_size)
        name_size = int.from_bytes(file.read(4), "little")
        self.file_content_size = file.read(name_size).decode('utf8')
        file.seek(current_position)


class FileContentEntry:
    def __init__(self, file):
        self.vfile_index = ""
        self.hash = int.from_bytes(file.read(4), "little")
        self.entry_size = int.from_bytes(file.read(4), "little")
        self.content_file_size = int.from_bytes(file.read(4), "little")
        self.content_file_offset = int.from_bytes(file.read(4), "little") if self.entry_size >= 0x10 else 0
        self.field_10 = int.from_bytes(file.read(4), "little") if self.entry_size >= 0x14 else 0
        self.field_14 = int.from_bytes(file.read(4), "little") if self.entry_size >= 0x18 else 0
        test = int.from_bytes(file.read(4), "little")
        if test != 0:
            file.seek(file.tell() - 4)
        self.name_size = int.from_bytes(file.read(4), "little")
        self.name = file.read(self.name_size).decode("utf-8")

if __name__ == "__main__":
    vfile = VFile()
    vfile.read()
    vfile.extract("Bundles/Windows/196/efx_18dfb0c4.bundle")
