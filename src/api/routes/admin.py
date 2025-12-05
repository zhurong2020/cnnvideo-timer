"""
Admin API routes for configuration management.

Provides endpoints for:
- Tier configuration management
- Video source configuration management
- System configuration reload
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import verify_api_key
from src.core.quota import get_tier_config
from src.core.sources import get_source_config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ============================================
# Request/Response Models
# ============================================


class TierUpdateRequest(BaseModel):
    """Request to update tier configuration."""

    daily_tasks: int | None = Field(None, description="Max tasks per day (-1 for unlimited)")
    max_resolution: str | None = Field(
        None, description="Max resolution (360p, 480p, 720p, 1080p)"
    )
    allowed_modes: list[str] | None = Field(None, description="Allowed processing modes")
    priority: int | None = Field(None, description="Queue priority")
    ai_subtitle: bool | None = Field(None, description="Allow AI subtitle generation")
    concurrent_tasks: int | None = Field(None, description="Max concurrent tasks")
    name: str | None = Field(None, description="Display name")
    description: str | None = Field(None, description="Description")
    price_monthly: str | None = Field(None, description="Monthly price")
    price_yearly: str | None = Field(None, description="Yearly price")


class TierResponse(BaseModel):
    """Tier configuration response."""

    id: str
    name: str
    description: str
    daily_tasks: int
    max_resolution: str
    allowed_modes: list[str]
    priority: int
    ai_subtitle: bool
    concurrent_tasks: int
    price_monthly: str
    price_yearly: str


class TiersConfigResponse(BaseModel):
    """All tiers configuration response."""

    tiers: list[TierResponse]
    processing_modes: dict[str, dict]
    resolutions: list[str]


class SourceResponse(BaseModel):
    """Video source response."""

    id: str
    name: str
    description: str
    url: str
    channel_id: str | None
    category: str
    language: str
    difficulty: str
    typical_duration: str
    update_frequency: str
    subtitle_available: bool
    enabled: bool
    tags: list[str]
    playlists: dict[str, str] | None = None


class SourcesConfigResponse(BaseModel):
    """All sources configuration response."""

    sources: list[SourceResponse]
    categories: dict[str, dict]
    difficulty_levels: dict[str, dict]
    total_enabled: int
    total_disabled: int


class SourceCreateRequest(BaseModel):
    """Request to create a new source."""

    name: str = Field(..., description="Source display name")
    description: str = Field(..., description="Source description")
    url: str = Field(..., description="YouTube channel URL")
    channel_id: str | None = Field(None, description="YouTube channel ID")
    category: str = Field("general", description="Category ID")
    language: str = Field("en", description="Language code")
    difficulty: str = Field("intermediate", description="Difficulty level")
    typical_duration: str = Field("varies", description="Typical video duration")
    update_frequency: str = Field("varies", description="Content update frequency")
    subtitle_available: bool = Field(True, description="Has subtitles")
    enabled: bool = Field(True, description="Is enabled")
    tags: list[str] = Field(default_factory=list, description="Search tags")


class SourceUpdateRequest(BaseModel):
    """Request to update a source."""

    name: str | None = None
    description: str | None = None
    url: str | None = None
    channel_id: str | None = None
    category: str | None = None
    language: str | None = None
    difficulty: str | None = None
    typical_duration: str | None = None
    update_frequency: str | None = None
    subtitle_available: bool | None = None
    enabled: bool | None = None
    tags: list[str] | None = None


# ============================================
# Tier Management Endpoints
# ============================================


@router.get("/tiers", response_model=TiersConfigResponse)
async def get_tiers_config(
    api_key: str = Depends(verify_api_key),
):
    """
    Get all tier configurations (admin).

    Returns full tier config including pricing and limits.
    """
    tier_config = get_tier_config()
    tiers = []

    for tier_id, limits in tier_config.get_all_tiers().items():
        tiers.append(
            TierResponse(
                id=tier_id,
                name=limits.name or tier_id.capitalize(),
                description=limits.description or "",
                daily_tasks=limits.daily_tasks,
                max_resolution=limits.max_resolution,
                allowed_modes=limits.allowed_modes,
                priority=limits.priority,
                ai_subtitle=limits.ai_subtitle,
                concurrent_tasks=limits.concurrent_tasks,
                price_monthly=limits.price_monthly or "",
                price_yearly=limits.price_yearly or "",
            )
        )

    return TiersConfigResponse(
        tiers=tiers,
        processing_modes=tier_config.get_processing_modes(),
        resolutions=tier_config.get_resolutions(),
    )


@router.put("/tiers/{tier_id}")
async def update_tier(
    tier_id: str,
    request: TierUpdateRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Update a tier configuration (admin).

    Changes are saved to config/tiers.json.
    """
    tier_config = get_tier_config()

    if tier_id not in tier_config.get_tier_ids():
        raise HTTPException(
            status_code=404,
            detail=f"Tier '{tier_id}' not found. Available: {tier_config.get_tier_ids()}",
        )

    # Build updates dict from non-None values
    updates = {k: v for k, v in request.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    success = tier_config.update_tier(tier_id, updates)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update tier configuration")

    logger.info(f"Admin updated tier {tier_id}: {updates}")

    return {
        "success": True,
        "tier_id": tier_id,
        "updates": updates,
        "message": f"Tier '{tier_id}' updated successfully",
    }


@router.post("/tiers/reload")
async def reload_tiers_config(
    api_key: str = Depends(verify_api_key),
):
    """
    Reload tier configuration from file (admin).

    Use after manually editing config/tiers.json.
    """
    tier_config = get_tier_config()
    tier_config.reload()

    return {
        "success": True,
        "message": "Tier configuration reloaded",
        "tiers_loaded": tier_config.get_tier_ids(),
    }


# ============================================
# Source Management Endpoints
# ============================================


@router.get("/sources", response_model=SourcesConfigResponse)
async def get_sources_config(
    category: str | None = Query(None, description="Filter by category"),
    difficulty: str | None = Query(None, description="Filter by difficulty"),
    language: str | None = Query(None, description="Filter by language"),
    enabled_only: bool = Query(False, description="Only show enabled sources"),
    api_key: str = Depends(verify_api_key),
):
    """
    Get all video source configurations (admin).

    Returns full source list with filters.
    """
    source_config = get_source_config()

    # Get sources with filters
    if category or difficulty or language:
        source_list = source_config.search_sources(
            category=category,
            difficulty=difficulty,
            language=language,
            enabled_only=enabled_only,
        )
    else:
        source_list = list(source_config.get_all_sources(enabled_only=enabled_only).values())

    sources = [
        SourceResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            url=s.url,
            channel_id=s.channel_id,
            category=s.category,
            language=s.language,
            difficulty=s.difficulty,
            typical_duration=s.typical_duration,
            update_frequency=s.update_frequency,
            subtitle_available=s.subtitle_available,
            enabled=s.enabled,
            tags=s.tags,
            playlists=s.playlists,
        )
        for s in source_list
    ]

    # Get categories and difficulty levels
    categories = {
        cat_id: {"name": c.name, "description": c.description, "recommended_for": c.recommended_for}
        for cat_id, c in source_config.get_categories().items()
    }
    difficulty_levels = {
        diff_id: {"name": d.name, "description": d.description}
        for diff_id, d in source_config.get_difficulty_levels().items()
    }

    all_sources = source_config.get_all_sources(enabled_only=False)
    enabled_count = sum(1 for s in all_sources.values() if s.enabled)

    return SourcesConfigResponse(
        sources=sources,
        categories=categories,
        difficulty_levels=difficulty_levels,
        total_enabled=enabled_count,
        total_disabled=len(all_sources) - enabled_count,
    )


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: str,
    api_key: str = Depends(verify_api_key),
):
    """Get a specific source configuration."""
    source_config = get_source_config()
    source = source_config.get_source(source_id)

    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    return SourceResponse(
        id=source.id,
        name=source.name,
        description=source.description,
        url=source.url,
        channel_id=source.channel_id,
        category=source.category,
        language=source.language,
        difficulty=source.difficulty,
        typical_duration=source.typical_duration,
        update_frequency=source.update_frequency,
        subtitle_available=source.subtitle_available,
        enabled=source.enabled,
        tags=source.tags,
        playlists=source.playlists,
    )


