import os
import shutil

def safe_remove(dir):
    try:
        os.remove(path=dir)
    except:
        pass

def remove_temp_files(initial_dir):
    for root, dirs, files in os.walk(initial_dir):
        for name in files:
            for i in range(16):
                if name.endswith(f".fragment{i}"):
                    safe_remove(os.path.join(root, name))

def environment_clean():
    safe_remove("config.xml")
    safe_remove("./AllFiles.xml")
    safe_remove("./ResList.xml")
    safe_remove("p5xmod.zip")
    safe_remove("temp.bytes")
    safe_remove("temp.zpf")
    shutil.rmtree('./temp', ignore_errors=True)