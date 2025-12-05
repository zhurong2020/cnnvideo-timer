"""
Subtitle generation and processing using Whisper.

Supports:
- Audio extraction from video
- Speech recognition using faster-whisper
- SRT/VTT subtitle generation
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass
from datetime import timedelta

logger = logging.getLogger(__name__)


@dataclass
class SubtitleSegment:
    """A single subtitle segment."""
    start: float  # seconds
    end: float    # seconds
    text: str


class SubtitleGenerator:
    """Generate subtitles from video using Whisper."""

    def __init__(
        self,
        model_size: str = "base",
        language: str = "en",
        device: str = "cpu",
    ):
        """Initialize subtitle generator.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Audio language code
            device: Device to use (cpu, cuda, auto)
        """
        self.model_size = model_size
        self.language = language
        self.device = device
        self._model = None

    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is not None:
            return

        try:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8",  # Use int8 for lower memory usage
            )
            logger.info("Whisper model loaded successfully")
        except ImportError:
            raise ImportError(
                "faster-whisper not installed. "
                "Install with: pip install faster-whisper"
            )

    def extract_audio(self, video_path: Path, audio_path: Optional[Path] = None) -> Path:
        """Extract audio from video using ffmpeg.

        Args:
            video_path: Path to video file
            audio_path: Output audio path (auto-generated if None)

        Returns:
            Path to extracted audio file
        """
        if audio_path is None:
            audio_path = video_path.parent / f"{video_path.stem}_audio.wav"

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # PCM 16-bit
            "-ar", "16000",  # 16kHz sample rate
            "-ac", "1",  # Mono
            "-y",  # Overwrite
            str(audio_path),
        ]

        try:
            logger.info(f"Extracting audio from {video_path.name}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Audio extraction completed")
            return audio_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio extraction failed: {e.stderr}")
            raise RuntimeError(f"Failed to extract audio: {e.stderr}")

    def transcribe(
        self,
        audio_path: Path,
        progress_callback=None,
    ) -> List[SubtitleSegment]:
        """Transcribe audio to text segments.

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback(current, total) for progress

        Returns:
            List of subtitle segments
        """
        self._load_model()

        logger.info(f"Transcribing {audio_path.name}")

        segments = []
        transcribe_options = {
            "language": self.language,
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
        }

        try:
            result, info = self._model.transcribe(
                str(audio_path),
                **transcribe_options,
            )

            logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")

            for i, segment in enumerate(result):
                segments.append(SubtitleSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                ))

                if progress_callback and i % 10 == 0:
                    progress_callback(i, -1)  # -1 means unknown total

            logger.info(f"Transcription completed: {len(segments)} segments")
            return segments

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def generate_srt(self, segments: List[SubtitleSegment]) -> str:
        """Generate SRT format subtitle content.

        Args:
            segments: List of subtitle segments

        Returns:
            SRT formatted string
        """
        srt_content = []

        for i, segment in enumerate(segments, 1):
            # Format: HH:MM:SS,mmm
            start_time = self._format_timestamp(segment.start)
            end_time = self._format_timestamp(segment.end)

            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment.text)
            srt_content.append("")  # Empty line

        return "\n".join(srt_content)

    def generate_vtt(self, segments: List[SubtitleSegment]) -> str:
        """Generate WebVTT format subtitle content.

        Args:
            segments: List of subtitle segments

        Returns:
            VTT formatted string
        """
        vtt_content = ["WEBVTT", ""]

        for segment in segments:
            # Format: HH:MM:SS.mmm
            start_time = self._format_timestamp(segment.start, use_comma=False)
            end_time = self._format_timestamp(segment.end, use_comma=False)

            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment.text)
            vtt_content.append("")  # Empty line

        return "\n".join(vtt_content)

    def _format_timestamp(self, seconds: float, use_comma: bool = True) -> str:
        """Format timestamp for subtitle files.

        Args:
            seconds: Time in seconds
            use_comma: Use comma for milliseconds (SRT) vs dot (VTT)

        Returns:
            Formatted timestamp string
        """
        td = timedelta(seconds=seconds)
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        millis = td.microseconds // 1000

        separator = "," if use_comma else "."
        return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"

    def generate_from_video(
        self,
        video_path: Path,
        output_path: Optional[Path] = None,
        subtitle_format: str = "srt",
        cleanup_audio: bool = True,
        progress_callback=None,
    ) -> Path:
        """Complete pipeline: video -> audio -> transcription -> subtitle file.

        Args:
            video_path: Path to video file
            output_path: Output subtitle path (auto-generated if None)
            subtitle_format: "srt" or "vtt"
            cleanup_audio: Delete temporary audio file after processing
            progress_callback: Optional progress callback

        Returns:
            Path to generated subtitle file
        """
        # Generate output path
        if output_path is None:
            ext = "srt" if subtitle_format == "srt" else "vtt"
            output_path = video_path.parent / f"{video_path.stem}.{ext}"

        # Extract audio
        audio_path = self.extract_audio(video_path)

        try:
            # Transcribe
            segments = self.transcribe(audio_path, progress_callback)

            # Generate subtitle content
            if subtitle_format == "srt":
                content = self.generate_srt(segments)
            elif subtitle_format == "vtt":
                content = self.generate_vtt(segments)
            else:
                raise ValueError(f"Unsupported subtitle format: {subtitle_format}")

            # Write to file
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Subtitle saved to {output_path}")

            return output_path

        finally:
            # Cleanup temporary audio file
            if cleanup_audio and audio_path.exists():
                audio_path.unlink()
                logger.info(f"Cleaned up temporary audio file: {audio_path}")


class SubtitleDownloader:
    """Download existing subtitles from video platforms."""

    @staticmethod
    def download_youtube_subtitles(
        video_url: str,
        output_path: Path,
        language: str = "en",
    ) -> Optional[Path]:
        """Download subtitles from YouTube if available.

        Args:
            video_url: YouTube video URL
            output_path: Output subtitle file path
            language: Subtitle language code

        Returns:
            Path to downloaded subtitle or None if not available
        """
        import yt_dlp

        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language],
            'subtitlesformat': 'srt/vtt/best',
            'outtmpl': str(output_path.parent / output_path.stem),
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                # Check if subtitles are available
                has_subs = (
                    info.get('subtitles') and language in info['subtitles']
                ) or (
                    info.get('automatic_captions') and language in info['automatic_captions']
                )

                if not has_subs:
                    logger.info(f"No subtitles available for language: {language}")
                    return None

                # Download
                ydl.download([video_url])

                # Find the downloaded subtitle file
                for ext in ['srt', 'vtt']:
                    subtitle_path = output_path.parent / f"{output_path.stem}.{language}.{ext}"
                    if subtitle_path.exists():
                        # Rename to desired output path
                        final_path = output_path.parent / f"{output_path.stem}.{ext}"
                        subtitle_path.rename(final_path)
                        logger.info(f"Downloaded subtitle to {final_path}")
                        return final_path

                return None

        except Exception as e:
            logger.error(f"Failed to download subtitles: {e}")
            return None


def get_or_generate_subtitle(
    video_path: Path,
    video_url: Optional[str] = None,
    language: str = "en",
    model_size: str = "base",
    prefer_download: bool = True,
) -> Optional[Path]:
    """Get subtitle: try downloading first, then generate with Whisper.

    Args:
        video_path: Path to video file
        video_url: Optional video URL for downloading subtitles
        language: Subtitle language
        model_size: Whisper model size for generation
        prefer_download: Try downloading before generating

    Returns:
        Path to subtitle file or None
    """
    subtitle_path = video_path.parent / f"{video_path.stem}.srt"

    # Try downloading if URL provided
    if prefer_download and video_url:
        logger.info("Attempting to download existing subtitles...")
        downloaded = SubtitleDownloader.download_youtube_subtitles(
            video_url, subtitle_path, language
        )
        if downloaded:
            return downloaded

    # Generate with Whisper
    logger.info("Generating subtitles with Whisper...")
    try:
        generator = SubtitleGenerator(model_size=model_size, language=language)
        return generator.generate_from_video(video_path)
    except ImportError:
        logger.warning(
            "faster-whisper not installed. Install with: pip install faster-whisper"
        )
        return None
    except Exception as e:
        logger.error(f"Subtitle generation failed: {e}")
        return None
