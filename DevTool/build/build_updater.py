import logging
import os
import subprocess

BUILD_NAME = "DM-Bot-updater.exe"

def build_updater():
    logging.info("Start build updater file")
    cur_path = os.path.dirname(os.path.abspath(__file__))

    if os.path.exists(os.path.join(cur_path, BUILD_NAME)):
        os.remove(BUILD_NAME)
    
    nuitka_command = (
        f"python -m nuitka "
        f"--remove-output "
        f"--jobs=4 "
        f"--standalone "
        f"--onefile "
        f"--no-pyi-file "
        f"--windows-icon-from-ico=icon.png "
        f"code/updater_main.py"
    )
    subprocess.run(nuitka_command, shell=True)

    os.rename("updater_main.exe", BUILD_NAME)

if __name__ == "__main__":
    build_updater()
