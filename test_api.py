#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple API test script.

Test the CNN Video Timer API without running full server.
"""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from pathlib import Path


def test_config():
    """Test configuration loading."""
    print("=" * 60)
    print("Testing Configuration...")
    print("=" * 60)

    from src.core.config import get_settings

    settings = get_settings()
    print(f"✓ App Name: {settings.app_name}")
    print(f"✓ Version: {settings.app_version}")
    print(f"✓ API Port: {settings.api_port}")
    print(f"✓ Temp Dir: {settings.temp_dir}")
    print(f"✓ Whisper Model: {settings.whisper_model}")
    print()


def test_video_sources():
    """Test video source adapters."""
    print("=" * 60)
    print("Testing Video Sources...")
    print("=" * 60)

    from src.sources.youtube import get_all_sources

    sources = get_all_sources()
    print(f"✓ Found {len(sources)} video sources:")
    for source in sources:
        print(f"  - {source.info.name} ({source.info.id})")
        print(f"    URL: {source.info.url}")
        print(f"    Tier: {source.info.min_tier.value}")
    print()


async def test_get_videos():
    """Test getting latest videos from a source."""
    print("=" * 60)
    print("Testing Video Retrieval...")
    print("=" * 60)

    from src.sources.youtube import CNN10Source

    source = CNN10Source()
    print(f"Getting latest videos from {source.info.name}...")

    try:
        videos = await source.get_latest_videos(limit=3)
        print(f"✓ Found {len(videos)} videos:")
        for i, video in enumerate(videos, 1):
            print(f"  {i}. {video.title}")
            print(f"     ID: {video.id}")
            print(f"     URL: {video.url}")
    except Exception as e:
        print(f"✗ Failed to get videos: {e}")
    print()


def test_downloader():
    """Test video downloader (info only, no actual download)."""
    print("=" * 60)
    print("Testing Video Downloader...")
    print("=" * 60)

    from src.core.downloader import VideoDownloader

    downloader = VideoDownloader()
    print("✓ Downloader initialized")
    print(f"  Output dir: {downloader.output_dir}")
    print(f"  Max resolution: {downloader.max_resolution}")
    print()


def test_task_manager():
    """Test task manager."""
    print("=" * 60)
    print("Testing Task Manager...")
    print("=" * 60)

    from src.core.task_manager import get_task_manager, ProcessingMode

    manager = get_task_manager()
    print("✓ Task manager initialized")
    print(f"  Database: {manager.db_path}")

    # Create a test task
    task = manager.create_task(
        user_id="test_user",
        source_id="cnn10",
        video_id="test123",
        video_url="https://youtube.com/watch?v=test123",
        video_title="Test Video",
        processing_mode=ProcessingMode.WITH_SUBTITLE,
    )
    print(f"✓ Created test task: {task.id}")

    # Get task
    retrieved = manager.get_task(task.id)
    print(f"✓ Retrieved task: {retrieved.video_title}")

    # Delete task
    manager.delete_task(task.id)
    print(f"✓ Deleted test task")
    print()


def test_ffmpeg():
    """Test FFmpeg availability."""
    print("=" * 60)
    print("Testing FFmpeg...")
    print("=" * 60)

    from src.core.config import get_settings
    from src.processors.ffmpeg import check_ffmpeg_installed

    settings = get_settings()
    ffmpeg_path = settings.ffmpeg_path

    if ffmpeg_path:
        print(f"  Using FFmpeg from config: {ffmpeg_path}")
    else:
        print("  Using FFmpeg from system PATH")

    if check_ffmpeg_installed(ffmpeg_path):
        print("✓ FFmpeg is installed and available")
    else:
        print("✗ FFmpeg not found!")
        print("  Please install FFmpeg:")
        print("  - Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("  - Linux: sudo apt install ffmpeg")
        print("  - Mac: brew install ffmpeg")
    print()


def test_whisper():
    """Test Whisper availability."""
    print("=" * 60)
    print("Testing Whisper...")
    print("=" * 60)

    try:
        import faster_whisper
        print("✓ faster-whisper is installed")
        print(f"  Version: {faster_whisper.__version__}")
    except ImportError:
        print("⚠ faster-whisper not installed (optional)")
        print("  Install with: pip install faster-whisper")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SmartNews Learn - API Tests" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        # Synchronous tests
        test_config()
        test_video_sources()
        test_downloader()
        test_task_manager()
        test_ffmpeg()
        test_whisper()

        # Async tests
        print("Running async tests...")
        asyncio.run(test_get_videos())

        print("=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Start API server: python server.py")
        print("  2. Open browser: http://localhost:8000/docs")
        print("  3. Try creating a task in the API docs")
        print()

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
