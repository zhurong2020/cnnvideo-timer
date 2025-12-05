"""
FFmpeg video processing utilities.

Provides functions for:
- Subtitle embedding (hard/soft subtitles)
- Video concatenation
- Speed adjustment
- Format conversion
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Video file information."""
    path: Path
    duration: float  # seconds
    width: int
    height: int
    codec: str
    fps: float
    bitrate: int


class FFmpegProcessor:
    """FFmpeg video processing wrapper."""

    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        """Initialize FFmpeg processor.

        Args:
            ffmpeg_path: Path to ffmpeg executable
            ffprobe_path: Path to ffprobe executable
        """
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        self._verify_ffmpeg()

    def _verify_ffmpeg(self):
        """Verify FFmpeg is available."""
        try:
            subprocess.run(
                [self.ffmpeg, "-version"],
                capture_output=True,
                check=True,
            )
            logger.info("FFmpeg found and verified")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg:\n"
                "  Windows: https://www.gyan.dev/ffmpeg/builds/\n"
                "  Linux: apt install ffmpeg\n"
                "  Mac: brew install ffmpeg"
            )

    def get_video_info(self, video_path: Path) -> VideoInfo:
        """Get video file information.

        Args:
            video_path: Path to video file

        Returns:
            VideoInfo object
        """
        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)

            # Find video stream
            video_stream = next(
                (s for s in data['streams'] if s['codec_type'] == 'video'),
                None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            # Parse FPS
            fps_parts = video_stream['r_frame_rate'].split('/')
            fps = int(fps_parts[0]) / int(fps_parts[1])

            return VideoInfo(
                path=video_path,
                duration=float(data['format']['duration']),
                width=video_stream['width'],
                height=video_stream['height'],
                codec=video_stream['codec_name'],
                fps=fps,
                bitrate=int(data['format'].get('bit_rate', 0)),
            )

        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise

    def embed_subtitle_hard(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Path,
        subtitle_style: Optional[dict] = None,
    ) -> Path:
        """Embed subtitle as hard subtitle (burned into video).

        Args:
            video_path: Input video path
            subtitle_path: Subtitle file path (SRT/VTT)
            output_path: Output video path
            subtitle_style: Optional subtitle styling dict

        Returns:
            Path to output video
        """
        # Default subtitle style
        default_style = {
            'FontName': 'Arial',
            'FontSize': 24,
            'PrimaryColour': '&H00FFFFFF',  # White
            'OutlineColour': '&H00000000',  # Black outline
            'BorderStyle': 1,
            'Outline': 2,
            'Shadow': 0,
            'Alignment': 2,  # Bottom center
            'MarginV': 30,
        }

        if subtitle_style:
            default_style.update(subtitle_style)

        # Build filter string
        filter_str = f"subtitles={subtitle_path}:force_style='"
        filter_str += ','.join(f"{k}={v}" for k, v in default_style.items())
        filter_str += "'"

        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
            "-vf", filter_str,
            "-c:a", "copy",  # Copy audio without re-encoding
            "-y",
            str(output_path),
        ]

        try:
            logger.info(f"Embedding hard subtitle into {video_path.name}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Hard subtitle embedded: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Hard subtitle embedding failed: {e.stderr}")
            raise RuntimeError(f"Failed to embed hard subtitle: {e.stderr}")

    def embed_subtitle_soft(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Path,
        language: str = "eng",
    ) -> Path:
        """Embed subtitle as soft subtitle (separate stream).

        Args:
            video_path: Input video path
            subtitle_path: Subtitle file path
            output_path: Output video path (must be .mkv or .mp4)
            language: Subtitle language code

        Returns:
            Path to output video
        """
        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
            "-i", str(subtitle_path),
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text" if output_path.suffix == ".mp4" else "srt",
            "-metadata:s:s:0", f"language={language}",
            "-y",
            str(output_path),
        ]

        try:
            logger.info(f"Embedding soft subtitle into {video_path.name}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Soft subtitle embedded: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Soft subtitle embedding failed: {e.stderr}")
            raise RuntimeError(f"Failed to embed soft subtitle: {e.stderr}")

    def concatenate_videos(
        self,
        video_paths: List[Path],
        output_path: Path,
        transition: Optional[str] = None,
    ) -> Path:
        """Concatenate multiple videos.

        Args:
            video_paths: List of video file paths
            output_path: Output video path
            transition: Optional transition effect (None, "fade", etc.)

        Returns:
            Path to concatenated video
        """
        if len(video_paths) < 2:
            raise ValueError("Need at least 2 videos to concatenate")

        # Create concat file
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w', encoding='utf-8') as f:
            for video in video_paths:
                # FFmpeg concat format
                f.write(f"file '{video.absolute()}'\n")

        try:
            cmd = [
                self.ffmpeg,
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                "-y",
                str(output_path),
            ]

            logger.info(f"Concatenating {len(video_paths)} videos")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Videos concatenated: {output_path}")

            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"Concatenation failed: {e.stderr}")
            raise RuntimeError(f"Failed to concatenate videos: {e.stderr}")

        finally:
            # Clean up concat file
            if concat_file.exists():
                concat_file.unlink()

    def adjust_speed(
        self,
        video_path: Path,
        output_path: Path,
        speed_factor: float = 0.75,
    ) -> Path:
        """Adjust video playback speed.

        Args:
            video_path: Input video path
            output_path: Output video path
            speed_factor: Speed multiplier (0.5=half speed, 2.0=double speed)

        Returns:
            Path to output video
        """
        if speed_factor <= 0:
            raise ValueError("Speed factor must be positive")

        # Calculate PTS and audio tempo
        video_filter = f"setpts={1/speed_factor}*PTS"
        audio_filter = f"atempo={speed_factor}"

        # atempo only supports 0.5-2.0, chain if needed
        if speed_factor > 2.0:
            count = 0
            temp_factor = speed_factor
            audio_filter = ""
            while temp_factor > 2.0:
                audio_filter += "atempo=2.0,"
                temp_factor /= 2.0
                count += 1
            audio_filter += f"atempo={temp_factor}"
        elif speed_factor < 0.5:
            count = 0
            temp_factor = speed_factor
            audio_filter = ""
            while temp_factor < 0.5:
                audio_filter += "atempo=0.5,"
                temp_factor /= 0.5
                count += 1
            audio_filter += f"atempo={temp_factor}"

        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
            "-filter:v", video_filter,
            "-filter:a", audio_filter,
            "-y",
            str(output_path),
        ]

        try:
            logger.info(f"Adjusting speed to {speed_factor}x for {video_path.name}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Speed adjusted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Speed adjustment failed: {e.stderr}")
            raise RuntimeError(f"Failed to adjust speed: {e.stderr}")

    def convert_format(
        self,
        video_path: Path,
        output_path: Path,
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        quality: Optional[int] = None,
    ) -> Path:
        """Convert video to different format.

        Args:
            video_path: Input video path
            output_path: Output video path
            video_codec: Video codec (None=copy, "libx264", "libx265", etc.)
            audio_codec: Audio codec (None=copy, "aac", "mp3", etc.)
            quality: CRF value for quality (18=high, 23=medium, 28=low)

        Returns:
            Path to output video
        """
        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
        ]

        # Video codec
        if video_codec:
            cmd.extend(["-c:v", video_codec])
            if quality:
                cmd.extend(["-crf", str(quality)])
        else:
            cmd.extend(["-c:v", "copy"])

        # Audio codec
        if audio_codec:
            cmd.extend(["-c:a", audio_codec])
        else:
            cmd.extend(["-c:a", "copy"])

        cmd.extend(["-y", str(output_path)])

        try:
            logger.info(f"Converting {video_path.name} to {output_path.suffix}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Conversion completed: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion failed: {e.stderr}")
            raise RuntimeError(f"Failed to convert video: {e.stderr}")

    def extract_segment(
        self,
        video_path: Path,
        output_path: Path,
        start_time: float,
        duration: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Path:
        """Extract a segment from video.

        Args:
            video_path: Input video path
            output_path: Output video path
            start_time: Start time in seconds
            duration: Duration in seconds (or use end_time)
            end_time: End time in seconds (or use duration)

        Returns:
            Path to output video
        """
        cmd = [
            self.ffmpeg,
            "-i", str(video_path),
            "-ss", str(start_time),
        ]

        if duration:
            cmd.extend(["-t", str(duration)])
        elif end_time:
            cmd.extend(["-to", str(end_time)])

        cmd.extend([
            "-c", "copy",
            "-y",
            str(output_path),
        ])

        try:
            logger.info(f"Extracting segment from {video_path.name}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Segment extracted: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Segment extraction failed: {e.stderr}")
            raise RuntimeError(f"Failed to extract segment: {e.stderr}")


# Utility functions

def check_ffmpeg_installed(ffmpeg_path: Optional[str] = None) -> bool:
    """Check if FFmpeg is installed and accessible.

    Args:
        ffmpeg_path: Custom path to ffmpeg executable. If None, uses "ffmpeg" from PATH.

    Returns:
        True if ffmpeg is available, False otherwise.
    """
    cmd = ffmpeg_path if ffmpeg_path else "ffmpeg"
    try:
        subprocess.run(
            [cmd, "-version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
