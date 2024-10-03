"""Custom version of https://pypi.org/project/s5cmdpy/
Unfortunately their implementation does not accept additional parameters
"""
import logging
import requests
import subprocess
from os import access, getenv, X_OK
from platform import machine, system
from pathlib import Path


class S5CmdRunner:
    """
    A class that provides methods for interacting with s5cmd, a command-line tool for efficient S3 data transfer.

    Attributes:
        s5cmd_path (str): The path to the s5cmd executable.
    """

    def __init__(self):
        # if on windows
        if system()[0].upper() == "W":
            binary_name = 's5cmd.exe'
        else:
            binary_name = 's5cmd'
        # Exe stored in the folder with python code
        current_directory = Path(__file__).resolve().parent
        self.s5cmd_path = current_directory.joinpath(binary_name)

        if not self.has_s5cmd():
            self.get_s5cmd()

    def has_s5cmd(self) -> bool:
        """ Check if the s5cmd is installed """
        return self.s5cmd_path.exists() and self.s5cmd_path.is_file() and access(self.s5cmd_path, X_OK)

    def get_s5cmd(self) -> None:
        """ Install the s5cmds"""
        arch = machine()
        s5cmd_url = ""

        if arch == 'x86_64':
            s5cmd_url = "https://huggingface.co/kiriyamaX/s5cmd-backup/resolve/main/s5cmd_2.2.2_Linux-64bit/s5cmd"
        elif arch == 'aarch64':
            s5cmd_url = "https://huggingface.co/kiriyamaX/s5cmd-backup/resolve/main/s5cmd_2.2.2_Linux-arm64/s5cmd"

        # windows support
        elif arch == 'AMD64':
            s5cmd_url = "https://huggingface.co/kiriyamaX/s5cmd-backup/resolve/main/s5cmd_2.2.2_Windows-amd64/s5cmd.exe"
        else:
            raise ValueError("Unsupported architecture")

        try:
            response = requests.get(s5cmd_url)
            response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
            with open(self.s5cmd_path, 'wb') as file:
                file.write(response.content)
            # Set executable permissions on Unix-like systems
            if system()[0].upper() != "W":
                self.s5cmd_path.chmod(0o755)
            logging.info("s5cmd downloaded and installed successfully.")
        except requests.exceptions.RequestException as e:
            logging.error("Failed to download s5cmd: {},\
                           download it manually from: https://github.com/peak/s5cmd/releases".format(e))

    def _call_function(self, command: list, capture_output: bool =False):
        """ Call the s5cmds
        Args:
            command: list
                command to execute
            capture_output: bool
                capture the output or not
        Returns:
            process: subprocess.Popen / None
                A process when capture_output is True
        """
        if capture_output:
            try:
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                return process
            except Exception as e:
                logging.error("Error starting subprocess: {}".format(e))
                return None
        else:
            result = subprocess.run(command)
            return result

    def _generate_cmd(self, command: str, source: str, destination: str):
        """ Generate the s5cmd with arguments
        
            Args:
                command: str
                    command to execute
                source: str
                    source path
                destination: str
                    destination path
            Returns:
                s5cmd_with_params: list
                    command with arguments
        """
        endpoint = getenv('ENDPOINT')
        profile = getenv('AWS_PROFILE')
        workers = getenv('AWS_WORKERS')
        if not (endpoint and profile and workers):
            logging.error(f"Incomplete environment: ENDPOINT = \
                          {endpoint}, AWS_PROFILE = {profile}, AWS_WORKERS = {workers}")
            exit(1)

        s5cmd_with_params = [
            self.s5cmd_path,
            '--endpoint-url',
            endpoint,
            '--profile',
            profile,
            '--numworkers',
            workers,
            command,
            source,
            destination
        ]
        return s5cmd_with_params

    def cp(self, source: str, destination: str, simplified_print: bool = True):
        """ Copy a file or folder from/to S3
        Args:
            source: str
                source path, can be a file or folder
            destination: str
                destination path, can be a file or folder
            simplified_print:
                return the status or not
        Returns:
            the process to monitor the status
        """
        command = self._generate_cmd('cp', source, destination)
        process = self._call_function(command, capture_output=simplified_print)
        if simplified_print and process and process.stdout:
            # Assuming we don't parse txt_uri to count commands, we leave total=None for an indeterminate progress bar
            return process
        else:
            return None

    def sync(self,  source: str, destination: str, simplified_print: bool = True):
        """ Sync a file or folder from/to S3
        Args:
            source: str
                source path, can be a file or folder
            destination: str
                destination path, can be a file or folder
            simplified_print:
                return the status or not
        Returns:
            the process to monitor the status
        """
        command = self._generate_cmd('sync', source, destination)
        process = self._call_function(command, capture_output=simplified_print)
        if simplified_print and process and process.stdout:
            # Assuming we don't parse txt_uri to count commands, we leave total=None for an indeterminate progress bar
            return process
        else:
            return None


if __name__ == "__main__":
    # S5cmd delete requires more arguments
    from dotenv import load_dotenv
    from datetime import datetime, timedelta
    from utils import setup_logger
    setup_logger()
    load_dotenv()
    runner = S5CmdRunner()
    destination_path = 's3://<bucketname>/<folders>'
    process = runner.cp('C:/<folder with test data>', destination_path, True)
    # Monitor progress
    start_time = last_report_time = datetime.now()
    logging.info(f'starting transfer: {start_time}')
    processed_files = 0
    error_list = []
    while process is not None and process.poll() is None:
        for line in process.stdout:
            processed_files += 1
            current_time = datetime.now()
            # Update progress bar if report_interval has passed or process completes
            if current_time - last_report_time >= timedelta(seconds=1) or process.poll() is not None:
                logging.info(processed_files)
                last_report_time = current_time
            if 'ERROR' in line:
                logging.error('Error during upload: {}'.format(line))
                error_list.append(line)
    exit_code = process.poll()
    logging.info(f'finished transfer: {datetime.now()}, it took: {datetime.now() - start_time}')
    if exit_code != 0 or len(error_list) > 0:
        logging.error('Error occured during transfer!')
    else:
        logging.info('Transfer completed successfully')
