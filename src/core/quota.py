"""
User Quota Management System.

Implements usage limits and tier-based permissions for monetization.

Tier configuration is loaded from config/tiers.json for easy admin customization.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


@dataclass
class TierLimits:
    """Limits for each user tier."""
    daily_tasks: int  # Max tasks per day (-1 = unlimited)
    max_resolution: str  # Max allowed resolution
    allowed_modes: List[str]  # Allowed processing modes
    priority: int  # Queue priority (higher = faster)
    ai_subtitle: bool  # Can use Whisper AI subtitle generation
    concurrent_tasks: int  # Max concurrent tasks
    # Optional pricing info
    name: str = ""
    description: str = ""
    price_monthly: str = ""
    price_yearly: str = ""


# Default tier configuration (fallback if config file not found)
DEFAULT_TIER_LIMITS: Dict[str, TierLimits] = {
    "free": TierLimits(
        daily_tasks=3,
        max_resolution="480p",
        allowed_modes=["original", "with_subtitle"],
        priority=1,
        ai_subtitle=False,
        concurrent_tasks=1,
        name="Free",
        description="Basic access",
        price_monthly="Free",
        price_yearly="Free",
    ),
    "basic": TierLimits(
        daily_tasks=15,
        max_resolution="720p",
        allowed_modes=["original", "with_subtitle", "repeat_twice"],
        priority=5,
        ai_subtitle=True,
        concurrent_tasks=2,
        name="Basic",
        description="For regular learners",
        price_monthly="19",
        price_yearly="190",
    ),
    "premium": TierLimits(
        daily_tasks=-1,
        max_resolution="1080p",
        allowed_modes=["original", "with_subtitle", "repeat_twice", "slow"],
        priority=10,
        ai_subtitle=True,
        concurrent_tasks=5,
        name="Premium",
        description="Unlimited access",
        price_monthly="49",
        price_yearly="490",
    ),
}


class TierConfigManager:
    """Manages tier configuration from JSON file."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize tier config manager.

        Args:
            config_path: Path to tiers.json. If None, uses default location.
        """
        if config_path is None:
            # Default to config/tiers.json relative to project root
            self.config_path = Path(__file__).parent.parent.parent / "config" / "tiers.json"
        else:
            self.config_path = Path(config_path)

        self._tier_limits: Dict[str, TierLimits] = {}
        self._processing_modes: Dict[str, Dict] = {}
        self._resolutions: List[str] = []
        self._last_loaded: Optional[datetime] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load tier configuration from JSON file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parse tiers
                for tier_id, tier_data in data.get("tiers", {}).items():
                    self._tier_limits[tier_id] = TierLimits(
                        daily_tasks=tier_data.get("daily_tasks", 3),
                        max_resolution=tier_data.get("max_resolution", "480p"),
                        allowed_modes=tier_data.get("allowed_modes", ["original"]),
                        priority=tier_data.get("priority", 1),
                        ai_subtitle=tier_data.get("ai_subtitle", False),
                        concurrent_tasks=tier_data.get("concurrent_tasks", 1),
                        name=tier_data.get("name", tier_id.capitalize()),
                        description=tier_data.get("description", ""),
                        price_monthly=tier_data.get("price_monthly", ""),
                        price_yearly=tier_data.get("price_yearly", ""),
                    )

                self._processing_modes = data.get("processing_modes", {})
                self._resolutions = data.get("resolutions", ["360p", "480p", "720p", "1080p"])
                self._last_loaded = datetime.now()

                logger.info(f"Loaded tier config from {self.config_path}: {len(self._tier_limits)} tiers")

            except Exception as e:
                logger.warning(f"Failed to load tier config: {e}, using defaults")
                self._tier_limits = DEFAULT_TIER_LIMITS.copy()
        else:
            logger.info(f"Tier config not found at {self.config_path}, using defaults")
            self._tier_limits = DEFAULT_TIER_LIMITS.copy()

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def get_tier_limits(self, tier: str) -> TierLimits:
        """Get limits for a specific tier."""
        return self._tier_limits.get(tier, self._tier_limits.get("free", DEFAULT_TIER_LIMITS["free"]))

    def get_all_tiers(self) -> Dict[str, TierLimits]:
        """Get all tier configurations."""
        return self._tier_limits.copy()

    def get_tier_ids(self) -> List[str]:
        """Get list of available tier IDs."""
        return list(self._tier_limits.keys())

    def get_processing_modes(self) -> Dict[str, Dict]:
        """Get processing mode definitions."""
        return self._processing_modes.copy()

    def get_resolutions(self) -> List[str]:
        """Get available resolutions."""
        return self._resolutions.copy()

    def update_tier(self, tier_id: str, updates: Dict[str, Any]) -> bool:
        """Update a tier configuration and save to file.

        Args:
            tier_id: Tier to update
            updates: Dictionary of fields to update

        Returns:
            True if successful
        """
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if tier_id not in data.get("tiers", {}):
                return False

            # Update the tier
            data["tiers"][tier_id].update(updates)
            data["_last_updated"] = date.today().isoformat()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Reload config
            self._load_config()
            logger.info(f"Updated tier {tier_id}: {updates}")
            return True

        except Exception as e:
            logger.error(f"Failed to update tier config: {e}")
            return False


# Global tier config manager instance
_tier_config: Optional[TierConfigManager] = None


def get_tier_config() -> TierConfigManager:
    """Get or create tier config manager instance."""
    global _tier_config
    if _tier_config is None:
        _tier_config = TierConfigManager()
    return _tier_config


# Legacy TIER_LIMITS for backward compatibility
TIER_LIMITS: Dict[UserTier, TierLimits] = {
    UserTier.FREE: DEFAULT_TIER_LIMITS["free"],
    UserTier.BASIC: DEFAULT_TIER_LIMITS["basic"],
    UserTier.PREMIUM: DEFAULT_TIER_LIMITS["premium"],
}


@dataclass
class UserUsage:
    """User usage tracking."""
    user_id: str
    tier: str = "free"
    daily_task_count: int = 0
    last_task_date: str = ""
    total_tasks: int = 0
    total_bytes_processed: int = 0
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class QuotaCheckResult:
    """Result of quota check."""
    allowed: bool
    reason: Optional[str] = None
    remaining_today: int = 0
    tier: str = "free"
    limits: Optional[Dict] = None


class QuotaManager:
    """Manages user quotas and usage tracking."""

    def __init__(self, data_dir: Path):
        """Initialize quota manager.

        Args:
            data_dir: Directory for storing quota data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "user_usage.json"
        self.users: Dict[str, UserUsage] = self._load_usage()
        logger.info(f"Quota manager initialized with {len(self.users)} users")

    def _load_usage(self) -> Dict[str, UserUsage]:
        """Load user usage from disk."""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, "r") as f:
                    data = json.load(f)
                    return {k: UserUsage(**v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load usage data: {e}")
        return {}

    def _save_usage(self):
        """Save user usage to disk."""
        try:
            with open(self.usage_file, "w") as f:
                json.dump(
                    {k: asdict(v) for k, v in self.users.items()},
                    f, indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

    def get_user(self, user_id: str) -> UserUsage:
        """Get or create user usage record."""
        if user_id not in self.users:
            self.users[user_id] = UserUsage(user_id=user_id)
            self._save_usage()
            logger.info(f"Created new user: {user_id}")
        return self.users[user_id]

    def set_user_tier(self, user_id: str, tier: UserTier) -> UserUsage:
        """Set user tier (for upgrades/downgrades).

        Args:
            user_id: User identifier
            tier: New tier level

        Returns:
            Updated user usage record
        """
        user = self.get_user(user_id)
        old_tier = user.tier
        user.tier = tier.value
        user.updated_at = datetime.now().isoformat()
        self._save_usage()
        logger.info(f"User {user_id} tier changed: {old_tier} -> {tier.value}")
        return user

    def get_tier_limits(self, tier: str) -> TierLimits:
        """Get limits for a tier from config file."""
        tier_config = get_tier_config()
        return tier_config.get_tier_limits(tier)

    def check_quota(
        self,
        user_id: str,
        processing_mode: str = "with_subtitle",
        video_format: str = "720p",
    ) -> QuotaCheckResult:
        """Check if user can create a new task.

        Args:
            user_id: User identifier
            processing_mode: Requested processing mode
            video_format: Requested video format

        Returns:
            QuotaCheckResult with allowed status and details
        """
        user = self.get_user(user_id)
        tier = UserTier(user.tier) if user.tier in [t.value for t in UserTier] else UserTier.FREE
        limits = self.get_tier_limits(user.tier)

        today = date.today().isoformat()

        # Reset daily count if new day
        if user.last_task_date != today:
            user.daily_task_count = 0
            user.last_task_date = today

        # Calculate remaining
        if limits.daily_tasks == -1:
            remaining = -1  # Unlimited
        else:
            remaining = max(0, limits.daily_tasks - user.daily_task_count)

        # Check daily limit
        if limits.daily_tasks != -1 and user.daily_task_count >= limits.daily_tasks:
            return QuotaCheckResult(
                allowed=False,
                reason=f"Daily limit reached ({limits.daily_tasks} tasks/day for {tier.value} tier). Upgrade to increase limit.",
                remaining_today=0,
                tier=tier.value,
                limits=asdict(limits),
            )

        # Check processing mode permission
        if processing_mode not in limits.allowed_modes:
            return QuotaCheckResult(
                allowed=False,
                reason=f"Processing mode '{processing_mode}' not available for {tier.value} tier. Upgrade to access this feature.",
                remaining_today=remaining,
                tier=tier.value,
                limits=asdict(limits),
            )

        # Check resolution permission
        resolution_order = ["360p", "480p", "720p", "1080p"]
        requested_idx = resolution_order.index(video_format) if video_format in resolution_order else 0
        max_idx = resolution_order.index(limits.max_resolution) if limits.max_resolution in resolution_order else 0

        if requested_idx > max_idx:
            return QuotaCheckResult(
                allowed=False,
                reason=f"Resolution '{video_format}' not available for {tier.value} tier. Max: {limits.max_resolution}. Upgrade for higher quality.",
                remaining_today=remaining,
                tier=tier.value,
                limits=asdict(limits),
            )

        return QuotaCheckResult(
            allowed=True,
            remaining_today=remaining if remaining != -1 else 999999,
            tier=tier.value,
            limits=asdict(limits),
        )

    def record_task(self, user_id: str, bytes_processed: int = 0) -> UserUsage:
        """Record a task usage.

        Args:
            user_id: User identifier
            bytes_processed: Size of processed video

        Returns:
            Updated user usage record
        """
        user = self.get_user(user_id)
        today = date.today().isoformat()

        # Reset if new day
        if user.last_task_date != today:
            user.daily_task_count = 0
            user.last_task_date = today

        user.daily_task_count += 1
        user.total_tasks += 1
        user.total_bytes_processed += bytes_processed
        user.updated_at = datetime.now().isoformat()

        self._save_usage()
        logger.info(f"Recorded task for {user_id}: daily={user.daily_task_count}, total={user.total_tasks}")

        return user

    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics.

        Args:
            user_id: User identifier

        Returns:
            User statistics dictionary
        """
        user = self.get_user(user_id)
        limits = self.get_tier_limits(user.tier)
        today = date.today().isoformat()

        # Reset daily count if new day
        daily_count = user.daily_task_count if user.last_task_date == today else 0

        if limits.daily_tasks == -1:
            remaining = -1
            daily_limit = "unlimited"
        else:
            remaining = max(0, limits.daily_tasks - daily_count)
            daily_limit = limits.daily_tasks

        return {
            "user_id": user_id,
            "tier": user.tier,
            "daily_tasks_used": daily_count,
            "daily_tasks_limit": daily_limit,
            "daily_tasks_remaining": remaining if remaining != -1 else "unlimited",
            "total_tasks": user.total_tasks,
            "total_data_processed_mb": user.total_bytes_processed / (1024 * 1024),
            "max_resolution": limits.max_resolution,
            "allowed_modes": limits.allowed_modes,
            "ai_subtitle_enabled": limits.ai_subtitle,
            "member_since": user.created_at,
        }

    def get_all_users_stats(self) -> List[Dict]:
        """Get statistics for all users (admin function)."""
        return [self.get_user_stats(user_id) for user_id in self.users.keys()]


# Global instance
_quota_manager: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Get or create quota manager instance."""
    global _quota_manager
    if _quota_manager is None:
        from src.core.config import get_settings
        settings = get_settings()
        _quota_manager = QuotaManager(settings.data_dir)
    return _quota_manager
