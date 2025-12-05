"""
Pytest configuration and shared fixtures.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient


@pytest.fixture(scope="session")
def test_config():
    """Set up test configuration environment variables."""
    os.environ["DEBUG"] = "true"
    os.environ["API_KEY"] = "test-api-key-12345"
    os.environ["DATA_DIR"] = "./data/test"
    os.environ["TEMP_DIR"] = "./data/test/temp"
    os.environ["LOG_DIR"] = "./log/test"
    yield
    # Cleanup is optional since these are test directories


@pytest.fixture
def app(test_config):
    """Create FastAPI app instance for testing."""
    # Import here to ensure test config is applied first
    from src.api.main import create_app

    return create_app()


@pytest.fixture
def client(app):
    """Create synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def api_headers():
    """Common API headers with authentication."""
    return {
        "X-API-Key": "test-api-key-12345",
        "X-User-Id": "test-user-001",
        "Content-Type": "application/json",
    }


@pytest.fixture
def sample_video_url():
    """Sample YouTube video URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_task_request():
    """Sample task creation request."""
    return {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "source_id": "cnn10",
        "processing_mode": "subtitles_only",
    }
