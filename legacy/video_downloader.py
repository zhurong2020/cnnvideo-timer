"""
video_downloader.py version 1.9.1
This module automatically downloads the latest CNN10 video using yt-dlp, ensuring titles are sanitized and saved to the designated directory.
"""

# Standard library imports
import os
import logging

# Third-party imports
import yt_dlp.utils
from yt_dlp import YoutubeDL

# Local application imports
from config_loader import load_config
from downloader_checker import DownloaderManager
from utils import setup_logging, create_directories, sanitize_filename
from link_extractor import VideoLinkExtractor
from metadata_manager import MetadataManager  
# from baidu_cloud_uploader import BaiduCloudUploader


# Load configuration file
config = load_config()

# Set up a logger for this module
logger = logging.getLogger('video_downloader')

class YTDownloader:
    def __init__(self, output_directory=None):
        """Initialize the YTDownloader with an output directory.

        Args:
        - output_directory : str : The directory where the downloaded videos will be saved.
        """
        if not output_directory:
            output_directory = config["DOWNLOAD_PATH"]
        self.output_directory = output_directory

        self.setup_youtube_downloader()

    def setup_youtube_downloader(self):
        """Setup the yt-dlp downloader with necessary options.
    
        Args:
            self (YTDownloader): An instance of YTDownloader.

        Returns:
            None
        """
        yt_dlp.utils.std_headers['User-Agent'] = "Mozilla/5.0 ..."
        self.ydl_opts = {
            # 'format': f'best[height<=720][ext={config["VIDEO_EXTENSION"]}]',  # Using VIDEO_EXTENSION from config
            'format': '18', # 640*360 mp4 avc1.42001E, about 34MB
            'outtmpl': os.path.join(self.output_directory, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_progress': True,
            'no_warnings': True,
            'progress_hooks': [self.hook]
        }
        self.ydl = YoutubeDL(self.ydl_opts)

    def hook(self, d):
        """Hook function to handle download progress.

        Args:
        - d : dict : A dictionary containing information about the download process such as 'status', '_percent_str', '_total_bytes_str', and '_speed_str'.
        
        Returns:
        - None
        """
        if d['status'] == 'downloading':
            print(f"\r[download] {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}", end='', flush=True)
        elif d['status'] == 'finished':
            print("")  # Print a new line to move the cursor to a new line after download is finished
        
    def get_video_info(self, video_url):
        """Get video information without downloading the video.
        
        Args:
        - video_url : str : The URL of the video to extract information from.
        
        Returns:
        - dict : A dictionary containing various pieces of information about the video such as 'title', 'uploader', 'upload_date', etc.
        """
        return self.ydl.extract_info(video_url, download=False)

    def download_video(self, video_url):
        """Download the video and save it to the specified directory.
        
        Args:
        - video_url : str : The URL of the video to be downloaded.
        
        Returns:
        - None : This method returns None. It downloads the video and saves it to the specified directory.
        """
        info = self.ydl.extract_info(video_url, download=False)
        clean_title = sanitize_filename(info['title'])
        self.ydl_opts['outtmpl'] = os.path.join(self.output_directory, clean_title + '.%(ext)s')
        self.ydl = YoutubeDL(self.ydl_opts)  # Re-initializing YoutubeDL to use the updated options
        self.ydl.download([video_url])
        # logger.info(f"Successfully downloaded {clean_title}.") 

def display_metadata(last_downloaded_titles, config):
    """Display metadata of the downloaded videos.
    
    Args:
    - last_downloaded_titles : list of str : A list of titles of the videos that were downloaded in the last run.
    - config : dict : A configuration dictionary containing various settings and parameters used throughout the script.
    
    Returns:
    - None
    """
    mm = MetadataManager(config)
    videos_metadata = mm.get_all_metadata()
    for metadata in videos_metadata:
        if metadata.get('title') in last_downloaded_titles:
            print(f"Title: {metadata.get('title', 'N/A')}")
            print(f"Uploader: {metadata.get('uploader', 'N/A')}")
            print(f"Published At: {metadata.get('published_at', 'N/A')}")
            print(f"Upload Date: {metadata.get('upload_date', 'N/A')}")
            print(f"Duration: {metadata.get('duration', 'N/A')}")
            print(f"View Count: {metadata.get('view_count', 'N/A')}")
            print(f"Description: {metadata.get('description', 'N/A')}")
            print("-"*50, "\n")

def main():
    """
    Main function that orchestrates the video downloading process.
    It extracts video links, downloads videos, and uploads them to Baidu Netdisk.
    
    Returns:
    - list : A list containing the filenames of the videos that were successfully downloaded.
    """

    # Check if config.env file exists
    if not os.path.exists('config/config.env'):
        print("Error: config/config.env file not found.")
        print("Please copy config/configenv to config/config.env and configure it for your environment.")
        exit(1)
        
    # Setup logging and directories
    setup_logging()
    create_directories()
    
    # Extract video URLs
    url = config["YOUTUBE_URL"]
    logger.debug(f"Extracting video links from: {url}")
    videos = VideoLinkExtractor.extract_video_links_from_page(url, config["MAX_VIDEOS_TO_DOWNLOAD"])
    logger.info(f"Extracted {len(videos)} video links.")
    
    # Initialize downloader and checker
    downloader = YTDownloader()
    checker = DownloaderManager(videos, downloader, config)
    logger.info("Starting the checking and downloading process.")
    downloaded_filenames = checker.check_and_download()  
    # Instantiate BaiduCloudUploader
    # uploader = BaiduCloudUploader()  
    # Temporarily disabling Baidu Netdisk upload feature, to be enhanced in future versions.
    # if downloaded_filenames:
        # for filename in downloaded_filenames:
            # video_path = os.path.join(config["DOWNLOAD_PATH"], filename)
            # uploader.upload_file(video_path) 

    logger.info("Script finished.")
    return downloaded_filenames  # Modified to return downloaded filenames

if __name__ == "__main__":
    main()
    input("Press Enter to continue...")
