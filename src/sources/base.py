"""
Base class for video sources.

All video source adapters should inherit from VideoSource.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class UserTier(Enum):
    """User subscription tier."""

    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


@dataclass
class SourceInfo:
    """Video source information."""

    id: str
    name: str
    description: str
    url: str
    icon: Optional[str] = None
    min_tier: UserTier = UserTier.FREE
    tags: List[str] = field(default_factory=list)


@dataclass
class VideoPreview:
    """Video preview information (without downloading)."""

    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: int = 0  # seconds
    upload_date: Optional[str] = None
    source_id: str = ""


class VideoSource(ABC):
    """Abstract base class for video sources."""

    @property
    @abstractmethod
    def info(self) -> SourceInfo:
        """Return source information."""
        pass

    @abstractmethod
    async def get_latest_videos(self, limit: int = 10) -> List[VideoPreview]:
        """Get latest videos from the source.

        Args:
            limit: Maximum number of videos to return

        Returns:
            List of VideoPreview objects
        """
        pass

    @abstractmethod
    async def get_video_url(self, video_id: str) -> Optional[str]:
        """Get the full URL for a video.

        Args:
            video_id: Video identifier

        Returns:
            Full video URL or None if not found
        """
        pass

    async def search_videos(self, query: str, limit: int = 10) -> List[VideoPreview]:
        """Search for videos (optional, not all sources support this).

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of VideoPreview objects
        """
        return []

    def is_available_for_tier(self, tier: UserTier) -> bool:
        """Check if this source is available for a user tier."""
        tier_order = [UserTier.FREE, UserTier.BASIC, UserTier.PREMIUM]
        return tier_order.index(tier) >= tier_order.index(self.info.min_tier)
