# metadata_manager.py v1.3.3

# Description: Manages the storage, retrieval, and querying of video metadata.

import json
import os
import logging
from typing import Optional, Dict, Union
from config_loader import load_config
from youtube_metadata_checker import get_metadata_from_api, get_metadata_from_yt_dlp

logger = logging.getLogger('metadata_manager')
config = load_config()

class MetadataManager:
    def __init__(self, config):
        """Initialize the MetadataManager with a configuration dictionary.

        Args:
        - config (Dict): The configuration dictionary containing settings and parameters.

        Returns:
        - None
        """
        self.metadata_file_path = config['METADATA_FILE']
        self.default_metadata_extractor = config.get('DEFAULT_METADATA_EXTRACTOR', 'yt_dlp')  

    def save_or_update_metadata(self, metadata):
        """Save or update the metadata of a video.

        Args:
        - metadata (Dict): The metadata dictionary to be saved or updated.

        Returns:
        - None
        """
        video_id = metadata.get('id')
        if video_id:
            all_metadata = self.get_all_metadata()
            all_metadata[video_id] = metadata
            # Get the directory of the metadata file
            metadata_dir = os.path.dirname(self.metadata_file_path)
            
            # Check if the directory exists, if not create it
            if not os.path.exists(metadata_dir):
                os.makedirs(metadata_dir)
            with open(self.metadata_file_path, 'w', encoding='utf-8') as file:
                json.dump(all_metadata, file, ensure_ascii=False, indent=4)

    def get_all_metadata(self):
        """Retrieve all stored metadata.

        Returns:
        - Dict: A dictionary containing all stored metadata.
        """
        if os.path.exists(self.metadata_file_path):
            with open(self.metadata_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def query_metadata(self, video_id):
        """Query metadata of a specific video using its video ID.

        Args:
        - video_id (str): The video ID used to query its metadata.

        Returns:
        - Optional[Dict]: The metadata of the specified video, or None if not found.
        """
        all_metadata = self.get_all_metadata()
        return all_metadata.get(video_id)

    def extract_and_save_additional_metadata(self, video_id):
        """Extract additional metadata using external functions and save or update it.

        Args:
        - video_id (str): The video ID used to extract and save or update its metadata.

        Returns:
        - None
        """
        if self.default_metadata_extractor == 'api':
            additional_metadata = get_metadata_from_api(video_id)
        else:
            additional_metadata = get_metadata_from_yt_dlp(video_id)
        
        if additional_metadata:
            existing_metadata = self.query_metadata(video_id) or {}
            updated_metadata = {**existing_metadata, **additional_metadata}
            self.save_or_update_metadata(updated_metadata)
    
    def get_metadata_file_path(self, video_id):
        """Generate the file path for a metadata file.

        Args:
        - video_id (str): The video ID used to generate the file path.

        Returns:
        - str: The generated file path for the metadata file.
        """
        return os.path.join(self.metadata_file_path, f"{video_id}.json")