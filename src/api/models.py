"""
Pydantic models for API request/response validation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# Enums
class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingModeEnum(str, Enum):
    ORIGINAL = "original"
    WITH_SUBTITLE = "with_subtitle"
    REPEAT_TWICE = "repeat_twice"
    SLOW = "slow"


class VideoFormatEnum(str, Enum):
    """Available video formats/resolutions."""

    LOW_360P = "360p"
    MEDIUM_480P = "480p"
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    AUDIO_ONLY = "audio_only"


class UserTierEnum(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


# Request Models
class TaskCreateRequest(BaseModel):
    """Request to create a new download task."""

    source_id: str = Field(..., description="Video source ID (e.g., 'cnn10', 'bbc_learning')")
    video_url: str = Field(..., description="Video URL to download")
    processing_mode: ProcessingModeEnum = Field(
        default=ProcessingModeEnum.WITH_SUBTITLE, description="Video processing mode"
    )
    video_format: VideoFormatEnum = Field(
        default=VideoFormatEnum.HD_720P,
        description="Video format/resolution (360p, 480p, 720p, 1080p, audio_only)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "source_id": "cnn10",
                    "video_url": "https://www.youtube.com/watch?v=abc123",
                    "processing_mode": "with_subtitle",
                    "video_format": "720p",
                }
            ]
        }
    }


class VideoPreviewRequest(BaseModel):
    """Request to preview video info."""

    url: str = Field(..., description="Video URL to preview")


# Response Models
class SourceResponse(BaseModel):
    """Video source information."""

    id: str
    name: str
    description: str
    url: str
    icon: str | None = None
    min_tier: UserTierEnum
    tags: list[str] = []


class VideoPreviewResponse(BaseModel):
    """Video preview information."""

    id: str
    title: str
    url: str
    thumbnail: str | None = None
    duration: int = 0
    upload_date: str | None = None
    source_id: str = ""


class TaskResponse(BaseModel):
    """Task information response."""

    id: str
    user_id: str
    source_id: str
    video_id: str
    video_url: str
    video_title: str
    status: TaskStatusEnum
    processing_mode: ProcessingModeEnum
    progress: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    download_url: str | None = None
    error_message: str | None = None


class TaskListResponse(BaseModel):
    """List of tasks response."""

    tasks: list[TaskResponse]
    total: int


class SourceListResponse(BaseModel):
    """List of sources response."""

    sources: list[SourceResponse]


class VideoListResponse(BaseModel):
    """List of videos from a source."""

    source_id: str
    videos: list[VideoPreviewResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    pending_tasks: int


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None


class VideoFormatInfo(BaseModel):
    """Video format information."""

    id: str
    description: str
    estimated_size_mb_per_min: float


class VideoFormatsResponse(BaseModel):
    """List of available video formats."""

    formats: list[VideoFormatInfo]
    default_format: str


class StorageStatsResponse(BaseModel):
    """Storage statistics response."""

    total_size_mb: float
    file_count: int
    quota_gb: float
    quota_used_percent: float
    cache_hours: int
    onedrive_enabled: bool
    onedrive_usage_mb: float | None = None


class MaintenanceResponse(BaseModel):
    """Maintenance operation response."""

    files_removed: int
    bytes_freed_mb: float
    storage_before_mb: float
    storage_after_mb: float
