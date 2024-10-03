"""Datatransfer class"""
import logging
from datetime import datetime, timedelta
from os import getenv, path
from pathlib import Path
from PySide6.QtCore import QObject, Signal

from data_operation import DataOperation
from s5cmd_runner import S5CmdRunner
from path import ScalityPath


class DataTransfer(QObject):
    """ data transfer class, called from the main UI
    See run for the flow """
    process = None
    finished = Signal(bool)
    progress = Signal(str)

    def __init__(self, stop_worker):
        super().__init__()
        self.stop_worker = stop_worker
        self.data_operations = DataOperation()
        self.s5cmd = S5CmdRunner()

    def _error(self, msg: str):
        """ Emit signals and take actions in case of an error
            Args:
                msg : str
                    Error message
        """
        self.progress.emit(msg)
        logging.info(msg)
        self.finished.emit(False)

    def progress_and_logg(self, msg: str):
        """ Emit message as progress update to the UI and log it
            Args:
                msg : str
                    Message to be emitted
        """
        self.progress.emit(msg)
        logging.info(msg)

    def set_params(self, updown: str, local_path: Path, scality_path: ScalityPath, delete_source: bool = False):
        """ Set the parameters for the transfer
            Args:
                updown : str
                    upload or download
                local_path : Path
                    local path to the file or folder
                scality_path : ScalityPath
                    scality path to the file or folder
                delete_source : bool
                    delete the source after transfer
        """
        self.updown = updown
        if updown == 'upload':
            self.source_path = local_path
            self.destination_path = scality_path
        else:
            self.source_path = scality_path
            self.destination_path = local_path
        self.delete_source = delete_source

    def run(self):
        """ Main function of the background thread """
        self.transfer(self.updown, self.source_path, self.destination_path, self.delete_source)

    def transfer(self, updown: str, source_path: Path | ScalityPath,
                 destination_path: Path | ScalityPath,
                 delete_source: bool = False):
        """ Main function of the background thread
            Args:
                updown : str
                    upload or download
                source_path : Path | ScalityPath
                    local path or scality path to the file or folder
                destination_path : Path | ScalityPath
                    local path or scality path to the file or folder
                delete_source : bool
                    delete the source after transfer
        """
        self.progress_and_logg('connecting')
        # self.progress.emit('connecting')
        if not self.data_operations.check_bucket(getenv('BUCKETNAME')):
            self._error('specified bucket not found')
            return

        self.progress_and_logg('Checking free space')
        if updown == 'upload':
            (local_files, localsize) = self.data_operations.get_local_datasize(source_path)
            (bucket_files, bucket_filesize, bucket_freespace) = self.data_operations.get_bucket_freespace()
            if bucket_freespace < localsize:
                self._error(f'Not enough free space, required: {self.data_operations.size_fmt(localsize)}, \
                              freespace: {self.data_operations.size_fmt(bucket_freespace)}')
                return
        elif updown == 'download':
            local_freespace = self.data_operations.get_local_freespace(destination_path)
            (bucket_files, bucket_filesize, bucket_freespace) = self.data_operations.get_bucket_freespace(source_path.relative_path())
            self.progress_and_logg(f'source_path: {source_path}, bucket_files: {bucket_files}, bucket_filesize: {bucket_filesize}')
            if local_freespace < bucket_filesize:
                self._error(f'Not enough free space, required: {self.data_operations.size_fmt(bucket_filesize)}, \n\
                              freespace: {self.data_operations.size_fmt(local_freespace)}')
                return
        else:
            self.finished.emit(False)
            return

        self.progress_and_logg('Passed free space check, creating copy paths')
        source_str, destination_str = self.prep_foldernames(updown, source_path, destination_path)
        if updown == 'upload':
            copy_status = self.copy_command(source_str, destination_str, local_files)
        else:
            destination_path.mkdir(parents=True, exist_ok=True)
            copy_status = self.copy_command(source_str, destination_str, bucket_files)

        if copy_status and delete_source:
            self.progress_and_logg(f"removing: {source_path}")
            if updown == 'upload':
                self.data_operations.delete_local_data(source_path)
            else:
                self.data_operations.delete_bucket_data(source_path)
        self.progress_and_logg("Transfer complete")
        self.finished.emit(True)

    def prep_foldernames(self, updown: str,
                         source_path: Path | ScalityPath,
                         destination_path: Path | ScalityPath):
        """ Generate the foldernames for data transfer
            Args:
                updown : str
                    upload or download
                source_path : Path | ScalityPath
                    local path or scality path to the file or folder
                destination_path : Path | ScalityPath
                    local path or scality path to the file or folder
            Return:
                source_path : str
                    source path for the transfer
                destination_path : str
                    destination path for the transfer"""
        f_name = source_path.name
        if updown == 'upload':
            destination_path = destination_path.joinpath(f_name)
            destination_path = destination_path.full_path()
            if source_path.is_dir():
                source_path = source_path.joinpath('*')
        else:
            # Download
            if source_path.suffix:
                source_path = source_path.full_path()
            else:
                source_path = str(source_path.full_path()) + '*'
            destination_path = destination_path.joinpath(f_name)
            # folders
            if not destination_path.suffix:
                destination_path = str(destination_path) + path.sep

        self.progress_and_logg(f"source_path: {source_path}, destination_path: {destination_path}")
        return str(source_path), str(destination_path)

    def copy_command(self, source_path: str, destination_path: str, files_to_copy: int):
        """Copy command, using the s5cmd instead of boto3 as its up to 40 times faster"""
        # Copy data with status monitoring
        process = self.s5cmd.cp(source_path, destination_path)
        copied_files = 0
        error_list = []
        start_time = last_report_time = datetime.now()
        self.progress_and_logg(f'starting transfer: {start_time}')
        while process is not None and process.poll() is None:
            for line in process.stdout:
                copied_files += 1
                current_time = datetime.now()
                # Update progress bar if report_interval has passed or process completes
                if current_time - last_report_time >= timedelta(seconds=1) or process.poll() is not None:
                    self.progress_and_logg(f'copied {copied_files}/{files_to_copy}')
                    last_report_time = current_time
                if 'ERROR' in line:
                    self._error('Error during upload: {}'.format(line))
                    error_list.append(line)
        if not process:
            self._error("Process is None might be an issue or could be a fast transfer")
            exit_code = 0
        else:
            exit_code = process.poll()
        self.progress_and_logg(f'copied {copied_files}/{files_to_copy}')
        self.progress_and_logg(f'finished transfer: {datetime.now()}, it took: {datetime.now() - start_time}')
        if exit_code != 0 or len(error_list) > 0:
            self._error('Error occured during transfer!')
            return False
        return True


if __name__ == "__main__":
    from threading import Event
    from dotenv import load_dotenv
    from utils import setup_logger
    # Load env file
    load_dotenv()
    # Setup logger
    setup_logger()

    # source_path = r"C:\temp\testdata"
    # destination_path = "test"
    # destination_path = r'C:\\Users\\daale010\\Downloads'
    source_path = "C:\\Users\\tim\\Downloads\\test.txt"
    destination_path = r"test"

    delete_source = False
    starttime = datetime.now()
    logging.info("Starting data transfer: %s", starttime.strftime("%Y-%m-%d %H:%M:%S"))
    stop_worker = Event()
    worker = DataTransfer(stop_worker)
    worker.transfer('upload', source_path, destination_path, delete_source)
    #worker.transfer('download', source_path, destination_path, delete_source)
    endtime = datetime.now()
    logging.info("finished data transfer: %s", endtime.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("Duration: %s", endtime - starttime)
