from pathlib import Path
from platform import system
from shutil import copy, copytree

import ui_to_py as uipy

# Build config and file paths
code_dir = Path("s5cmd_gui")
icons_folder = Path.cwd().joinpath(code_dir, 'icons')
ui_folder = Path.cwd().joinpath(code_dir, 'gui')
venv = Path.cwd().joinpath('venv')
# Debug mode shows the console (command prompt with the logging)
debug_mode = True
# ---------------------------------------------------------#


# Overwrite one folder with all content
def replace_folder(source, destination):
    copytree(source, destination, dirs_exist_ok=True)


def create_exe():
    (python, cmd_sep) = uipy.os_specific_settings()

    # Step 1: Setup
    # Step 1a, Ensure the folder for the venv exists
    if (not venv.exists()) or (not venv.is_dir()):
        venv.mkdir()

    # Step 1b, Create the venv if needed
    # windows
    if system()[0].upper() == "W":
        venv_activate = venv.joinpath('Scripts', 'activate.bat')
    else:  # Ubuntu/IOS
        venv_activate = venv.joinpath('bin', 'activate')
    if (not venv_activate.exists()) or (not venv_activate.is_file()):
        venv_activate = f"\"{str(venv_activate)}\""
        if system()[0].upper() != "W":
            venv_activate = f"source {venv_activate}"
        uipy.run_cmd(f"{python} -m venv {venv}")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} python -m pip install --upgrade pip")
        uipy.run_cmd(f"{venv_activate} {cmd_sep} pip install -r requirements.txt")
    else:
        venv_activate = f"\"{str(venv_activate)}\""

    # Step 2 Convert .ui files to .py files
    # Recompiling is the best way to ensure they are up to date
    uipy.remove_pyui_files(ui_folder)
    uipy.ui_to_py(ui_folder, venv_activate, cmd_sep)

    # Step 3, Activate venv and run nuitka
    cmd = f"{venv_activate} {cmd_sep} python -m nuitka "
    if not debug_mode:
        cmd += "--disable-console "
    cmd += f"--standalone \
        --remove-output --enable-plugin=pyside6 --include-qt-plugins=sensible,styles \
        --assume-yes-for-downloads --show-progress  \
        --windows-icon-from-ico=\"{icons_folder.joinpath('icon.ico')}\" {code_dir.joinpath('main.py')} --quiet"
    uipy.run_cmd(cmd)

    # Step 4, move the config, env file and icons folder to the distribution folder
    # icons
    replace_folder(icons_folder, icons_folder.parent.joinpath('main.dist', icons_folder.name))

    # Move .env file
    copy(Path.cwd().joinpath('.env'), Path.cwd().joinpath('main.dist', '.env'))


if __name__ == "__main__":
    create_exe()
