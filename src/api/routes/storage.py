"""
Storage management API routes.

Provides endpoints for:
- Storage statistics
- Manual cleanup/maintenance
- Video format options
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from src.core.config import get_settings
from src.api.dependencies import verify_api_key
from src.api.models import (
    VideoFormatsResponse,
    VideoFormatInfo,
    StorageStatsResponse,
    MaintenanceResponse,
)
from src.storage.manager import (
    StorageManager,
    VIDEO_FORMATS,
    get_available_formats,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/storage", tags=["storage"])

# Global storage manager instance
_storage_manager: StorageManager = None


def get_storage_manager() -> StorageManager:
    """Get or create storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        settings = get_settings()
        _storage_manager = StorageManager(
            local_path=settings.temp_dir,
            onedrive_path=settings.rclone_remote,
            quota_bytes=int(settings.storage_quota_gb * 1024 * 1024 * 1024),
            cache_hours=settings.cache_hours,
            enable_onedrive=settings.enable_onedrive,
        )
    return _storage_manager


@router.get("/formats", response_model=VideoFormatsResponse)
async def get_video_formats():
    """
    Get available video formats/resolutions.

    Returns list of formats with estimated file sizes.
    No authentication required.
    """
    settings = get_settings()
    formats = [
        VideoFormatInfo(
            id=fmt_id,
            description=fmt_info["description"],
            estimated_size_mb_per_min=fmt_info["estimated_size_mb_per_min"],
        )
        for fmt_id, fmt_info in VIDEO_FORMATS.items()
    ]

    return VideoFormatsResponse(
        formats=formats,
        default_format=settings.default_video_format,
    )


@router.get("/stats", response_model=StorageStatsResponse)
async def get_storage_stats(api_key: str = Depends(verify_api_key)):
    """
    Get storage statistics.

    Requires API key authentication.
    """
    settings = get_settings()
    manager = get_storage_manager()
    stats = manager.get_storage_stats()

    # Get OneDrive usage if enabled
    onedrive_usage = None
    if settings.enable_onedrive:
        onedrive_bytes = manager.get_onedrive_usage()
        if onedrive_bytes is not None:
            onedrive_usage = onedrive_bytes / (1024 * 1024)

    return StorageStatsResponse(
        total_size_mb=stats.total_size / (1024 * 1024),
        file_count=stats.file_count,
        quota_gb=settings.storage_quota_gb,
        quota_used_percent=stats.quota_used_percent,
        cache_hours=settings.cache_hours,
        onedrive_enabled=settings.enable_onedrive,
        onedrive_usage_mb=onedrive_usage,
    )


@router.post("/maintenance", response_model=MaintenanceResponse)
async def run_maintenance(api_key: str = Depends(verify_api_key)):
    """
    Run storage maintenance (cleanup expired files, enforce quota).

    Requires API key authentication.
    """
    manager = get_storage_manager()

    # Get stats before
    stats_before = manager.get_storage_stats()

    # Run maintenance
    report = manager.run_maintenance()

    # Get stats after
    stats_after = manager.get_storage_stats()

    total_files = report["expired_cleanup"]["files"] + report["quota_cleanup"]["files"]
    total_bytes = report["expired_cleanup"]["bytes"] + report["quota_cleanup"]["bytes"]

    logger.info(
        f"Maintenance completed: {total_files} files removed, {total_bytes / (1024**2):.1f}MB freed"
    )

    return MaintenanceResponse(
        files_removed=total_files,
        bytes_freed_mb=total_bytes / (1024 * 1024),
        storage_before_mb=stats_before.total_size / (1024 * 1024),
        storage_after_mb=stats_after.total_size / (1024 * 1024),
    )


@router.get("/cache")
async def get_cache_info(api_key: str = Depends(verify_api_key)):
    """
    Get cached videos information.

    Requires API key authentication.
    """
    manager = get_storage_manager()

    cache_entries = []
    for key, cached in manager.cache_index.items():
        cache_entries.append(
            {
                "video_id": cached.video_id,
                "source_id": cached.source_id,
                "format": cached.format_id,
                "size_mb": cached.file_size / (1024 * 1024),
                "access_count": cached.access_count,
                "has_subtitle": cached.has_subtitle,
                "last_accessed": cached.last_accessed,
            }
        )

    return {
        "cached_videos": len(cache_entries),
        "entries": sorted(cache_entries, key=lambda x: x["last_accessed"], reverse=True),
    }
