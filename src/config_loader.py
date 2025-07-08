# config_loader.py v1.4.1

"""
This script is responsible for loading and providing configuration values from a specified environment file,
ensuring that the application runs with the correct settings.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Union, Tuple, Type, Any

# Setup logging
logger = logging.getLogger('config_loader')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def load_config(file_path: str = "config/config.env") -> Dict[str, Any]:
    """
    Load configuration values from an environment file.
    
    Arus:
    - file_path : str : Path to the environment file (default is "config.env").
    
    Returns:
    - dict : A dictionary containing the configuration values.
    """
    load_dotenv(file_path)


    # Predefined configuration parameters with their expected types
    config_params: Dict[str, Union[Tuple[Type, Any], Type]] = {
        "YOUTUBE_URL": (str, "https://www.youtube.com/@CNN10/videos"),
        "DOWNLOAD_PATH": (str,"./videos"),
        "VIDEO_EXTENSION": (str, ".mp4"), 
        "MAX_VIDEOS_TO_DOWNLOAD": (int, 1),
        "MAX_DOWNLOAD_RETRIES": (int, 3),
        "YOUTUBE_VIDEO_PATTERN": (str,"/watch\?v=([a-zA-Z0-9_-]+)"),
        "YOUTUBE_BASE_URL": (str,"https://www.youtube.com"),
        "SMTP_SERVER": (str,"smtp.gmail.com"),
        "SMTP_PORT": (int, 587),
        "SMTP_USERNAME": str,
        "SMTP_PASSWORD": str,
        "SMTP_SENDER": str,
        "SMTP_RECEIVER": str,
        "MORNING_RUN_HOUR": (int, 9),
        "MORNING_RUN_MINUTE": (int, 0),
        "EVENING_RUN_HOUR": (int, 21),
        "EVENING_RUN_MINUTE": (int, 0),
        "LOG_FILENAME": (str, "video_downloader.log"),
        "LOG_DIRECTORY": (str,"./log"),
        "VIDEO_DIRECTORY": (str, "./videos"),
        "VIDEO_EXTENSION": (str, ".mp4"),
        "DOWNLOAD_COMPLETE_MESSAGE": (str, "All downloads completed. {} videos downloaded."),
        "VIEW_METADATA_PROMPT": (str,"Would you like to view the metadata for downloaded videos? (y/n):"),
        "AFFIRMATIVE_RESPONSE": (str, "y"),
        "ALL_VIDEOS_DOWNLOADED_MESSAGE": (str,"All videos already downloaded. {} videos checked."),
        "REQUEST_TIMEOUT": (int, 10),
        "METADATA_FILE": (str, "./metadata/metadata.json"),
        "YOUTUBE_API_KEY": str,
        "BAIDU_APPID": str,
        "BAIDU_APIKEY": str,
        "BAIDU_SECRETKEY": str,
        "BAIDU_SIGNKEY": str,
        "BAIDU_REDIRECT_URI": str,
        "BAIDU_APP_NAME": str,
        "BAIDU_ACCESS_TOKEN": str,
        "DEFAULT_METADATA_EXTRACTOR": (str, "yt_dlp"),
        "METADATA_DIRECTORY": (str, "./metadata"),
        "MAX_RESOLUTION": (int, 720)
    }

    config = {}
    for key, expected_type_default in config_params.items():
        value = os.getenv(key)
        
        if isinstance(expected_type_default, tuple):
            expected_type, default_value = expected_type_default
            if value is None:
                value = default_value
        else:
            expected_type = expected_type_default
        
        if expected_type is int:
            try:
                value = int(value)
            except ValueError:
                error_message = f"{key} value in config is not a valid integer."
                logger.error(error_message)
                raise ValueError(error_message)
        
        config[key] = value
    
    return config

# Example usage
if __name__ == "__main__":
    try:
        config_data = load_config()
        print(config_data)
    except ValueError as e:
        print(f"An error occurred: {e}")