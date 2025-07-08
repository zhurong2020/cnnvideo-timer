"""
link_extractor.py v1.4.1

This module extracts video links from a specified webpage. 
"""
import requests
import re
import logging
from config_loader import load_config

logger = logging.getLogger('link_extractor')

config = load_config()

class VideoLinkExtractor:
    
    @staticmethod
    def extract_video_links_from_page(url=None, max_links=None, video_pattern=None, 
                                      base_url=None, timeout=None) -> list:
        """
        Extract video links from a webpage.

        Args:
        - url (str): The URL of the webpage to extract video links from. Defaults to config["YOUTUBE_URL"].
        - max_links (int): The maximum number of links to extract. Defaults to config["MAX_VIDEOS_TO_DOWNLOAD"].
        - video_pattern (str): The regex pattern to match video links. Defaults to config["YOUTUBE_VIDEO_PATTERN"].
        - base_url (str): The base URL to prepend to relative video links. Defaults to config["YOUTUBE_BASE_URL"].
        - timeout (float): The timeout for the HTTP request in seconds. Defaults to config.get("REQUEST_TIMEOUT", 10).

        Returns:
        - list: A list of extracted video links, or an empty list if an error occurs.
        """
        url = url or config["YOUTUBE_URL"]
        max_links = max_links or config["MAX_VIDEOS_TO_DOWNLOAD"]
        video_pattern = video_pattern or config["YOUTUBE_VIDEO_PATTERN"]
        base_url = base_url or config["YOUTUBE_BASE_URL"]
        timeout = timeout or config.get("REQUEST_TIMEOUT", 10)

        # Ensure max_links is an integer
        if not isinstance(max_links, int):
            try:
                max_links = int(max_links)
            except ValueError:
                logger.error(f"Invalid MAX_VIDEOS_TO_DOWNLOAD value: {max_links}. It must be an integer.")
                return []

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  

            video_links = re.findall(video_pattern, response.text)
            full_links = [f'{base_url}/watch?v={link}' for link in video_links]
            return full_links[:max_links]

        except requests.Timeout:
            logger.error(f"Request to {url} timed out after {timeout} seconds.")
        except requests.RequestException as e:
            logger.error(f"Error fetching the page at {url}. Error: {e}")
        
        return []

# Usage example
if __name__ == '__main__':
    links = VideoLinkExtractor.extract_video_links_from_page()
    print(links)
