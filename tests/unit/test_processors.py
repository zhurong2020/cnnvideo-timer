"""
Unit tests for processors module.

These tests use mocking to avoid requiring FFmpeg and Whisper.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestSubtitleSegment:
    """Tests for SubtitleSegment dataclass."""

    def test_subtitle_segment_creation(self):
        """Test creating a subtitle segment."""
        from src.processors.subtitle import SubtitleSegment

        segment = SubtitleSegment(start=0.0, end=5.0, text="Hello world")

        assert segment.start == 0.0
        assert segment.end == 5.0
        assert segment.text == "Hello world"

    def test_subtitle_segment_with_float_times(self):
        """Test segment with precise float times."""
        from src.processors.subtitle import SubtitleSegment

        segment = SubtitleSegment(start=1.234, end=5.678, text="Test")

        assert segment.start == 1.234
        assert segment.end == 5.678


class TestSubtitleGenerator:
    """Tests for SubtitleGenerator class."""

    def test_generator_initialization(self):
        """Test SubtitleGenerator initialization."""
        from src.processors.subtitle import SubtitleGenerator

        generator = SubtitleGenerator(
            model_size="tiny",
            language="en",
            device="cpu",
        )

        assert generator.model_size == "tiny"
        assert generator.language == "en"
        assert generator.device == "cpu"
        assert generator._model is None  # Lazy loading

    def test_generator_default_values(self):
        """Test SubtitleGenerator default values."""
        from src.processors.subtitle import SubtitleGenerator

        generator = SubtitleGenerator()

        assert generator.model_size == "base"
        assert generator.language == "en"
        assert generator.device == "cpu"

    @patch("src.processors.subtitle.subprocess.run")
    def test_extract_audio(self, mock_run, tmp_path):
        """Test audio extraction calls ffmpeg."""
        from src.processors.subtitle import SubtitleGenerator

        mock_run.return_value = Mock(returncode=0)
        generator = SubtitleGenerator()

        video_path = tmp_path / "test.mp4"
        video_path.touch()

        generator.extract_audio(video_path)

        # Should call subprocess.run with ffmpeg
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "ffmpeg" in call_args[0] or call_args[0] == "ffmpeg"


class TestVideoInfo:
    """Tests for VideoInfo dataclass."""

    def test_video_info_creation(self):
        """Test creating VideoInfo."""
        from src.processors.ffmpeg import VideoInfo

        info = VideoInfo(
            path=Path("/test/video.mp4"),
            duration=120.5,
            width=1920,
            height=1080,
            codec="h264",
            fps=30.0,
            bitrate=5000000,
        )

        assert info.duration == 120.5
        assert info.width == 1920
        assert info.height == 1080
        assert info.codec == "h264"
        assert info.fps == 30.0


class TestFFmpegProcessor:
    """Tests for FFmpegProcessor class."""

    @patch("src.processors.ffmpeg.subprocess.run")
    def test_processor_initialization(self, mock_run):
        """Test FFmpegProcessor initialization verifies ffmpeg."""
        from src.processors.ffmpeg import FFmpegProcessor

        mock_run.return_value = Mock(returncode=0)

        processor = FFmpegProcessor()

        # Should verify ffmpeg on init
        mock_run.assert_called()
        assert processor.ffmpeg == "ffmpeg"
        assert processor.ffprobe == "ffprobe"

    @patch("src.processors.ffmpeg.subprocess.run")
    def test_processor_custom_paths(self, mock_run):
        """Test FFmpegProcessor with custom paths."""
        from src.processors.ffmpeg import FFmpegProcessor

        mock_run.return_value = Mock(returncode=0)

        processor = FFmpegProcessor(
            ffmpeg_path="/custom/ffmpeg",
            ffprobe_path="/custom/ffprobe",
        )

        assert processor.ffmpeg == "/custom/ffmpeg"
        assert processor.ffprobe == "/custom/ffprobe"

    @patch("src.processors.ffmpeg.subprocess.run")
    def test_processor_ffmpeg_not_found(self, mock_run):
        """Test FFmpegProcessor raises error when ffmpeg not found."""
        from src.processors.ffmpeg import FFmpegProcessor

        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError, match="FFmpeg not found"):
            FFmpegProcessor()


class TestCheckFFmpegInstalled:
    """Tests for check_ffmpeg_installed function."""

    @patch("src.processors.ffmpeg.subprocess.run")
    def test_check_ffmpeg_installed_true(self, mock_run):
        """Test check_ffmpeg_installed returns True when found."""
        from src.processors.ffmpeg import check_ffmpeg_installed

        mock_run.return_value = Mock(returncode=0)

        result = check_ffmpeg_installed()

        assert result is True

    @patch("src.processors.ffmpeg.subprocess.run")
    def test_check_ffmpeg_installed_false(self, mock_run):
        """Test check_ffmpeg_installed returns False when not found."""
        from src.processors.ffmpeg import check_ffmpeg_installed

        mock_run.side_effect = FileNotFoundError()

        result = check_ffmpeg_installed()

        assert result is False


class TestLearningMode:
    """Tests for LearningMode enum."""

    def test_learning_mode_values(self):
        """Test LearningMode enum has expected values."""
        from src.processors.learning_modes import LearningMode

        # Check actual enum members from implementation
        assert hasattr(LearningMode, "ORIGINAL")
        assert hasattr(LearningMode, "WITH_SUBTITLE")
        assert hasattr(LearningMode, "REPEAT_TWICE")
        assert hasattr(LearningMode, "SLOW")

        # Check values
        assert LearningMode.ORIGINAL.value == "original"
        assert LearningMode.WITH_SUBTITLE.value == "with_subtitle"
        assert LearningMode.REPEAT_TWICE.value == "repeat_twice"
        assert LearningMode.SLOW.value == "slow"


class TestLearningModeProcessor:
    """Tests for LearningModeProcessor class."""

    @patch("src.processors.learning_modes.FFmpegProcessor")
    def test_processor_initialization(self, mock_ffmpeg, test_config):
        """Test LearningModeProcessor initialization."""
        from src.processors.learning_modes import LearningModeProcessor

        processor = LearningModeProcessor()

        # Should initialize without error
        assert processor is not None
        # Should have created FFmpegProcessor
        mock_ffmpeg.assert_called_once()

    @patch("src.processors.learning_modes.FFmpegProcessor")
    def test_processor_has_ffmpeg(self, mock_ffmpeg, test_config):
        """Test LearningModeProcessor has ffmpeg attribute."""
        from src.processors.learning_modes import LearningModeProcessor

        processor = LearningModeProcessor()

        assert hasattr(processor, "ffmpeg")
