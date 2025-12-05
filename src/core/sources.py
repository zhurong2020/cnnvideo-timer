"""
Video Source Configuration Manager.

Manages video sources from config/sources.json for easy admin customization.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VideoSource:
    """Video source configuration."""
    id: str
    name: str
    description: str
    url: str
    channel_id: Optional[str]
    category: str
    language: str
    difficulty: str
    typical_duration: str
    update_frequency: str
    subtitle_available: bool
    enabled: bool
    tags: List[str]
    playlists: Optional[Dict[str, str]] = None


@dataclass
class SourceCategory:
    """Source category definition."""
    id: str
    name: str
    description: str
    recommended_for: List[str]


@dataclass
class DifficultyLevel:
    """Difficulty level definition."""
    id: str
    name: str
    description: str


class SourceConfigManager:
    """Manages video source configuration from JSON file."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize source config manager.

        Args:
            config_path: Path to sources.json. If None, uses default location.
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent.parent / "config" / "sources.json"
        else:
            self.config_path = Path(config_path)

        self._sources: Dict[str, VideoSource] = {}
        self._categories: Dict[str, SourceCategory] = {}
        self._difficulty_levels: Dict[str, DifficultyLevel] = {}
        self._last_loaded: Optional[datetime] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load source configuration from JSON file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Parse sources
                for source_id, source_data in data.get("sources", {}).items():
                    self._sources[source_id] = VideoSource(
                        id=source_id,
                        name=source_data.get("name", source_id),
                        description=source_data.get("description", ""),
                        url=source_data.get("url", ""),
                        channel_id=source_data.get("channel_id"),
                        category=source_data.get("category", "general"),
                        language=source_data.get("language", "en"),
                        difficulty=source_data.get("difficulty", "intermediate"),
                        typical_duration=source_data.get("typical_duration", "varies"),
                        update_frequency=source_data.get("update_frequency", "varies"),
                        subtitle_available=source_data.get("subtitle_available", True),
                        enabled=source_data.get("enabled", True),
                        tags=source_data.get("tags", []),
                        playlists=source_data.get("playlists"),
                    )

                # Parse categories
                for cat_id, cat_data in data.get("categories", {}).items():
                    self._categories[cat_id] = SourceCategory(
                        id=cat_id,
                        name=cat_data.get("name", cat_id),
                        description=cat_data.get("description", ""),
                        recommended_for=cat_data.get("recommended_for", []),
                    )

                # Parse difficulty levels
                for diff_id, diff_data in data.get("difficulty_levels", {}).items():
                    self._difficulty_levels[diff_id] = DifficultyLevel(
                        id=diff_id,
                        name=diff_data.get("name", diff_id),
                        description=diff_data.get("description", ""),
                    )

                self._last_loaded = datetime.now()
                logger.info(f"Loaded source config: {len(self._sources)} sources, {len(self._categories)} categories")

            except Exception as e:
                logger.warning(f"Failed to load source config: {e}")
                self._sources = {}
        else:
            logger.info(f"Source config not found at {self.config_path}")

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def get_source(self, source_id: str) -> Optional[VideoSource]:
        """Get a specific source by ID."""
        return self._sources.get(source_id)

    def get_all_sources(self, enabled_only: bool = True) -> Dict[str, VideoSource]:
        """Get all sources.

        Args:
            enabled_only: If True, only return enabled sources
        """
        if enabled_only:
            return {k: v for k, v in self._sources.items() if v.enabled}
        return self._sources.copy()

    def get_sources_by_category(self, category: str, enabled_only: bool = True) -> List[VideoSource]:
        """Get sources in a specific category."""
        sources = self.get_all_sources(enabled_only)
        return [s for s in sources.values() if s.category == category]

    def get_sources_by_difficulty(self, difficulty: str, enabled_only: bool = True) -> List[VideoSource]:
        """Get sources matching a difficulty level."""
        sources = self.get_all_sources(enabled_only)
        return [s for s in sources.values() if s.difficulty == difficulty]

    def get_sources_by_language(self, language: str, enabled_only: bool = True) -> List[VideoSource]:
        """Get sources in a specific language."""
        sources = self.get_all_sources(enabled_only)
        return [s for s in sources.values() if s.language.startswith(language)]

    def search_sources(
        self,
        query: str = "",
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        language: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[VideoSource]:
        """Search sources with multiple filters.

        Args:
            query: Text to search in name, description, and tags
            category: Filter by category
            difficulty: Filter by difficulty
            language: Filter by language
            enabled_only: Only return enabled sources

        Returns:
            List of matching sources
        """
        sources = list(self.get_all_sources(enabled_only).values())

        if category:
            sources = [s for s in sources if s.category == category]

        if difficulty:
            sources = [s for s in sources if s.difficulty == difficulty]

        if language:
            sources = [s for s in sources if s.language.startswith(language)]

        if query:
            query_lower = query.lower()
            sources = [
                s for s in sources
                if query_lower in s.name.lower()
                or query_lower in s.description.lower()
                or any(query_lower in tag.lower() for tag in s.tags)
            ]

        return sources

    def get_categories(self) -> Dict[str, SourceCategory]:
        """Get all categories."""
        return self._categories.copy()

    def get_difficulty_levels(self) -> Dict[str, DifficultyLevel]:
        """Get all difficulty levels."""
        return self._difficulty_levels.copy()

    def enable_source(self, source_id: str, enabled: bool = True) -> bool:
        """Enable or disable a source.

        Args:
            source_id: Source to update
            enabled: Whether to enable

        Returns:
            True if successful
        """
        return self._update_source(source_id, {"enabled": enabled})

    def _update_source(self, source_id: str, updates: Dict[str, Any]) -> bool:
        """Update a source and save to file."""
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if source_id not in data.get("sources", {}):
                return False

            data["sources"][source_id].update(updates)
            data["_last_updated"] = datetime.now().date().isoformat()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._load_config()
            logger.info(f"Updated source {source_id}: {updates}")
            return True

        except Exception as e:
            logger.error(f"Failed to update source: {e}")
            return False

    def add_source(self, source_id: str, source_data: Dict[str, Any]) -> bool:
        """Add a new source.

        Args:
            source_id: Unique source ID
            source_data: Source configuration

        Returns:
            True if successful
        """
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if source_id in data.get("sources", {}):
                logger.warning(f"Source {source_id} already exists")
                return False

            # Set defaults
            defaults = {
                "enabled": True,
                "subtitle_available": True,
                "language": "en",
                "difficulty": "intermediate",
                "typical_duration": "varies",
                "update_frequency": "varies",
                "tags": [],
            }
            defaults.update(source_data)

            data["sources"][source_id] = defaults
            data["_last_updated"] = datetime.now().date().isoformat()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._load_config()
            logger.info(f"Added new source: {source_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add source: {e}")
            return False

    def remove_source(self, source_id: str) -> bool:
        """Remove a source.

        Args:
            source_id: Source to remove

        Returns:
            True if successful
        """
        if not self.config_path.exists():
            return False

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if source_id not in data.get("sources", {}):
                return False

            del data["sources"][source_id]
            data["_last_updated"] = datetime.now().date().isoformat()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._load_config()
            logger.info(f"Removed source: {source_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove source: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Export all configuration as dictionary."""
        return {
            "sources": {
                source_id: {
                    "name": s.name,
                    "description": s.description,
                    "url": s.url,
                    "channel_id": s.channel_id,
                    "category": s.category,
                    "language": s.language,
                    "difficulty": s.difficulty,
                    "typical_duration": s.typical_duration,
                    "update_frequency": s.update_frequency,
                    "subtitle_available": s.subtitle_available,
                    "enabled": s.enabled,
                    "tags": s.tags,
                    "playlists": s.playlists,
                }
                for source_id, s in self._sources.items()
            },
            "categories": {
                cat_id: {
                    "name": c.name,
                    "description": c.description,
                    "recommended_for": c.recommended_for,
                }
                for cat_id, c in self._categories.items()
            },
            "difficulty_levels": {
                diff_id: {
                    "name": d.name,
                    "description": d.description,
                }
                for diff_id, d in self._difficulty_levels.items()
            },
        }


# Global source config manager instance
_source_config: Optional[SourceConfigManager] = None


def get_source_config() -> SourceConfigManager:
    """Get or create source config manager instance."""
    global _source_config
    if _source_config is None:
        _source_config = SourceConfigManager()
    return _source_config
