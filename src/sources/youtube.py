"""
YouTube video source adapters.

Provides adapters for YouTube channels including CNN10, BBC Learning English, VOA, etc.
"""

import logging
import re

import requests
import yt_dlp

from .base import SourceInfo, UserTier, VideoPreview, VideoSource

logger = logging.getLogger(__name__)


class YouTubeSource(VideoSource):
    """Generic YouTube channel source."""

    def __init__(
        self,
        channel_url: str,
        source_id: str,
        name: str,
        description: str = "",
        min_tier: UserTier = UserTier.FREE,
    ):
        self._channel_url = channel_url
        self._source_id = source_id
        self._name = name
        self._description = description
        self._min_tier = min_tier
        self._base_url = "https://www.youtube.com"
        self._video_pattern = re.compile(r"/watch\?v=([a-zA-Z0-9_-]+)")

    @property
    def info(self) -> SourceInfo:
        return SourceInfo(
            id=self._source_id,
            name=self._name,
            description=self._description,
            url=self._channel_url,
            icon="youtube",
            min_tier=self._min_tier,
            tags=["youtube", "news", "english"],
        )

    async def get_latest_videos(self, limit: int = 10) -> list[VideoPreview]:
        """Get latest videos from the YouTube channel."""
        videos = []

        try:
            # Method 1: Try scraping the channel page
            response = requests.get(
                self._channel_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
            )
            response.raise_for_status()

            # Extract video IDs
            video_ids = self._video_pattern.findall(response.text)
            unique_ids = list(dict.fromkeys(video_ids))[:limit]

            # Get video info for each
            for video_id in unique_ids:
                url = f"{self._base_url}/watch?v={video_id}"
                preview = await self._get_video_preview(video_id, url)
                if preview:
                    videos.append(preview)

        except Exception as e:
            logger.error(f"Failed to get videos from {self._channel_url}: {e}")

            # Method 2: Fallback to yt-dlp
            try:
                videos = await self._get_videos_via_ytdlp(limit)
            except Exception as e2:
                logger.error(f"yt-dlp fallback also failed: {e2}")

        return videos

    async def _get_videos_via_ytdlp(self, limit: int) -> list[VideoPreview]:
        """Get videos using yt-dlp (fallback method)."""
        videos = []
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "playlistend": limit,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Try /videos tab
                url = self._channel_url
                if not url.endswith("/videos"):
                    url = url.rstrip("/") + "/videos"

                result = ydl.extract_info(url, download=False)

                if result and "entries" in result:
                    for entry in result["entries"][:limit]:
                        if entry:
                            videos.append(
                                VideoPreview(
                                    id=entry.get("id", ""),
                                    title=entry.get("title", ""),
                                    url=entry.get(
                                        "url", f"{self._base_url}/watch?v={entry.get('id', '')}"
                                    ),
                                    thumbnail=entry.get("thumbnail"),
                                    duration=entry.get("duration", 0),
                                    source_id=self._source_id,
                                )
                            )
        except Exception as e:
            logger.error(f"yt-dlp extraction failed: {e}")

        return videos

    async def _get_video_preview(self, video_id: str, url: str) -> VideoPreview | None:
        """Get preview info for a single video."""
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return VideoPreview(
                    id=video_id,
                    title=info.get("title", ""),
                    url=url,
                    thumbnail=info.get("thumbnail"),
                    duration=info.get("duration", 0),
                    upload_date=info.get("upload_date"),
                    source_id=self._source_id,
                )
        except Exception as e:
            logger.warning(f"Failed to get preview for {video_id}: {e}")
            # Return basic info even if yt-dlp fails
            return VideoPreview(
                id=video_id,
                title="",
                url=url,
                source_id=self._source_id,
            )

    async def get_video_url(self, video_id: str) -> str | None:
        """Get the full URL for a video."""
        return f"{self._base_url}/watch?v={video_id}"


# Pre-configured sources for common channels


class CNN10Source(YouTubeSource):
    """CNN10 news source - 10 minute daily news for students."""

    def __init__(self):
        super().__init__(
            channel_url="https://www.youtube.com/@CNN10/videos",
            source_id="cnn10",
            name="CNN 10",
            description="10-minute daily news program for students, perfect for English learners",
            min_tier=UserTier.FREE,
        )


class BBCLearningEnglishSource(YouTubeSource):
    """BBC Learning English source."""

    def __init__(self):
        super().__init__(
            channel_url="https://www.youtube.com/@bbclearningenglish/videos",
            source_id="bbc_learning",
            name="BBC Learning English",
            description="English learning videos from BBC, various topics and levels",
            min_tier=UserTier.FREE,
        )


class VOASource(YouTubeSource):
    """Voice of America Learning English source."""

    def __init__(self):
        super().__init__(
            channel_url="https://www.youtube.com/@voaborenglish/videos",
            source_id="voa",
            name="VOA Learning English",
            description="Voice of America slow-paced English news for learners",
            min_tier=UserTier.FREE,
        )


# Registry of all available sources
YOUTUBE_SOURCES = {
    "cnn10": CNN10Source,
    "bbc_learning": BBCLearningEnglishSource,
    "voa": VOASource,
}


def get_source(source_id: str) -> VideoSource | None:
    """Get a video source by ID."""
    source_class = YOUTUBE_SOURCES.get(source_id)
    if source_class:
        return source_class()
    return None


def get_all_sources() -> list[VideoSource]:
    """Get all available video sources."""
    return [cls() for cls in YOUTUBE_SOURCES.values()]
