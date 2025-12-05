"""
Video sources API routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models import (
    SourceResponse,
    SourceListResponse,
    VideoListResponse,
    VideoPreviewResponse,
    VideoPreviewRequest,
    UserTierEnum,
)
from ...sources.youtube import get_source, get_all_sources
from ...sources.base import UserTier
from ..dependencies import verify_api_key

router = APIRouter(prefix="/sources", tags=["sources"])


def _tier_to_enum(tier: UserTier) -> UserTierEnum:
    """Convert internal UserTier to API enum."""
    return UserTierEnum(tier.value)


@router.get("", response_model=SourceListResponse)
async def list_sources(
    tier: UserTierEnum = Query(default=UserTierEnum.FREE, description="User tier to filter sources")
):
    """Get list of available video sources."""
    all_sources = get_all_sources()
    user_tier = UserTier(tier.value)

    sources = [
        SourceResponse(
            id=s.info.id,
            name=s.info.name,
            description=s.info.description,
            url=s.info.url,
            icon=s.info.icon,
            min_tier=_tier_to_enum(s.info.min_tier),
            tags=s.info.tags,
        )
        for s in all_sources
        if s.is_available_for_tier(user_tier)
    ]

    return SourceListResponse(sources=sources)


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source_info(source_id: str):
    """Get information about a specific source."""
    source = get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    return SourceResponse(
        id=source.info.id,
        name=source.info.name,
        description=source.info.description,
        url=source.info.url,
        icon=source.info.icon,
        min_tier=_tier_to_enum(source.info.min_tier),
        tags=source.info.tags,
    )


@router.get("/{source_id}/videos", response_model=VideoListResponse)
async def list_source_videos(
    source_id: str,
    limit: int = Query(default=10, ge=1, le=50, description="Maximum videos to return"),
):
    """Get latest videos from a source."""
    source = get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    videos = await source.get_latest_videos(limit=limit)

    return VideoListResponse(
        source_id=source_id,
        videos=[
            VideoPreviewResponse(
                id=v.id,
                title=v.title,
                url=v.url,
                thumbnail=v.thumbnail,
                duration=v.duration,
                upload_date=v.upload_date,
                source_id=v.source_id,
            )
            for v in videos
        ],
    )


@router.post("/preview", response_model=VideoPreviewResponse)
async def preview_video(
    request: VideoPreviewRequest,
    api_key: str = Depends(verify_api_key),
):
    """Preview video information without downloading."""
    from ...core.downloader import VideoDownloader

    downloader = VideoDownloader()
    info = downloader.get_video_info(request.url)

    if not info:
        raise HTTPException(status_code=400, detail="Could not get video information")

    return VideoPreviewResponse(
        id=info.id,
        title=info.title,
        url=info.url,
        thumbnail=info.thumbnail,
        duration=info.duration,
        upload_date=info.upload_date,
    )
