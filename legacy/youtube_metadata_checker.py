"""
youtube_metadata_checker.py v1.0.2
This module extracts and logs metadata from YouTube videos using both the YouTube Data API and yt-dlp.
It's designed to work seamlessly with a list of video URLs obtained from a VideoLinkExtractor.
"""
import requests
import json
import re
import sys
import logging
import argparse
import yt_dlp
from datetime import datetime
from typing import Optional, Dict
from config_loader import load_config
from link_extractor import VideoLinkExtractor

# Create a logger object
logger = logging.getLogger('youtube_metadata_checker')
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

config = load_config()

API_KEY = config["YOUTUBE_API_KEY"]

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'Error: {message}\n')
        self.print_help()
        sys.exit(2)

def get_metadata_from_api(video_id: str) -> dict:
    """
    Get metadata from YouTube Data API.
    
    Args:
        video_id (str): The ID of the YouTube video.
    
    Returns:
        dict: The metadata obtained from the API.
    """
    part_parameters = 'snippet,statistics,contentDetails'
    url = f"https://www.googleapis.com/youtube/v3/videos?part={part_parameters}&id={video_id}&key={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            item = items[0]
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            metadata_api = {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'published_at': snippet.get('publishedAt'),
                'channel_title': snippet.get('channelTitle'),
                'view_count': statistics.get('viewCount'),
                'like_count': statistics.get('likeCount'),
                'dislike_count': statistics.get('dislikeCount'),
                'comment_count': statistics.get('commentCount'),
                'tags': snippet.get('tags'),
                'category_id': snippet.get('categoryId'),
                'duration': content_details.get('duration'),
            }
            return metadata_api
    else:
        logger.error(f"API Error: {response.status_code}, {response.text}")
        return None

def get_metadata_from_yt_dlp(video_id: str) -> Optional[Dict]:
    """
    Retrieve video metadata using the yt-dlp library.

    Parameters:
    - video_id : str : The ID of the YouTube video.

    Returns:
    - dict : A dictionary containing metadata such as title, description, publication date, channel title, and various counts (views, likes, dislikes, comments).
             Returns None if there's an error in fetching or processing the data.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'force_generic_extractor': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        
        # Obtain more metadata
        metadata_yt_dlp = {
            'title': info_dict.get('title'),
            'description': info_dict.get('description'),
            'published_at': info_dict.get('upload_date'),
            'channel_title': info_dict.get('uploader'),
            'view_count': info_dict.get('view_count'),
            'like_count': info_dict.get('like_count'),
            'dislike_count': info_dict.get('dislike_count'),
            'comment_count': info_dict.get('comment_count'),
        }
        upload_date = info_dict.get('upload_date')
        if upload_date:
            # Convert date string to datetime object
            upload_datetime = datetime.strptime(upload_date, '%Y%m%d')
            # Format datetime object to ISO 8601 string
            metadata_yt_dlp['published_at'] = upload_datetime.isoformat()
        else:
            metadata_yt_dlp['published_at'] = None
            
        return metadata_yt_dlp

def extract_video_id(video_url: str) -> str:
    """
    Extract the video ID from a YouTube video URL.
    
    Args:
        video_url (str): The URL of the YouTube video.
    
    Returns:
        str: The extracted video ID.
    """
    video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', video_url)
    if video_id_match:
        return video_id_match.group(1)
    else:
        logger.error(f"Failed to extract video ID from URL: {video_url}")
        return None
    
def main():
    """
    Entry point for the script. 

    If a YouTube video URL is provided via the --url parameter, extracts the video ID from the URL, 
    and retrieves and logs the video metadata using both the YouTube Data API and yt-dlp. 

    Usage:
    --url <YouTube video URL>: Specify the YouTube video URL to fetch metadata for.

    If no URL is provided, an error message is displayed and the program exits.

    Returns:
    None
    """
    parser = CustomArgumentParser(
        description='Get metadata from YouTube videos.',
        usage='%(prog)s --url "<youtube-url>"'
    )
    parser.add_argument('--url', type=str, help="A specific YouTube video URL enclosed in double quotes.")
    args = parser.parse_args()
    
    if not args.url:
        parser.error("No URL provided. Please provide a YouTube video URL using the --url parameter.")

    video_links = [args.url]  # Process only this URL if provided

    for link in video_links:
        video_id = extract_video_id(link)
        print(f"Video ID: {video_id}")
        if not video_id:
            print(f"Error: Could not extract video ID from URL: {link}")
            continue  # Skip current loop, process the next link

        metadata_api = get_metadata_from_api(video_id)
        if not metadata_api:
            print(f"Error: Could not get metadata from YouTube Data API for video ID: {video_id}")
            continue

        metadata_yt_dlp = get_metadata_from_yt_dlp(video_id)
        if not metadata_yt_dlp:
            print(f"Error: Could not get metadata from yt-dlp for video ID: {video_id}")
            continue

        # Format output
        logger.info(f"\nMetadata for Video ID: {video_id}")
        logger.info(f"From YouTube Data API:\n{json.dumps(metadata_api, indent=4, ensure_ascii=False)}")
        logger.info(f"From yt-dlp:\n{json.dumps(metadata_yt_dlp, indent=4, ensure_ascii=False)}")

if __name__ == "__main__":
    main()