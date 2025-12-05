#!/usr/bin/env python3
"""
CNN Video Timer - Main Entry Point

A tool for scheduling and downloading videos from news channels like CNN10.

Usage:
    python main.py                  # Run immediate download
    python main.py --schedule       # Start scheduler for periodic downloads
    python main.py --help           # Show help message
"""

import argparse
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video_downloader import main as download_videos
from scheduler import job, next_run_time
from config_loader import load_config
from utils import setup_logging, create_directories


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="CNN Video Timer - Download videos from news channels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    Download latest videos immediately
  python main.py --schedule         Start scheduled downloads (morning & evening)
  python main.py --max-videos 3     Download up to 3 videos
  python main.py --channel URL      Download from a specific YouTube channel
        """
    )

    parser.add_argument(
        '--schedule', '-s',
        action='store_true',
        help='Start the scheduler for periodic downloads'
    )

    parser.add_argument(
        '--max-videos', '-n',
        type=int,
        default=None,
        help='Maximum number of videos to download (default: from config)'
    )

    parser.add_argument(
        '--channel', '-c',
        type=str,
        default=None,
        help='YouTube channel URL to download from (default: CNN10)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output directory for downloaded videos'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='CNN Video Timer v2.0.0'
    )

    return parser.parse_args()


def run_download(args):
    """Run immediate video download."""
    print("=" * 50)
    print("CNN Video Timer - Starting Download")
    print("=" * 50)

    # Check config file exists
    if not os.path.exists('config/config.env'):
        print("\nError: config/config.env not found!")
        print("Please copy config/configenv to config/config.env and configure it.")
        sys.exit(1)

    # Setup
    setup_logging()
    create_directories()

    # Load config and apply overrides
    config = load_config()

    if args.channel:
        os.environ['YOUTUBE_URL'] = args.channel
        print(f"Using channel: {args.channel}")

    if args.max_videos:
        os.environ['MAX_VIDEOS_TO_DOWNLOAD'] = str(args.max_videos)
        print(f"Max videos: {args.max_videos}")

    if args.output:
        os.environ['DOWNLOAD_PATH'] = args.output
        print(f"Output directory: {args.output}")

    print()

    # Run download
    downloaded = download_videos()

    print()
    print("=" * 50)
    if downloaded:
        print(f"Successfully downloaded {len(downloaded)} video(s):")
        for title in downloaded:
            print(f"  - {title}")
    else:
        print("No new videos to download.")
    print("=" * 50)

    return downloaded


def run_scheduler():
    """Start the scheduler for periodic downloads."""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    from scheduler import listener

    print("=" * 50)
    print("CNN Video Timer - Scheduler Mode")
    print("=" * 50)

    # Check config file exists
    if not os.path.exists('config/config.env'):
        print("\nError: config/config.env not found!")
        print("Please copy config/configenv to config/config.env and configure it.")
        sys.exit(1)

    config = load_config()

    next_time = next_run_time()
    print(f"\nScheduler started!")
    print(f"Next run time: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Morning run: {config['MORNING_RUN_HOUR']:02d}:{config['MORNING_RUN_MINUTE']:02d}")
    print(f"Evening run: {config['EVENING_RUN_HOUR']:02d}:{config['EVENING_RUN_MINUTE']:02d}")
    print("\nPress Ctrl+C to stop the scheduler.")
    print("=" * 50)

    scheduler = BlockingScheduler()
    scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.add_job(job, 'interval', hours=12, next_run_time=next_time)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
        scheduler.shutdown()


def main():
    """Main entry point."""
    args = parse_args()

    if args.schedule:
        run_scheduler()
    else:
        run_download(args)


if __name__ == "__main__":
    main()
