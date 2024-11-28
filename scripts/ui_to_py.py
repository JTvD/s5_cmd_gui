from subprocess import run, STDOUT
from platform import system
from pathlib import Path


def run_cmd(cmd: str):
    """ Run a commandline command snd check if it was successful
        Args:
            cmd : str
                command to run
    """
    if system()[0].upper() == "W":  # Windows
        ps = run(cmd, stderr=STDOUT, shell=True, universal_newlines=True)
    else:
        ps = run(cmd, stderr=STDOUT, shell=True, universal_newlines=True, executable="/bin/bash")
    # Print all errors
    if ps.stderr is not None or ps.returncode != 0:
        print(f"commandline error: {ps.stderr}")
        raise Exception("shell run error")


def os_specific_settings():
    """ Get the settings for the operating system
        Returns:
            python : str
                python version
            cmd_sep : str
                command separator
    """
    if system()[0].upper() == "W":  # windows
        cmd_sep = "&&"
        python = "python"  # python version
    else:  # Linux, ensure it uses python 3
        cmd_sep = ";"
        python = "python3"
    return (python, cmd_sep)


def ui_to_py(ui_folder: Path, venv_activate: str, cmd_sep: str):
    """ Convert the .ui files to .py files
        pyside6-uic gui/MainWindow.ui -o gui/MainWindow.py
        Args:
            ui_folder : Path
                folder containing the .ui files
            venv_activate : str
                command to activate the virtual environment
            cmd_sep : str
                command separator
    """
    for ui_file in ui_folder.glob('*.ui'):
        py_file = ui_file.with_suffix('.py')
        print(f"Converting {py_file.name} to .py")
        run_cmd(f"""{venv_activate} {cmd_sep} pyside6-uic "{ui_file}" -o "{py_file}" """)


def remove_pyui_files(ui_folder: Path):
    """ Remove the locally stored .py versions of the files"""
    pyuifiles = ui_folder.glob('*.py')
    for file in pyuifiles:
        # Skip __init__.py files
        if "__init__" in file.name:
            continue
        print(f"Removing {file}")
        file.unlink()


if __name__ == "__main__":
    icons_folder = Path.cwd().joinpath('s5cmd_gui', 'icons')
    ui_foldername = Path.cwd().joinpath('s5cmd_gui', 'gui')
    python_v, _ = os_specific_settings()

    # Step 1 Convert .ui files to .py files
    # Remove py files if they already exist, recompiling is the best way to ensure they are up to date
    remove_pyui_files(ui_foldername)
    ui_to_py(ui_foldername)
