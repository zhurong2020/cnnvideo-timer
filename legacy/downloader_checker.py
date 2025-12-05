"""
 downloader_checker.py v2.4.1

This script is responsible for checking the availability of new videos and managing their download process. It utilizes the video_downloader module to perform the actual download, and it ensures that each video is only downloaded once by checking against a record of previously downloaded videos.
"""

import time
import os
import logging
import random  
from typing import List, Tuple, Any, Optional

import yt_dlp

from utils import sanitize_filename
from config_loader import load_config
from metadata_manager import MetadataManager

logger = logging.getLogger(__name__)

config = load_config()

class DownloaderManager:

    def __init__(self, videos: List[dict], downloader: Any, config: dict) -> None:
        """Initialize the DownloaderManager with videos to be downloaded, a downloader, and configuration.
        
        Args:
        - videos : list : A list of video information to be downloaded.
        - downloader : YTDownloader : An instance of YTDownloader to perform the actual download.
        - config : dict : Configuration parameters.
        
        Returns:
        - None
        """
        self.videos = videos
        self.downloader = downloader
        self.metadata_manager = MetadataManager(config)  # 创建MetadataManager的实例，并传递配置

    def should_download(self, video_info: dict) -> bool:
        """Determine if a video should be downloaded based on its title and metadata.
        
        Args:
        - video_info : dict : Information about the video to be downloaded.
        
        Returns:
        - bool : True if the video should be downloaded, False otherwise.
        """
        sanitized_title = sanitize_filename(video_info['title'])
        video_path = os.path.join(self.downloader.output_directory, sanitized_title + config["VIDEO_EXTENSION"])

        # Check if the file exists in the file system and metadata exists.
        return not (os.path.exists(video_path) and self.metadata_manager.query_metadata(video_info['id']))

    def store_video_metadata(self, video_info: dict) -> None:
        """Store video metadata using MetadataManager.

        Parameters:
        - video_info : dict : Information about the video to be downloaded.

        Returns:
        - None
        """
        sanitized_title = sanitize_filename(video_info['title'])
        video_path = os.path.join(self.downloader.output_directory, sanitized_title + '.mp4')
        metadata = {
            'id': video_info['id'], 
            'title': video_info['title'],
            'url': video_info['url'],
            'description': video_info['description'],
            'published_at': video_info.get('published_at', 'Unknown Date'),
            'video_path': video_path,
            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        self.metadata_manager.save_or_update_metadata(metadata)

    def check_and_download(self) -> List[str]:
        """Prepare to download videos and return a list of filenames of downloaded videos.

        Args:
        - None
                
        Returns:
        - List[str] : A list of filenames of the downloaded videos.
        """
        downloaded_filenames = []  # Used to store filenames of downloaded videos
        downloaded_count = 0
        # downloaded_titles = []  

        logger.info(f"Preparing to download {len(self.videos)} videos...")

        for video_url in self.videos:
            try:
                downloaded_title, cleaned_filename = self._download_single_video(video_url)  # Get original title and cleaned filename
                if cleaned_filename: # If there's a cleaned filename, the video has been successfully downloaded
                    downloaded_filenames.append(cleaned_filename)   # Save cleaned filename
                    downloaded_count += 1
            except Exception as e:
                logger.error(f"Failed to download video from {video_url}. Error: {e}.", exc_info=True)  # Logging more error info
                
        return downloaded_filenames
    
    def _download_single_video(self, video_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Try downloading a single video and return the title if successful.
        
        Args:
        - video_url : str : URL of the video to be downloaded.
        
        Returns:
        - tuple[Optional[str], Optional[str]] : Tuple containing the title and filename of the downloaded video if successful, None otherwise.
        """
        retries = 0
        max_retries = config.get("MAX_DOWNLOAD_RETRIES", 3)  # Getting the value from config with a default

        while retries < max_retries:
            try:
                video_info = self.downloader.get_video_info(video_url)

                if self.should_download(video_info):
                    print(f"Downloading: {video_info['title']}")
                    self.downloader.download_video(video_url)
                    self.store_video_metadata(video_info)
                    sanitized_title = sanitize_filename(video_info['title']) + config["VIDEO_EXTENSION"]
                    return video_info['title'], sanitized_title  # Return the title and filename of the downloaded video
                else:
                    logger.info(f"Video {video_info['title']} already exists. Skipping download.")
                    print(f"Video {video_info['title']} already exists. Skipping download.")
                    return None, None  # Return None if the video was not downloaded

            except Exception as e:
                retries += 1
                logger.error(f"Error downloading video from {video_url}. Error: {e}. Retrying {retries}/{max_retries}...")
                time.sleep((retries + 1) * 5 + random.randint(1, 5))  # Exponential backoff with randomness

        logger.error(f"Failed to download video from {video_url} after {max_retries} retries.")
        return None, None  # Return None if the download failed after retries
    
    def get_suitable_formats(self, video_url: str) -> List[str]:
        """Get a list of suitable format IDs for a given video URL.

        Args:
        - video_url : str : The URL of the video to get suitable formats for.

        Returns:
        - List[str] : A list of strings representing suitable format IDs for the video, sorted by file size.
        """
        max_resolution = config.get('MAX_RESOLUTION') 
        ydl_opts = {
        'quiet': True,
        'no_progress': True,
        'no_warnings': True,
        }
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            
            suitable_formats = [
                f for f in formats 
                if f['ext'] == 'mp4' and f.get('height') and f['height'] <= max_resolution
            ]
            
            suitable_formats.sort(key=lambda f: f['filesize'] or 0)
            
            format_ids = [str(f['format_id']) for f in suitable_formats]
            
            return format_ids
        
    def download_video_with_format(self, video_url: str) -> None:
        """Download a video in a suitable format from a list of format IDs.
        
        Args:
        - video_url : str : The URL of the video to be downloaded.

        Returns:
        - None
        """
        format_list = self.get_suitable_formats(video_url)
        
        for fmt in format_list:
            try:
                 # Attempt to download
                self.downloader.download_video(video_url, fmt)
                # If download is successful, exit the loop
                break
            except Exception as e:
                # If download fails, continue trying with other formats
                logger.error(f"Error downloading {video_url} with format {fmt}: {e}")
