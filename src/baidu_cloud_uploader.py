# baidu_cloud_uploader.py v1.3.4
"""
Module for uploading files to Baidu Netdisk using the Baidu Cloud API,
handling tasks such as pre-creating upload tasks, uploading file slices,
and merging slices to complete the upload.
"""

import os
import sys
import json
import hashlib
import requests
import logging
import urllib3
from tqdm import tqdm
from dotenv import load_dotenv
from utils import setup_logging

class BaiduCloudUploader:
    def __init__(self, file_path=None, config_path: str = './config.env') -> None:
    
        """
        Initializes the uploader with access token and app name.
        
        Args:
        - config_path : str : Path to the configuration file (default is './config.env').
        """
        # Load environment variables from the config.env file
        load_dotenv(dotenv_path=config_path)
        setup_logging()
        self.logger = logging.getLogger('baidu_cloud_uploader')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.access_token = os.getenv('BAIDU_ACCESS_TOKEN')
        self.app_name = os.getenv('BAIDU_APP_NAME')
        
        if not self.access_token or not self.app_name:
            self._log_error('ACCESS_TOKEN or APP_NAME is missing in the configuration file.')
            raise ValueError("ACCESS_TOKEN or APP_NAME is missing in the configuration file.")
        
        if not file_path:
            self._log_info("Usage: python baidu_cloud_uploader.py <FILE_PATH>")  
            print("Usage: python baidu_cloud_uploader.py <FILE_PATH>")
            sys.exit(1)

    def _log_info(self, message: str) -> None:
        """
        Log info messages with a consistent format.

        Args:
        - message : str : Message to be logged.
        """
        self.logger.info(message)
        # print(message)

    def _log_error(self, message: str) -> None:
        """
        Log error messages with a consistent format.
        
        Args:
        - message : str : Error message to be logged.
        """
        self.logger.error(message)
        # print(f"ERROR: {message}")

    def send_request(self, url: str, method: str, headers: dict = None, params: dict = None, data: dict = None, files: dict = None) -> dict:
        """
        Send an HTTP request and return the response.

        Args:
        - url : str : The URL to send the request to.
        - method : str : The HTTP method to use ('GET', 'POST', etc.).
        - headers : dict : (Optional) HTTP headers to include with the request.
        - params : dict : (Optional) URL parameters to include with the request.
        - data : dict : (Optional) Data to include with a POST request.
        - files : dict : (Optional) Files to include with a POST request.
        
        Returns:
        - dict : The JSON response from the server.
        """
        if method == "POST":
            response = requests.post(url, headers=headers, params=params, data=data, files=files, verify=False)
        else:
            response = requests.get(url, headers=headers, params=params, data=data, verify=False)
        return response.json()  # Assuming the response is already in JSON format

    def precreate_file(self, file_path, file_size, block_list):
        """
        Precreate the file on Baidu Netdisk.
        
        Args:
        - file_path : str : Path to the file to be uploaded.
        - file_size : int : Size of the file to be uploaded.
        - block_list : list : List of MD5 hashes of the file blocks.

        Returns:
        - dict : Response from the server, assumed to be in JSON format.
        """
        print("Precreating file...")
        url = "https://pan.baidu.com/rest/2.0/xpan/file?method=precreate"
        headers = {"User-Agent": "pan.baidu.com"}
        params = {
            "access_token": self.access_token,
        }
        data = {
            "path": f"/apps/{self.app_name}/{os.path.basename(file_path)}",
            "size": file_size,
            "isdir": 0,
            "autoinit": 1,
            "block_list": json.dumps(block_list)
        }

        self.logger.info(f"Sending POST request to: {url}")
        response = requests.post(url, headers=headers, params=params, data=data, verify=False)
        return response.json()  # Assuming the response is already in JSON format


    def upload_slice(self, file_path, upload_id, partseq, block_size):
        """
        Upload a single slice of the file.

        Args:
        - file_path : str : Path to the file being uploaded.
        - upload_id : str : Upload ID received from the precreate step.
        - partseq : int : Sequence number of the part being uploaded.
        - block_size : int : Size of each slice.

        Returns:
        - dict : Response from the server.
        """
        url = f"https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?method=upload&access_token={self.access_token}"
        
        with open(file_path, "rb") as f:
            f.seek(partseq * block_size)     # Seek to the start of the slice
            file_slice = f.read(block_size)  # Read the slice from the file

        params = {
            "type": "tmpfile",
            "path": f"/apps/{self.app_name}/{os.path.basename(file_path)}",
            "uploadid": upload_id,
            "partseq": partseq
        }
        files = {
            'file': ("blob", file_slice)
        }

        self.logger.info(f"Uploading slice {partseq} for file {file_path}")
        response = requests.post(url, params=params, files=files)
        self.logger.info(f"Received response with status code: {response.status_code} for slice {partseq}")
        
        return response.json()

    def create_file(self, file_path, upload_id, file_size, block_list):
        """
        Finalize the file upload by merging all slices.

        Args:
        - file_path : str : Path to the file being uploaded.
        - upload_id : str : Upload ID received from the precreate step.
        - file_size : int : Total size of the file.
        - block_list : list : List of MD5 hashes of the file blocks.

        Returns:
        - dict : Response from the server.
        """
        print("Creating file...")
        url = "https://pan.baidu.com/rest/2.0/xpan/file?method=create"
        headers = {"User-Agent": "pan.baidu.com"}
        params = {
            "access_token": self.access_token,
        }
        data = {
            "path": f"/apps/{self.app_name}/{os.path.basename(file_path)}",
            "size": file_size,
            "isdir": 0,
            "uploadid": upload_id,
            "block_list": json.dumps(block_list)
        }

        self.logger.info(f"Sending POST request to: {url}")
        response = requests.post(url, headers=headers, params=params, data=data)
        response_json = response.json()

        if response_json.get('errno', -1) == 0:
            print("File creation successful!")
        else:
            print(f"File creation failed. Full response: {response_json}")

        return response.json()

    def upload_slices(self, file_path, upload_id, total_slices, block_size):
        """
        Upload slices of the file with a progress bar.

        Args:
        - file_path : str : Path to the file being uploaded.
        - upload_id : str : Upload ID received from the precreate step.
        - total_slices : int : Total number of slices.
        - block_size : int : Size of each slice.

        No explicit return value.
        """
        print(f"Uploading {total_slices} slices. Please be patient.")
        with tqdm(total=total_slices, unit="slice", desc="Uploading slices", ncols=100, position=0, leave=True) as pbar:
            for i in range(total_slices):
                try:
                    upload_response = self.upload_slice(file_path, upload_id, i, block_size)
                    pbar.update(1)
                except Exception as e:
                    self._log_error(f"Error uploading slice {i+1}/{total_slices}: {e}")

    def upload_file(self, file_path, block_size=4 * 1024 * 1024):
        """
        Handle the entire file upload process.

        
        Args:
        - file_path : str : Path to the file being uploaded.
        - block_size : int : Size of each block (default is 4MB).

        Returns:
        - dict : Response from the server after the file creation step.
        """
        file_size = os.path.getsize(file_path)

        # Calculate MD5 for each block
        block_list = []
        with open(file_path, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                md5_hash = hashlib.md5(block).hexdigest()
                block_list.append(md5_hash)

        # Precreate
        precreate_response = self.precreate_file(file_path, file_size, block_list)
        upload_id = precreate_response['uploadid']
        print("Precreate successful!")

        total_slices = len(block_list)  # Calculate the total number of slices
        
        # Upload each slice with progress bar
        self.upload_slices(file_path, upload_id, total_slices, block_size)

        # Create file
        create_response = self.create_file(file_path, upload_id, file_size, block_list)
        
        return create_response

if __name__ == "__main__":
    """
    If this module is run directly, it will upload the file specified in the command line arguments.
    If the number of arguments is incorrect, it will print the usage instructions.

    Args:
    - sys.argv[1] : str : Path to the file to be uploaded.

    Returns:
    - None
    """
    file_path_to_upload = sys.argv[1] if len(sys.argv) == 2 else None
    uploader = BaiduCloudUploader(file_path=file_path_to_upload)
    if file_path_to_upload:
        uploader.upload_file(file_path_to_upload)
