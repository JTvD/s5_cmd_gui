import boto3
import logging
import re
from psutil import disk_usage
from datetime import datetime
from shutil import rmtree
from os import getenv, path
from pathlib import Path
from path import ScalityPath
import platform
if platform.system() == "Windows":
    import win32com.client as com
    import pythoncom
else:
    raise EnvironmentError("This script can only be run on Windows.")


class DataOperation():
    def __init__(self):
        self.bucket_name = getenv('BUCKETNAME')
        self.bucket_size = getenv('BUCKETSIZE')
        self.endpoint_url = getenv('ENDPOINT')
        self.aws_profile = getenv('AWS_PROFILE')
        self.processed_files = []
        try:
            session = boto3.Session(profile_name=self.aws_profile)
            self.s3 = session.client('s3', endpoint_url=self.endpoint_url)
        except Exception as e:
            msg = "Could not open session: {}".format(e)
            logging.error(msg)
            exit(1)

        if not self.check_bucket(self.bucket_name):
            msg = "Could not find bucket: {}".format(self.bucket_name)
            logging.error(msg)

    def check_bucket(self, bucket_name: str):
        """Check if the bucket exists
            Args:
                bucket_name: str
                    name of the bucket
            Return:
                boolean
                    True is the bucket exists, False if not
        """
        response = self.s3.list_buckets()
        for bucket in response['Buckets']:
            if bucket['Name'] == bucket_name:
                return True
        return False

    # def check_local_folder_exists(self, source_folder: str):
    #     """Check if the folder exists on the local disk
    #         Args:
    #             source_folder: str
    #                 path to the folder on the local disk
    #         Return:
    #             boolean
    #                 True if the folder exists, False otherwise
    #     """
    #     return path.exists(source_folder)

    def check_scality_path_exists(self, scality_path: str):
        """check if the destination folder already exists to avoid accident overwrites
            Args:
                scality_path: str
                    name of the file or folder
            Return:
                boolean
                    Trur if the folder exists, False otherwise
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=scality_path)
        except Exception as e:
            logging.warning("Error in checking for {} in bucket {}: {}".format(scality_path, self.bucket_name, e))
        return 'Contents' in response

    def get_local_freespace(self, data_path: Path):
        """Retreive the free space on the local disk
            Args:
                path: Path
            Return:
                free_space: int
                    number of bytes free on the disk
        """
        usage = disk_usage(data_path.drive + f'{path.sep}')
        return usage.free

    def get_bucket_freespace(self, foldername: str = ''):
        """Retreive the free space in the bucket
            Args:
                foldername: str
                    name of the folder in the bucket
            Return:
                num_files : int
                    number of files in the bucket
                total_size: int
                    total size of the files in the folder
                free_space: int
                    number of bytes free in the bucket
        """
        bucket_free_size = 0
        total_size = 0
        num_files = 0
        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            # Iterate over all objects in the bucket
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=foldername):
                total_size += sum(obj['Size'] for obj in page.get('Contents', []))
                num_files += len(page.get('Contents', []))
            bucket_free_size = self.parse_size(self.bucket_size) - total_size
        except Exception as e:
            logging.warning("Failed to compute free space for bucket {}: {}".format(self.bucket_name, e))
        return (num_files, total_size, bucket_free_size)

    def get_local_datasize(self, local_path: Path):
        """Get the size of a file or folder on the local disk
            Args:
                local_path: Path
                    path to the file or folder on the local disk
            Return:
                num_files: int
                    number of files in the folder
                size: int
                    size of the file or folder in bytes
        """
        if local_path.is_file():
            return (1, local_path.stat().st_size)
        else:
            return self.get_local_foldersize(local_path)

    def get_local_foldersize(self, local_path: Path):
        """ os.walk and pathlib take quite some time, on Windows the com object provides a fast alternative
            Args:
                local_path: Path
                    complete path to the folder on the local disk
            Return:
                num_files: int
                    number of files in the folder
                foldersize: int
                    size of the folder on disk
        """
        logging.info("Calculating size of: {}".format(local_path))
        if platform.system() == "Windows":
            # Enable com usage from threads
            pythoncom.CoInitialize()
            fso = com.Dispatch("Scripting.FileSystemObject")
            folder = fso.GetFolder(local_path)
            size = folder.Size
            num_files = sum(1 for _ in local_path.glob('**/*') if _.is_file())
        else:
            num_files = 0
            size = 0
            for f in local_path.glob('**/*'):
                if f.is_file():
                    num_files += 1
                    size += f.stat().st_size
        return (num_files, size)

    def parse_size(self, size: str):
        """ The units are added added with the value, this function converts it to bytes
            Args:
                size: str
                    size string in units
            Return:
                int
                    size in bytes
        """
        units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40,
                 "": 1, "KIB": 10**3, "MIB": 10**6, "GIB": 10**9, "TIB": 10**12}
        m = re.match(r'^([\d\.]+)\s*([a-zA-Z]{0,3})$', str(size).strip())
        number, unit = float(m.group(1)), m.group(2).upper()
        return int(number * units[unit])

    def size_fmt(self, num: int):
        """ For vizualisation it is nicer to show the value in a bigger unit than bytes
            Args:
                num: int
                    size in bytes
            Return:
                str
                    size unit
        """
        for unit in ("", "KB", "MB", "GB", "TB", "PB"):
            if abs(num) < 2**10:
                return f"{num:3.1f} {unit}"
            num /= 2**10
        return "Not implemented"

    def delete_local_data(self, local_path: Path):
        """ Remove data in folder
            Args:
                local_path: Path
                    path to the files on the local file system
            Return:
                -
        """
        logging.info("Removing: {}".format(local_path))
        if local_path.is_file():
            local_path.unlink()
        elif local_path.is_dir():
            rmtree(local_path)

    def delete_bucket_data(self, prefix: ScalityPath = '*'):
        """Deleting all the objects in the bucket with the specified prefix: foldername
            Args:
                prefix: str
                    path to the files in the bucket
            Return:
                -
        """
        try:
            while True:
                # List objects in batches of 1000
                response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=str(prefix) + '/')
                if 'Contents' not in response:
                    break  # Exit if the bucket is empty

                # Delete the objects in a batch
                delete_keys = {'Objects': [{'Key': obj['Key']} for obj in response['Contents']]}
                self.s3.delete_objects(Bucket=self.bucket_name, Delete=delete_keys)

                # Handle pagination if the bucket is very large
                if not response.get('IsTruncated', False):
                    break

            logging.info(f"All objects with prefix '{prefix}' deleted from bucket.")
        except Exception as e:
            logging.warning(f"Failed to delete objects with prefix '{prefix}': {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    from utils import setup_logger
    setup_logger()
    load_dotenv()
    data_ops = DataOperation()
    data_ops.get_local_freespace(Path("C:\\Users\\tim\\Downloads\\tim\\1"))
    a, b = data_ops.get_local_foldersize(Path("C:\\Users\\tim\\Downloads\\tim\\1"))
    # Example usage:
    # print(data_ops.get_local_foldersize("C:/traitseeker_testdata"))
    print(f'starting freespace check {datetime.now()}')
    print(data_ops.get_bucket_freespace('20240319/1/'))
    print(data_ops.size_fmt(30000000))