@router.post("/sources/{source_id}")
async def create_source(
    source_id: str,
    request: SourceCreateRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Create a new video source (admin).

    Source ID must be unique.
    """
    source_config = get_source_config()

    if source_config.get_source(source_id):
        raise HTTPException(status_code=409, detail=f"Source '{source_id}' already exists")

    source_data = request.model_dump()
    success = source_config.add_source(source_id, source_data)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create source")

    logger.info(f"Admin created source: {source_id}")

    return {
        "success": True,
        "source_id": source_id,
        "message": f"Source '{source_id}' created successfully",
    }


@router.put("/sources/{source_id}")
async def update_source(
    source_id: str,
    request: SourceUpdateRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Update a video source configuration (admin).

    Changes are saved to config/sources.json.
    """
    source_config = get_source_config()

    if not source_config.get_source(source_id):
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    updates = {k: v for k, v in request.model_dump().items() if v is not None}

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    success = source_config._update_source(source_id, updates)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update source")

    logger.info(f"Admin updated source {source_id}: {updates}")

    return {
        "success": True,
        "source_id": source_id,
        "updates": updates,
        "message": f"Source '{source_id}' updated successfully",
    }


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Delete a video source (admin).

    Removes from config/sources.json.
    """
    source_config = get_source_config()

    if not source_config.get_source(source_id):
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    success = source_config.remove_source(source_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete source")

    logger.info(f"Admin deleted source: {source_id}")

    return {
        "success": True,
        "source_id": source_id,
        "message": f"Source '{source_id}' deleted successfully",
    }


@router.post("/sources/{source_id}/enable")
async def enable_source(
    source_id: str,
    enabled: bool = Query(True, description="Enable or disable"),
    api_key: str = Depends(verify_api_key),
):
    """Enable or disable a video source (admin)."""
    source_config = get_source_config()

    if not source_config.get_source(source_id):
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    success = source_config.enable_source(source_id, enabled)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update source")

    status = "enabled" if enabled else "disabled"
    logger.info(f"Admin {status} source: {source_id}")

    return {
        "success": True,
        "source_id": source_id,
        "enabled": enabled,
        "message": f"Source '{source_id}' {status}",
    }


@router.post("/sources/reload")
async def reload_sources_config(
    api_key: str = Depends(verify_api_key),
):
    """
    Reload source configuration from file (admin).

    Use after manually editing config/sources.json.
    """
    source_config = get_source_config()
    source_config.reload()

    all_sources = source_config.get_all_sources(enabled_only=False)
    enabled_count = sum(1 for s in all_sources.values() if s.enabled)

    return {
        "success": True,
        "message": "Source configuration reloaded",
        "total_sources": len(all_sources),
        "enabled_sources": enabled_count,
    }


# ============================================
# System Endpoints
# ============================================


@router.post("/reload-all")
async def reload_all_config(
    api_key: str = Depends(verify_api_key),
):
    """
    Reload all configuration files (admin).

    Reloads tiers.json and sources.json.
    """
    tier_config = get_tier_config()
    source_config = get_source_config()

    tier_config.reload()
    source_config.reload()

    return {
        "success": True,
        "message": "All configurations reloaded",
        "tiers": tier_config.get_tier_ids(),
        "sources_count": len(source_config.get_all_sources(enabled_only=False)),
    }
