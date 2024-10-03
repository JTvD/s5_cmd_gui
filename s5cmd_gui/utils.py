"""Utils """
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QMetaObject


class UiLoader(QUiLoader):
    """UILoader to allow custom widgets"""
    def __init__(self, base_instance):
        QUiLoader.__init__(self, base_instance)
        self.base_instance = base_instance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.base_instance:
            return self.base_instance
        else:
            # create a new widget for child widgets
            widget = QUiLoader.createWidget(self, class_name, parent, name)
            if self.base_instance:
                setattr(self.base_instance, name, widget)
            return widget


def load_ui(ui_file, base_instance=None):
    """load ui, as available in pyqt"""
    loader = UiLoader(base_instance)
    widget = loader.load(ui_file)
    QMetaObject.connectSlotsByName(widget)
    return widget


def make_folder(parent: str, foldername: str):
    """Create a folder if it does not exist"""
    folder = Path(parent).joinpath(foldername)
    if not folder.exists():
        folder.mkdir(parents=True)


def get_logfolder():
    """ Loads a config.json and returns the content """
    cfd = Path(__file__).resolve().parent
    log_path = cfd.joinpath("logs", "traitseeker.log")
    if not log_path.parent.exists():
        log_path.parent.mkdir(parents=True)
    return log_path


def setup_logger():
    """ Create logger, it is important to note that prints are not written to the logfile! """
    log_file = get_logfolder()
    log_format = '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    # Roratingfile handler: 1MB/logfile and keep last 2 files, lower number = newer.
    handlers = [RotatingFileHandler(log_file, 'a', 1000000, 1), logging.StreamHandler(sys.stdout)]
    logging.basicConfig(format=log_format, level=logging.INFO, handlers=handlers)

    with open(log_file, 'a', encoding='UTF-8') as file:
        file.write("\n\n")
        file.write("New session")
        file.write("\n\n")
