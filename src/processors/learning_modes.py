"""
Learning mode processors for English learning videos.

Implements different video processing modes:
- Original: Keep video as-is
- With Subtitle: Add subtitle track
- Repeat Twice: Play video twice, second time with subtitle
- Slow Mode: Slow playback with subtitle
"""

import logging
from pathlib import Path
from typing import Optional
from enum import Enum

from .ffmpeg import FFmpegProcessor
from .subtitle import get_or_generate_subtitle

logger = logging.getLogger(__name__)


class LearningMode(str, Enum):
    """Learning mode enum."""
    ORIGINAL = "original"
    WITH_SUBTITLE = "with_subtitle"
    REPEAT_TWICE = "repeat_twice"
    SLOW = "slow"


class LearningModeProcessor:
    """Process videos for different learning modes."""

    def __init__(self):
        """Initialize learning mode processor."""
        self.ffmpeg = FFmpegProcessor()

    def process(
        self,
        video_path: Path,
        output_path: Path,
        mode: LearningMode,
        video_url: Optional[str] = None,
        whisper_model: str = "base",
        subtitle_path: Optional[Path] = None,
        progress_callback=None,
    ) -> Path:
        """Process video according to learning mode.

        Args:
            video_path: Input video path
            output_path: Output video path
            mode: Learning mode to apply
            video_url: Optional video URL (for downloading subtitles)
            whisper_model: Whisper model size for subtitle generation
            subtitle_path: Optional pre-existing subtitle file
            progress_callback: Optional progress callback

        Returns:
            Path to processed video
        """
        logger.info(f"Processing video with mode: {mode}")

        if mode == LearningMode.ORIGINAL:
            return self._process_original(video_path, output_path)

        elif mode == LearningMode.WITH_SUBTITLE:
            return self._process_with_subtitle(
                video_path, output_path, video_url,
                whisper_model, subtitle_path, progress_callback
            )

        elif mode == LearningMode.REPEAT_TWICE:
            return self._process_repeat_twice(
                video_path, output_path, video_url,
                whisper_model, subtitle_path, progress_callback
            )

        elif mode == LearningMode.SLOW:
            return self._process_slow(
                video_path, output_path, video_url,
                whisper_model, subtitle_path, progress_callback
            )

        else:
            raise ValueError(f"Unknown learning mode: {mode}")

    def _process_original(
        self,
        video_path: Path,
        output_path: Path,
    ) -> Path:
        """Mode 1: Original video, no changes.

        Args:
            video_path: Input video
            output_path: Output video

        Returns:
            Path to output video (copy of input)
        """
        logger.info("Processing: Original mode (no changes)")

        # Simple copy or convert to standard format
        if video_path.suffix == output_path.suffix:
            # Just copy
            import shutil
            shutil.copy2(video_path, output_path)
        else:
            # Convert format
            self.ffmpeg.convert_format(video_path, output_path)

        return output_path

    def _process_with_subtitle(
        self,
        video_path: Path,
        output_path: Path,
        video_url: Optional[str],
        whisper_model: str,
        subtitle_path: Optional[Path],
        progress_callback,
    ) -> Path:
        """Mode 2: Original video + subtitle (hard-coded).

        Args:
            video_path: Input video
            output_path: Output video
            video_url: Video URL for subtitle download
            whisper_model: Whisper model size
            subtitle_path: Pre-existing subtitle file
            progress_callback: Progress callback

        Returns:
            Path to video with embedded subtitle
        """
        logger.info("Processing: With subtitle mode")

        # Get or generate subtitle
        if subtitle_path and subtitle_path.exists():
            srt_path = subtitle_path
        else:
            srt_path = get_or_generate_subtitle(
                video_path,
                video_url=video_url,
                model_size=whisper_model,
            )

        if not srt_path:
            logger.warning("No subtitle available, using original video")
            return self._process_original(video_path, output_path)

        # Embed hard subtitle
        return self.ffmpeg.embed_subtitle_hard(
            video_path,
            srt_path,
            output_path,
            subtitle_style={
                'FontSize': 20,
                'PrimaryColour': '&H00FFFFFF',
                'OutlineColour': '&H00000000',
                'Alignment': 2,
                'MarginV': 30,
            }
        )

    def _process_repeat_twice(
        self,
        video_path: Path,
        output_path: Path,
        video_url: Optional[str],
        whisper_model: str,
        subtitle_path: Optional[Path],
        progress_callback,
    ) -> Path:
        """Mode 3: Play video twice - first without subtitle, second with subtitle.

        This is great for learning: watch once to test comprehension,
        then watch again with subtitles to verify understanding.

        Args:
            video_path: Input video
            output_path: Output video
            video_url: Video URL
            whisper_model: Whisper model size
            subtitle_path: Pre-existing subtitle file
            progress_callback: Progress callback

        Returns:
            Path to concatenated video
        """
        logger.info("Processing: Repeat twice mode (1st no sub, 2nd with sub)")

        # Get or generate subtitle
        if subtitle_path and subtitle_path.exists():
            srt_path = subtitle_path
        else:
            srt_path = get_or_generate_subtitle(
                video_path,
                video_url=video_url,
                model_size=whisper_model,
            )

        if not srt_path:
            logger.warning("No subtitle available, using double original video")
            # Just repeat original twice
            temp_dir = output_path.parent / "temp"
            temp_dir.mkdir(exist_ok=True)
            return self.ffmpeg.concatenate_videos(
                [video_path, video_path],
                output_path
            )

        # Create temp directory
        temp_dir = output_path.parent / "temp"
        temp_dir.mkdir(exist_ok=True)

        try:
            # First video: Original (no subtitle)
            video1 = temp_dir / f"{video_path.stem}_part1.mp4"
            self._process_original(video_path, video1)

            # Second video: With subtitle
            video2 = temp_dir / f"{video_path.stem}_part2.mp4"
            self.ffmpeg.embed_subtitle_hard(
                video_path,
                srt_path,
                video2,
                subtitle_style={
                    'FontSize': 20,
                    'PrimaryColour': '&H0000FFFF',  # Yellow for second part
                    'OutlineColour': '&H00000000',
                    'Alignment': 2,
                    'MarginV': 30,
                }
            )

            # Concatenate
            result = self.ffmpeg.concatenate_videos(
                [video1, video2],
                output_path
            )

            return result

        finally:
            # Cleanup temp files
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _process_slow(
        self,
        video_path: Path,
        output_path: Path,
        video_url: Optional[str],
        whisper_model: str,
        subtitle_path: Optional[Path],
        progress_callback,
    ) -> Path:
        """Mode 4: Slow playback (0.75x speed) with subtitle.

        Good for beginners - slower speaking pace makes it easier to follow.

        Args:
            video_path: Input video
            output_path: Output video
            video_url: Video URL
            whisper_model: Whisper model size
            subtitle_path: Pre-existing subtitle file
            progress_callback: Progress callback

        Returns:
            Path to slowed video with subtitle
        """
        logger.info("Processing: Slow mode (0.75x speed + subtitle)")

        # Get or generate subtitle
        if subtitle_path and subtitle_path.exists():
            srt_path = subtitle_path
        else:
            srt_path = get_or_generate_subtitle(
                video_path,
                video_url=video_url,
                model_size=whisper_model,
            )

        temp_dir = output_path.parent / "temp"
        temp_dir.mkdir(exist_ok=True)

        try:
            # First, slow down the video
            slow_video = temp_dir / f"{video_path.stem}_slow.mp4"
            self.ffmpeg.adjust_speed(
                video_path,
                slow_video,
                speed_factor=0.75
            )

            # Then add subtitle
            if srt_path:
                return self.ffmpeg.embed_subtitle_hard(
                    slow_video,
                    srt_path,
                    output_path,
                    subtitle_style={
                        'FontSize': 22,
                        'PrimaryColour': '&H00FFFFFF',
                        'OutlineColour': '&H00000000',
                        'Alignment': 2,
                        'MarginV': 30,
                    }
                )
            else:
                # No subtitle, just return slow video
                logger.warning("No subtitle available, using slow video without subtitle")
                import shutil
                shutil.move(str(slow_video), str(output_path))
                return output_path

        finally:
            # Cleanup
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)


def process_video_for_learning(
    video_path: Path,
    output_path: Path,
    mode: str = "with_subtitle",
    video_url: Optional[str] = None,
    whisper_model: str = "base",
) -> Path:
    """Convenience function to process video for learning.

    Args:
        video_path: Input video file
        output_path: Output video file
        mode: Learning mode ("original", "with_subtitle", "repeat_twice", "slow")
        video_url: Optional video URL for subtitle download
        whisper_model: Whisper model size (tiny, base, small, medium, large)

    Returns:
        Path to processed video

    Example:
        >>> process_video_for_learning(
        ...     Path("cnn10.mp4"),
        ...     Path("cnn10_learning.mp4"),
        ...     mode="repeat_twice",
        ...     video_url="https://youtube.com/watch?v=abc123"
        ... )
    """
    processor = LearningModeProcessor()
    learning_mode = LearningMode(mode)

    return processor.process(
        video_path=video_path,
        output_path=output_path,
        mode=learning_mode,
        video_url=video_url,
        whisper_model=whisper_model,
    )
