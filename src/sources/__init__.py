"""Video source adapters."""

from .base import VideoSource, SourceInfo
from .youtube import YouTubeSource, CNN10Source, BBCLearningEnglishSource, VOASource

__all__ = [
    "VideoSource",
    "SourceInfo",
    "YouTubeSource",
    "CNN10Source",
    "BBCLearningEnglishSource",
    "VOASource",
]
