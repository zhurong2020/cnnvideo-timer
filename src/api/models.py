"""
Pydantic models for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
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
        default=ProcessingModeEnum.WITH_SUBTITLE,
        description="Video processing mode"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "source_id": "cnn10",
                "video_url": "https://www.youtube.com/watch?v=abc123",
                "processing_mode": "with_subtitle"
            }]
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
    icon: Optional[str] = None
    min_tier: UserTierEnum
    tags: List[str] = []


class VideoPreviewResponse(BaseModel):
    """Video preview information."""
    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: int = 0
    upload_date: Optional[str] = None
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
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None


class TaskListResponse(BaseModel):
    """List of tasks response."""
    tasks: List[TaskResponse]
    total: int


class SourceListResponse(BaseModel):
    """List of sources response."""
    sources: List[SourceResponse]


class VideoListResponse(BaseModel):
    """List of videos from a source."""
    source_id: str
    videos: List[VideoPreviewResponse]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    pending_tasks: int


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
