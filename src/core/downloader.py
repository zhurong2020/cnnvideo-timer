"""
Video downloader module.

Provides a unified interface for downloading videos from various sources.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import yt_dlp

from .config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Video information container."""

    id: str
    title: str
    url: str
    description: str = ""
    duration: int = 0  # seconds
    thumbnail: Optional[str] = None
    uploader: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: int = 0
    formats: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.formats is None:
            self.formats = []


@dataclass
class DownloadResult:
    """Download result container."""

    success: bool
    video_id: str
    title: str
    file_path: Optional[Path] = None
    error: Optional[str] = None
    file_size: int = 0


class VideoDownloader:
    """Video downloader using yt-dlp."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the downloader.

        Args:
            output_dir: Directory for downloaded videos. Defaults to settings.
        """
        settings = get_settings()
        self.output_dir = output_dir or settings.download_path
        self.max_resolution = settings.max_resolution
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_ydl_opts(self, format_id: Optional[str] = None) -> Dict[str, Any]:
        """Get yt-dlp options."""
        opts = {
            "format": format_id
            or f"best[height<={self.max_resolution}][ext=mp4]/best[height<={self.max_resolution}]",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_progress": True,
            "no_warnings": True,
            "extract_flat": False,
            # Download subtitles if available
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "srt/vtt/best",
        }
        return opts

    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """Get video information without downloading.

        Args:
            url: Video URL

        Returns:
            VideoInfo object or None if failed
        """
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

                return VideoInfo(
                    id=info.get("id", ""),
                    title=info.get("title", ""),
                    url=info.get("webpage_url", url),
                    description=info.get("description", ""),
                    duration=info.get("duration", 0),
                    thumbnail=info.get("thumbnail"),
                    uploader=info.get("uploader"),
                    upload_date=info.get("upload_date"),
                    view_count=info.get("view_count", 0),
                    formats=info.get("formats", []),
                )
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None

    def download(self, url: str, format_id: Optional[str] = None) -> DownloadResult:
        """Download a video.

        Args:
            url: Video URL
            format_id: Specific format ID to download

        Returns:
            DownloadResult with status and file path
        """
        # Get video info first
        info = self.get_video_info(url)
        if not info:
            return DownloadResult(
                success=False, video_id="", title="", error="Failed to get video info"
            )

        opts = self._get_ydl_opts(format_id)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            # Find the downloaded file
            expected_path = self.output_dir / f"{info.id}.mp4"
            if not expected_path.exists():
                # Try other extensions
                for ext in [".webm", ".mkv", ".mp4"]:
                    alt_path = self.output_dir / f"{info.id}{ext}"
                    if alt_path.exists():
                        expected_path = alt_path
                        break

            if expected_path.exists():
                return DownloadResult(
                    success=True,
                    video_id=info.id,
                    title=info.title,
                    file_path=expected_path,
                    file_size=expected_path.stat().st_size,
                )
            else:
                return DownloadResult(
                    success=False,
                    video_id=info.id,
                    title=info.title,
                    error="Downloaded file not found",
                )

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return DownloadResult(success=False, video_id=info.id, title=info.title, error=str(e))

    def get_suitable_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get list of suitable formats for a video.

        Args:
            url: Video URL

        Returns:
            List of format dictionaries sorted by file size
        """
        info = self.get_video_info(url)
        if not info:
            return []

        suitable = [
            f
            for f in info.formats
            if f.get("ext") == "mp4"
            and f.get("height")
            and f["height"] <= self.max_resolution
            and f.get("vcodec") != "none"  # Has video
        ]

        # Sort by filesize (smallest first)
        suitable.sort(key=lambda f: f.get("filesize") or float("inf"))

        return suitable
