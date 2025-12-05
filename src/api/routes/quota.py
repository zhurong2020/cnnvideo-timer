"""
Quota and User Management API routes.

Provides endpoints for:
- User quota checking
- Usage statistics
- Tier management (admin)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_user_id, verify_api_key
from src.core.quota import (
    TIER_LIMITS,
    UserTier,
    get_quota_manager,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/quota", tags=["quota"])


# Response Models
class TierInfo(BaseModel):
    """Tier information."""

    id: str
    name: str
    daily_tasks: int
    max_resolution: str
    allowed_modes: list[str]
    ai_subtitle: bool
    price_monthly: str | None = None


class TiersResponse(BaseModel):
    """Available tiers response."""

    tiers: list[TierInfo]


class UserQuotaResponse(BaseModel):
    """User quota status response."""

    user_id: str
    tier: str
    daily_tasks_used: int
    daily_tasks_limit: int
    daily_tasks_remaining: int
    total_tasks: int
    total_data_processed_mb: float
    max_resolution: str
    allowed_modes: list[str]
    ai_subtitle_enabled: bool
    member_since: str


class QuotaCheckResponse(BaseModel):
    """Quota check result response."""

    allowed: bool
    reason: str | None = None
    remaining_today: int
    tier: str


class UpgradeTierRequest(BaseModel):
    """Request to upgrade user tier."""

    user_id: str
    tier: str


# Endpoints
@router.get("/tiers", response_model=TiersResponse)
async def get_available_tiers():
    """
    Get available subscription tiers and their limits.

    No authentication required.
    """
    tiers = []
    prices = {
        "free": "Free",
        "basic": "¥19/month",
        "premium": "¥49/month",
    }

    for tier, limits in TIER_LIMITS.items():
        tiers.append(
            TierInfo(
                id=tier.value,
                name=tier.value.capitalize(),
                daily_tasks=limits.daily_tasks,
                max_resolution=limits.max_resolution,
                allowed_modes=limits.allowed_modes,
                ai_subtitle=limits.ai_subtitle,
                price_monthly=prices.get(tier.value),
            )
        )

    return TiersResponse(tiers=tiers)


@router.get("/me", response_model=UserQuotaResponse)
async def get_my_quota(
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """
    Get current user's quota status and usage.

    Requires API key authentication.
    """
    manager = get_quota_manager()
    stats = manager.get_user_stats(user_id)

    # Convert "unlimited" to -1 for API response
    daily_remaining = stats["daily_tasks_remaining"]
    if daily_remaining == "unlimited":
        daily_remaining = -1

    daily_limit = stats["daily_tasks_limit"]
    if daily_limit == "unlimited":
        daily_limit = -1

    return UserQuotaResponse(
        user_id=stats["user_id"],
        tier=stats["tier"],
        daily_tasks_used=stats["daily_tasks_used"],
        daily_tasks_limit=daily_limit,
        daily_tasks_remaining=daily_remaining,
        total_tasks=stats["total_tasks"],
        total_data_processed_mb=stats["total_data_processed_mb"],
        max_resolution=stats["max_resolution"],
        allowed_modes=stats["allowed_modes"],
        ai_subtitle_enabled=stats["ai_subtitle_enabled"],
        member_since=stats["member_since"],
    )


@router.get("/check")
async def check_quota(
    processing_mode: str = "with_subtitle",
    video_format: str = "720p",
    api_key: str = Depends(verify_api_key),
    user_id: str = Depends(get_user_id),
):
    """
    Check if user can create a task with specified parameters.

    Requires API key authentication.
    """
    manager = get_quota_manager()
    result = manager.check_quota(user_id, processing_mode, video_format)

    return {
        "allowed": result.allowed,
        "reason": result.reason,
        "remaining_today": result.remaining_today,
        "tier": result.tier,
        "requested": {
            "processing_mode": processing_mode,
            "video_format": video_format,
        },
    }


@router.post("/upgrade")
async def upgrade_user_tier(
    request: UpgradeTierRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Upgrade/change user tier (admin function).

    In production, this would be called after payment verification.
    Requires API key authentication.
    """
    # Validate tier
    try:
        tier = UserTier(request.tier)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier: {request.tier}. Valid tiers: {[t.value for t in UserTier]}",
        )

    manager = get_quota_manager()
    user = manager.set_user_tier(request.user_id, tier)

    logger.info(f"User {request.user_id} upgraded to {tier.value}")

    return {
        "success": True,
        "user_id": request.user_id,
        "new_tier": user.tier,
        "message": f"User tier updated to {tier.value}",
    }


@router.get("/users")
async def list_all_users(
    api_key: str = Depends(verify_api_key),
):
    """
    List all users and their usage (admin function).

    Requires API key authentication.
    """
    manager = get_quota_manager()
    users = manager.get_all_users_stats()

    return {
        "total_users": len(users),
        "users": users,
    }


@router.get("/stats")
async def get_quota_stats(
    api_key: str = Depends(verify_api_key),
):
    """
    Get overall quota system statistics (admin function).

    Requires API key authentication.
    """
    manager = get_quota_manager()
    users = manager.get_all_users_stats()

    tier_counts = {"free": 0, "basic": 0, "premium": 0}
    total_tasks = 0
    total_data_mb = 0

    for user in users:
        tier_counts[user["tier"]] = tier_counts.get(user["tier"], 0) + 1
        total_tasks += user["total_tasks"]
        total_data_mb += user["total_data_processed_mb"]

    return {
        "total_users": len(users),
        "users_by_tier": tier_counts,
        "total_tasks_processed": total_tasks,
        "total_data_processed_gb": total_data_mb / 1024,
        "tiers_available": [t.value for t in UserTier],
    }
