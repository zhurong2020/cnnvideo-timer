"""Video source adapters."""

from .base import SourceInfo, VideoSource
from .youtube import BBCLearningEnglishSource, CNN10Source, VOASource, YouTubeSource

__all__ = [
    "VideoSource",
    "SourceInfo",
    "YouTubeSource",
    "CNN10Source",
    "BBCLearningEnglishSource",
    "VOASource",
]
