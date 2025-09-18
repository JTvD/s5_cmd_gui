from dotenv import load_dotenv
from datetime import datetime
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QStandardPaths, QDir, QThread
import PySide6.QtWidgets as QtWidgets
from threading import Event
from pathlib import Path
# from os import path
import sys

import gui
from utils import setup_logger, load_ui, make_folder
from path import ScalityPath
from data_transfer import DataTransfer
from data_operation import DataOperation
from scality_tree import scalityTreeModel


class mainmenu(QtWidgets.QMainWindow, gui.MainWindow.Ui_MainWindow):
    def __init__(self):
        super(mainmenu, self).__init__()

        # Nuitka does not freeze code, but add __compiled__...
        if getattr(sys, 'frozen', False) or ("__compiled__" in globals()):
            super(mainmenu, self).setupUi(self)
        else:
            cfd = Path(__file__).resolve().parent
            load_ui(cfd.joinpath('gui', 'MainWindow.ui'), self)

        self.PB_fs_create.clicked.connect(self.create_fs_dir)
        self.PB_fs_delete.clicked.connect(self.delete_fs_dir)
        self.PB_sc_create.clicked.connect(self.create_sc_dir)
        self.PB_sc_delete.clicked.connect(self.delete_sc_dir)
        self.PB_upload.clicked.connect(self.upload_data)
        self.PB_download.clicked.connect(self.download_data)
        self._init_local_fs_tree()
        self._init_scality_tree()

        self.sc_new_foldername = ""
        self.data_operations = DataOperation()
        self.threads = []
        self.refresh_scality_index = None

    def _enable_buttons(self, enable: bool):
        self.PB_fs_create.setEnabled(enable)
        self.PB_fs_delete.setEnabled(enable)
        self.PB_sc_create.setEnabled(enable)
        self.PB_sc_delete.setEnabled(enable)
        self.PB_upload.setEnabled(enable)
        self.PB_download.setEnabled(enable)

    def pop_up(self, message):
        """ Pop up a message box with the given message
        Args:
            message : str
                message to be displayed
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("Confirm Action")
        msgBox.setText(message)
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        response = msgBox.exec_()
        if response == QtWidgets.QMessageBox.Ok:
            return True
        else:
            return False

    def _init_local_fs_tree(self):
        """ Initialize local QTreeView"""
        self.local_fs_model = QtWidgets.QFileSystemModel(self.local_fs_tree)
        self.local_fs_tree.setModel(self.local_fs_model)
        # Hide all columns except the Name
        self.local_fs_tree.setColumnHidden(1, True)
        self.local_fs_tree.setColumnHidden(2, True)
        self.local_fs_tree.setColumnHidden(3, True)
        self.local_fs_tree.header().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        home_location = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.HomeLocation)[0]
        self.local_fs_model.setRootPath(home_location)

    def _init_scality_tree(self):
        self.scality_model = scalityTreeModel(self.scality_fs_tree)
        self.scality_fs_tree.setModel(self.scality_model)
        self.scality_fs_tree.expanded.connect(self.scality_model.refresh_subtree)
        self.scality_model.init_tree()

        # Hide unnecessary information
        self.scality_fs_tree.setColumnHidden(1, True)
        self.scality_fs_tree.setColumnHidden(2, True)
        self.scality_fs_tree.setColumnHidden(3, True)
        self.scality_fs_tree.setColumnHidden(4, True)
        self.scality_fs_tree.setColumnHidden(5, True)

    def create_fs_dir(self):
        """Create a directory/folder on the local filesystem """
        self.TB_status.clear()
        indexes = self.local_fs_tree.selectedIndexes()
        if len(indexes) == 0:
            self.TB_status.append("Please select a parent directory.")
            return
        parent_path = Path(self.local_fs_model.filePath(indexes[0]))
        if parent_path.is_dir():
            foldername, ok = QtWidgets.QInputDialog.getText(self, "Create folder",
                                                            "Foldername:", QtWidgets.QLineEdit.Normal,
                                                            QDir.home().dirName())
            if ok and foldername:
                folder_path = parent_path.joinpath(foldername)
                folder_path.mkdir(parents=True, exist_ok=True)
        else:
            self.TB_status.append("Please select a parent directory, not a file.")

    def delete_fs_dir(self):
        """Delete a folder/file on the local filesystem."""
        self.TB_status.clear()
        fs_selection = self.local_fs_tree.selectedIndexes()
        if len(fs_selection) == 0:
            self.TB_status.append("Please select a directory.")
            return None
        fs_index = fs_selection[0]
        local_path = Path(self.local_fs_model.filePath(fs_index))
        if self.pop_up(f"Are you sure you want to delete {local_path}?"):
            self.TB_status.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\
                                   starting deletion of {local_path}. Ui might hang, please wait..")
            self.data_operations.delete_local_data(local_path)
            self.TB_status.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {local_path} deleted.")

    def create_sc_dir(self):
        """Create a directory/folder on the local filesystem."""

        foldername, ok = QtWidgets.QInputDialog.getText(self, "Create folder",
                                                        "Enter foldername\n It is automatically created during the upload:\n",
                                                        QtWidgets.QLineEdit.Normal,
                                                        QDir.home().dirName())
        if ok and foldername:
            self.sc_new_foldername = foldername
        else:
            self.sc_new_foldername = ""

    def delete_sc_dir(self):
        """Delete a folder/file on the scality filesystem."""
        self.TB_status.clear()
        scality_selection = self.scality_fs_tree.selectedIndexes()
        if len(scality_selection) == 0:
            self.TB_status.append("Please select a collection.")
            return None
        scality_index = scality_selection[0]
        self.refresh_scality_index = scality_index
        _, _, _, scality_folder = self.scality_model.path_from_tree_index(scality_index)

        if self.pop_up(f"Are you sure you want to delete {scality_folder}?"):
            self.TB_status.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\
                                   starting deletion of {scality_folder}. Ui might hang, please wait..")
            self.data_operations.delete_bucket_data(ScalityPath(self.data_operations, scality_folder))
            self.TB_status.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {scality_folder} deleted.")
            self.scality_model.refresh_subtree(scality_index)

    def update_transfer_status(self, status):
        """Helper function to update the data transfer thread"""
        self.TB_status.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {status}")

    def upload_data(self):
        local_paths, scality_paths = self._gather_info_for_transfer()
        if len(scality_paths) != 1 or scality_paths[0].Ff == 'f':
            self.TB_status.append("Can only upload to one scality folder.")
            return
        self.to_up_download = []
        for local_folder in local_paths:
            if self.sc_new_foldername == '':
                self.to_up_download.append(('upload', local_folder, scality_paths[0]))
            else:
                self.to_up_download.append(('upload', local_folder, f'{scality_paths[0]}{self.sc_new_foldername}'))
        self.start_data_transfer(self.to_up_download.pop(0))

    def finish_data_transfer(self):
        """ Finish an up/download"""
        if len(self.to_up_download) > 0:
            self.start_data_transfer(self.to_up_download.pop(0))
            return
        self._enable_buttons(True)
        if self.refresh_scality_index is not None:
            self.scality_model.refresh_subtree(self.refresh_scality_index)

    def download_data(self):
        local_paths, scality_paths = self._gather_info_for_transfer()
        self.refresh_scality_index = None
        if len(local_paths) != 1 or not local_paths[0].is_dir():
            self.TB_status.append("Can only download to one local folder.")
            return
        self.to_up_download = []
        for Scalitypath in scality_paths:
            self.to_up_download.append(('download', local_paths[0], Scalitypath))
        self.start_data_transfer(self.to_up_download.pop(0))

    def start_data_transfer(self, item):
        """ Item is a tuple containing: ('upload', 'C:/Users/daale010', '.')"""
        updown, local_path, scality_path = item
        thread = QThread()
        self.stop_worker = Event()
        self.worker = DataTransfer(self.stop_worker)
        self.worker.set_params(updown, local_path, scality_path, False)
        self.worker.moveToThread(thread)
        self.worker.progress.connect(self.update_transfer_status)
        thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.finish_data_transfer)
        self.worker.finished.connect(thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._enable_buttons(False)
        thread.start()
        self.threads.append(thread)

    def _gather_info_for_transfer(self):
        """ Retrieve the paths for the transfer
        Return:
            local_paths : list
                list of local paths
            scality_paths : list
                list of Scality paths
        """
        self.TB_status.clear()
        # Retrieve local fs path
        local_paths = []
        for fs_index in self.local_fs_tree.selectedIndexes():
            local_path = Path(self.local_fs_model.filePath(fs_index))
            local_paths.append(local_path)
        if len(local_paths) == 0:
            self.TB_status.append("Please select a file or folder.")
            return None, None

        # Retrieve scality path
        scality_paths = []
        for scality_index in self.scality_fs_tree.selectedIndexes():
            tree_item_data = self.scality_model.path_from_tree_index(scality_index)

            scality_paths.append(ScalityPath.from_tree_item(self.data_operations, tree_item_data))
            self.refresh_scality_index = scality_index
        if len(scality_paths) == 0:
            self.TB_status.append("Please select a file or folder.")
            return None, None
        return local_paths, scality_paths


if __name__ == "__main__":
    # Load env file
    load_dotenv()
    # Setup logger
    setup_logger()

    # QT initialization
    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    widget = mainmenu()
    widget.show()
    sys.exit(app.exec())
