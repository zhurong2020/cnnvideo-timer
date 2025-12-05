#!/usr/bin/env python3
"""
SmartNews Learn - API Server Entry Point

Run with:
    python server.py
    # or
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
from src.api.main import app
from src.core.config import get_settings


def main():
    """Run the API server."""
    settings = get_settings()

    print("=" * 60)
    print("SmartNews Learn API Server")
    print("=" * 60)
    print(f"  Version:  {settings.app_version}")
    print(f"  Host:     {settings.api_host}")
    print(f"  Port:     {settings.api_port}")
    print(f"  Docs:     http://localhost:{settings.api_port}/docs")
    print("=" * 60)

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
