"""
Unit tests for configuration module.
"""

import os
import pytest
from pathlib import Path


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self, test_config):
        """Test default configuration values."""
        # Clear cache to get fresh settings
        from src.core.config import get_settings
        get_settings.cache_clear()

        settings = get_settings()

        assert settings.app_name == "SmartNews Learn"
        assert settings.app_version == "2.0.0"
        assert settings.api_port == 8000

    def test_debug_mode_from_env(self, test_config):
        """Test DEBUG mode is read from environment."""
        from src.core.config import get_settings
        get_settings.cache_clear()

        settings = get_settings()

        # We set DEBUG=true in test_config fixture
        assert settings.debug is True

    def test_api_key_from_env(self, test_config):
        """Test API_KEY is read from environment."""
        from src.core.config import get_settings
        get_settings.cache_clear()

        settings = get_settings()

        assert settings.api_key == "test-api-key-12345"

    def test_ensure_directories_creates_paths(self, test_config, tmp_path):
        """Test ensure_directories creates required directories."""
        from src.core.config import Settings

        settings = Settings(
            data_dir=tmp_path / "data",
            temp_dir=tmp_path / "data" / "temp",
            log_dir=tmp_path / "log",
        )

        settings.ensure_directories()

        assert (tmp_path / "data").exists()
        assert (tmp_path / "data" / "temp").exists()
        assert (tmp_path / "log").exists()

    def test_validate_production_config_debug_warning(self):
        """Test validation warns about DEBUG mode."""
        from src.core.config import Settings

        settings = Settings(debug=True)
        warnings = settings.validate_production_config()

        assert any("DEBUG" in w for w in warnings)

    def test_validate_production_config_api_key_warning(self):
        """Test validation warns about missing API key."""
        from src.core.config import Settings

        settings = Settings(api_key=None, debug=False)
        warnings = settings.validate_production_config()

        assert any("API_KEY" in w for w in warnings)

    def test_validate_production_config_placeholder_warning(self):
        """Test validation warns about placeholder API key."""
        from src.core.config import Settings

        settings = Settings(api_key="your-secret-api-key-here", debug=False)
        warnings = settings.validate_production_config()

        assert any("API_KEY" in w for w in warnings)

    def test_validate_production_config_cors_warning(self):
        """Test validation warns about missing CORS origins."""
        from src.core.config import Settings

        settings = Settings(cors_origins=[], debug=False)
        warnings = settings.validate_production_config()

        assert any("CORS" in w for w in warnings)

    def test_validate_production_config_no_cors_warning_in_debug(self):
        """Test CORS warning is suppressed in debug mode."""
        from src.core.config import Settings

        settings = Settings(cors_origins=[], debug=True)
        warnings = settings.validate_production_config()

        # Should not warn about CORS in debug mode
        cors_warnings = [w for w in warnings if "CORS" in w]
        assert len(cors_warnings) == 0

    def test_validate_production_config_large_model_warning(self):
        """Test validation warns about large Whisper models."""
        from src.core.config import Settings

        settings = Settings(whisper_model="large")
        warnings = settings.validate_production_config()

        assert any("Whisper" in w and "large" in w for w in warnings)

    def test_validate_production_config_high_concurrency_warning(self):
        """Test validation warns about high concurrent tasks."""
        from src.core.config import Settings

        settings = Settings(max_concurrent_tasks=10)
        warnings = settings.validate_production_config()

        assert any("MAX_CONCURRENT_TASKS" in w for w in warnings)

    def test_validate_production_config_passes_with_good_config(self):
        """Test validation passes with proper production config."""
        from src.core.config import Settings

        settings = Settings(
            debug=False,
            api_key="strong-production-api-key-32chars",
            cors_origins=["https://example.com"],
            whisper_model="base",
            max_concurrent_tasks=2,
        )
        warnings = settings.validate_production_config()

        # Should have no critical warnings
        critical_warnings = [w for w in warnings if "⚠️" in w or "❌" in w]
        assert len(critical_warnings) == 0
