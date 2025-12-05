"""
Storage Manager - Intelligent caching, cleanup, and OneDrive integration.

Features:
- Smart video caching (avoid re-downloading same videos)
- Automatic cleanup based on age and storage quota
- OneDrive integration via rclone
- Storage quota management
"""

import os
import logging
import subprocess
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CachedVideo:
    """Cached video metadata."""

    video_id: str
    source_id: str
    format_id: str  # e.g., "720p", "480p", "360p"
    file_path: str
    file_size: int  # bytes
    created_at: str
    last_accessed: str
    access_count: int
    has_subtitle: bool
    subtitle_path: Optional[str] = None


@dataclass
class StorageStats:
    """Storage statistics."""

    total_size: int  # bytes
    file_count: int
    oldest_file: Optional[str]
    newest_file: Optional[str]
    quota_used_percent: float


class StorageManager:
    """Manages video storage, caching, and cleanup."""

    def __init__(
        self,
        local_path: Path,
        onedrive_path: Optional[str] = None,
        quota_bytes: int = 10 * 1024 * 1024 * 1024,  # 10GB default
        cache_hours: int = 24,
        enable_onedrive: bool = False,
    ):
        """Initialize storage manager.

        Args:
            local_path: Local storage directory
            onedrive_path: OneDrive rclone path (e.g., "onedrive:videos")
            quota_bytes: Storage quota in bytes (default 10GB)
            cache_hours: How long to keep cached files
            enable_onedrive: Whether to use OneDrive for storage
        """
        self.local_path = Path(local_path)
        self.onedrive_path = onedrive_path
        self.quota_bytes = quota_bytes
        self.cache_hours = cache_hours
        self.enable_onedrive = enable_onedrive

        # Ensure directories exist
        self.local_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.local_path / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.processed_dir = self.local_path / "processed"
        self.processed_dir.mkdir(exist_ok=True)

        # Cache index file
        self.cache_index_path = self.local_path / "cache_index.json"
        self.cache_index: Dict[str, CachedVideo] = self._load_cache_index()

        logger.info(f"Storage manager initialized: {local_path}")
        logger.info(f"Quota: {quota_bytes / (1024**3):.1f}GB, Cache hours: {cache_hours}")
        if enable_onedrive:
            logger.info(f"OneDrive enabled: {onedrive_path}")

    def _load_cache_index(self) -> Dict[str, CachedVideo]:
        """Load cache index from disk."""
        if self.cache_index_path.exists():
            try:
                with open(self.cache_index_path, "r") as f:
                    data = json.load(f)
                    return {k: CachedVideo(**v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
        return {}

    def _save_cache_index(self):
        """Save cache index to disk."""
        try:
            with open(self.cache_index_path, "w") as f:
                json.dump({k: asdict(v) for k, v in self.cache_index.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def get_cache_key(self, video_id: str, source_id: str, format_id: str) -> str:
        """Generate cache key for a video."""
        return f"{source_id}_{video_id}_{format_id}"

    def get_cached_video(
        self, video_id: str, source_id: str, format_id: str = "720p"
    ) -> Optional[CachedVideo]:
        """Get cached video if available.

        Args:
            video_id: YouTube video ID
            source_id: Source ID (e.g., "cnn10")
            format_id: Format/resolution

        Returns:
            CachedVideo if found and file exists, None otherwise
        """
        cache_key = self.get_cache_key(video_id, source_id, format_id)
        cached = self.cache_index.get(cache_key)

        if cached:
            # Verify file exists
            if Path(cached.file_path).exists():
                # Update access time
                cached.last_accessed = datetime.now().isoformat()
                cached.access_count += 1
                self._save_cache_index()
                logger.info(f"Cache hit: {cache_key} (accessed {cached.access_count} times)")
                return cached
            else:
                # File missing, remove from index
                del self.cache_index[cache_key]
                self._save_cache_index()
                logger.warning(f"Cache file missing: {cached.file_path}")

        return None

    def add_to_cache(
        self,
        video_id: str,
        source_id: str,
        format_id: str,
        file_path: Path,
        has_subtitle: bool = False,
        subtitle_path: Optional[Path] = None,
    ) -> CachedVideo:
        """Add video to cache.

        Args:
            video_id: YouTube video ID
            source_id: Source ID
            format_id: Format/resolution
            file_path: Path to video file
            has_subtitle: Whether video has embedded subtitle
            subtitle_path: Path to subtitle file

        Returns:
            CachedVideo entry
        """
        cache_key = self.get_cache_key(video_id, source_id, format_id)
        file_size = file_path.stat().st_size if file_path.exists() else 0

        cached = CachedVideo(
            video_id=video_id,
            source_id=source_id,
            format_id=format_id,
            file_path=str(file_path),
            file_size=file_size,
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            access_count=1,
            has_subtitle=has_subtitle,
            subtitle_path=str(subtitle_path) if subtitle_path else None,
        )

        self.cache_index[cache_key] = cached
        self._save_cache_index()
        logger.info(f"Added to cache: {cache_key} ({file_size / (1024**2):.1f}MB)")

        return cached

    def get_storage_stats(self) -> StorageStats:
        """Get current storage statistics."""
        total_size = 0
        file_count = 0
        oldest_time = None
        newest_time = None
        oldest_file = None
        newest_file = None

        for path in [self.cache_dir, self.processed_dir]:
            for file in path.rglob("*"):
                if file.is_file():
                    file_count += 1
                    total_size += file.stat().st_size
                    mtime = file.stat().st_mtime

                    if oldest_time is None or mtime < oldest_time:
                        oldest_time = mtime
                        oldest_file = str(file)
                    if newest_time is None or mtime > newest_time:
                        newest_time = mtime
                        newest_file = str(file)

        return StorageStats(
            total_size=total_size,
            file_count=file_count,
            oldest_file=oldest_file,
            newest_file=newest_file,
            quota_used_percent=(total_size / self.quota_bytes * 100) if self.quota_bytes > 0 else 0,
        )

    def cleanup_expired(self) -> Tuple[int, int]:
        """Remove expired cache files.

        Returns:
            Tuple of (files_removed, bytes_freed)
        """
        cutoff = datetime.now() - timedelta(hours=self.cache_hours)
        files_removed = 0
        bytes_freed = 0

        # Clean up based on cache index
        expired_keys = []
        for key, cached in self.cache_index.items():
            last_accessed = datetime.fromisoformat(cached.last_accessed)
            if last_accessed < cutoff:
                file_path = Path(cached.file_path)
                if file_path.exists():
                    bytes_freed += file_path.stat().st_size
                    file_path.unlink()
                    files_removed += 1
                    logger.info(f"Removed expired: {file_path.name}")

                # Also remove subtitle if exists
                if cached.subtitle_path:
                    sub_path = Path(cached.subtitle_path)
                    if sub_path.exists():
                        sub_path.unlink()

                expired_keys.append(key)

        # Remove from index
        for key in expired_keys:
            del self.cache_index[key]

        # Clean up orphan files in processed dir
        for file in self.processed_dir.glob("*_processed.*"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < cutoff:
                bytes_freed += file.stat().st_size
                file.unlink()
                files_removed += 1
                logger.info(f"Removed orphan: {file.name}")

        if files_removed > 0:
            self._save_cache_index()
            logger.info(
                f"Cleanup: removed {files_removed} files, freed {bytes_freed / (1024**2):.1f}MB"
            )

        return files_removed, bytes_freed

    def cleanup_to_quota(self) -> Tuple[int, int]:
        """Remove oldest files until under quota.

        Returns:
            Tuple of (files_removed, bytes_freed)
        """
        stats = self.get_storage_stats()
        if stats.total_size <= self.quota_bytes:
            return 0, 0

        files_removed = 0
        bytes_freed = 0
        target_size = int(self.quota_bytes * 0.8)  # Clean to 80% of quota

        # Get all files sorted by last access time
        files_by_access = []
        for key, cached in self.cache_index.items():
            files_by_access.append((datetime.fromisoformat(cached.last_accessed), key, cached))

        files_by_access.sort(key=lambda x: x[0])  # Oldest first

        current_size = stats.total_size
        for _, key, cached in files_by_access:
            if current_size <= target_size:
                break

            file_path = Path(cached.file_path)
            if file_path.exists():
                file_size = file_path.stat().st_size
                file_path.unlink()
                current_size -= file_size
                bytes_freed += file_size
                files_removed += 1
                logger.info(f"Quota cleanup: removed {file_path.name}")

            # Remove subtitle
            if cached.subtitle_path:
                sub_path = Path(cached.subtitle_path)
                if sub_path.exists():
                    sub_path.unlink()

            del self.cache_index[key]

        if files_removed > 0:
            self._save_cache_index()
            logger.info(
                f"Quota cleanup: removed {files_removed} files, freed {bytes_freed / (1024**2):.1f}MB"
            )

        return files_removed, bytes_freed

    def sync_to_onedrive(self, file_path: Path) -> Optional[str]:
        """Sync file to OneDrive using rclone.

        Args:
            file_path: Local file path

        Returns:
            OneDrive URL if successful, None otherwise
        """
        if not self.enable_onedrive or not self.onedrive_path:
            return None

        try:
            remote_path = f"{self.onedrive_path}/{file_path.name}"
            cmd = ["rclone", "copy", str(file_path), self.onedrive_path]

            logger.info(f"Syncing to OneDrive: {file_path.name}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"Synced to OneDrive: {remote_path}")
                return remote_path
            else:
                logger.error(f"OneDrive sync failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("OneDrive sync timed out")
            return None
        except FileNotFoundError:
            logger.error("rclone not found. Install rclone to enable OneDrive sync.")
            return None
        except Exception as e:
            logger.error(f"OneDrive sync error: {e}")
            return None

    def get_onedrive_usage(self) -> Optional[int]:
        """Get OneDrive storage usage via rclone.

        Returns:
            Bytes used, or None if unavailable
        """
        if not self.enable_onedrive or not self.onedrive_path:
            return None

        try:
            cmd = ["rclone", "size", self.onedrive_path, "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("bytes", 0)
            return None

        except Exception as e:
            logger.error(f"Failed to get OneDrive usage: {e}")
            return None

    def run_maintenance(self) -> Dict:
        """Run full maintenance cycle.

        Returns:
            Maintenance report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "expired_cleanup": {"files": 0, "bytes": 0},
            "quota_cleanup": {"files": 0, "bytes": 0},
            "storage_before": None,
            "storage_after": None,
        }

        report["storage_before"] = asdict(self.get_storage_stats())

        # Cleanup expired files
        files, bytes_freed = self.cleanup_expired()
        report["expired_cleanup"] = {"files": files, "bytes": bytes_freed}

        # Cleanup to quota if needed
        files, bytes_freed = self.cleanup_to_quota()
        report["quota_cleanup"] = {"files": files, "bytes": bytes_freed}

        report["storage_after"] = asdict(self.get_storage_stats())

        logger.info(f"Maintenance complete: {report}")
        return report


# Video format options
VIDEO_FORMATS = {
    "360p": {
        "format": "best[height<=360]",
        "description": "Low quality (360p) - ~15MB/10min",
        "estimated_size_mb_per_min": 1.5,
    },
    "480p": {
        "format": "best[height<=480]",
        "description": "Medium quality (480p) - ~25MB/10min",
        "estimated_size_mb_per_min": 2.5,
    },
    "720p": {
        "format": "best[height<=720]",
        "description": "HD quality (720p) - ~50MB/10min",
        "estimated_size_mb_per_min": 5.0,
    },
    "1080p": {
        "format": "best[height<=1080]",
        "description": "Full HD (1080p) - ~100MB/10min",
        "estimated_size_mb_per_min": 10.0,
    },
    "audio_only": {
        "format": "bestaudio",
        "description": "Audio only (MP3) - ~10MB/10min",
        "estimated_size_mb_per_min": 1.0,
    },
}


def get_available_formats() -> List[Dict]:
    """Get list of available video formats for API."""
    return [
        {
            "id": format_id,
            "description": info["description"],
            "estimated_size": info["estimated_size_mb_per_min"],
        }
        for format_id, info in VIDEO_FORMATS.items()
    ]


def get_format_string(format_id: str) -> str:
    """Get yt-dlp format string for a format ID."""
    return VIDEO_FORMATS.get(format_id, VIDEO_FORMATS["720p"])["format"]
