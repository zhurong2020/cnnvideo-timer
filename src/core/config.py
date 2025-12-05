"""
Configuration management using Pydantic Settings.

Provides type-safe configuration with validation and environment variable support.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file="config/config.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App settings
    app_name: str = "SmartNews Learn"
    app_version: str = "2.0.0"
    debug: bool = False

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: Optional[str] = None  # For WordPress authentication
    cors_origins: list[str] = []  # Comma-separated in .env: CORS_ORIGINS=https://example.com,https://www.example.com

    # Paths
    data_dir: Path = Path("./data")
    temp_dir: Path = Path("./data/temp")
    log_dir: Path = Path("./log")

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/tasks.db"

    # YouTube settings
    youtube_url: str = "https://www.youtube.com/@CNN10/videos"
    youtube_base_url: str = "https://www.youtube.com"
    youtube_video_pattern: str = r"/watch\?v=([a-zA-Z0-9_-]+)"

    # Download settings
    download_path: Path = Path("./data/temp")
    max_videos_to_download: int = 1
    max_download_retries: int = 3
    request_timeout: int = 30
    max_resolution: int = 720
    video_extension: str = ".mp4"

    # Whisper settings (for subtitle generation)
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_language: str = "en"

    # FFmpeg settings
    ffmpeg_path: Optional[str] = None  # Auto-detect if None

    # Task settings
    max_concurrent_tasks: int = 2
    task_retention_hours: int = 24  # Keep completed tasks for 24 hours

    # Storage settings
    storage_quota_gb: float = 10.0  # Storage quota in GB
    cache_hours: int = 24  # How long to keep cached videos
    default_video_format: str = "720p"  # Default video format

    # OneDrive (rclone) settings
    rclone_remote: Optional[str] = None  # e.g., "onedrive:videos"
    enable_onedrive: bool = False
    onedrive_quota_gb: float = 10.0  # Limit OneDrive usage

    # SMTP settings (for notifications)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_sender: Optional[str] = None
    smtp_receiver: Optional[str] = None

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def validate_production_config(self) -> list[str]:
        """
        Validate configuration for production deployment.

        Returns:
            List of warning messages. Empty list means all checks passed.
        """
        warnings = []

        # Check if debug mode is enabled in production
        if self.debug:
            warnings.append("⚠️  DEBUG mode is enabled. Disable in production for security.")

        # Check if API key is set
        if not self.api_key or self.api_key == "your-secret-api-key-here":
            warnings.append("⚠️  API_KEY not set or using default placeholder. Set a strong API key.")

        # Check CORS configuration
        if not self.cors_origins and not self.debug:
            warnings.append(
                "⚠️  CORS_ORIGINS not configured. Configure allowed origins for production "
                "(e.g., CORS_ORIGINS=https://yourdomain.com)"
            )

        # Check Whisper model selection for resource constraints
        large_models = ["medium", "large"]
        if self.whisper_model in large_models:
            warnings.append(
                f"ℹ️  Using Whisper model '{self.whisper_model}' requires significant RAM. "
                "Consider 'tiny' or 'base' for low-resource servers."
            )

        # Check concurrent tasks
        if self.max_concurrent_tasks > 4:
            warnings.append(
                f"⚠️  MAX_CONCURRENT_TASKS={self.max_concurrent_tasks} may be too high. "
                "Consider reducing to 1-2 for low-resource servers."
            )

        # Check FFmpeg availability
        if self.ffmpeg_path and not Path(self.ffmpeg_path).exists():
            warnings.append(f"❌ FFmpeg path '{self.ffmpeg_path}' does not exist.")

        return warnings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
