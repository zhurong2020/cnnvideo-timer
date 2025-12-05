"""Video processors module."""

from .subtitle import SubtitleGenerator, SubtitleDownloader, get_or_generate_subtitle
from .ffmpeg import FFmpegProcessor, check_ffmpeg_installed
from .learning_modes import LearningMode, LearningModeProcessor, process_video_for_learning

__all__ = [
    "SubtitleGenerator",
    "SubtitleDownloader",
    "get_or_generate_subtitle",
    "FFmpegProcessor",
    "check_ffmpeg_installed",
    "LearningMode",
    "LearningModeProcessor",
    "process_video_for_learning",
]
