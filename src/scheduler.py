"""
scheduler.py v1.3.0

This script is responsible for scheduling and automating the video checking and downloading tasks. 
It ensures that these tasks are executed at specified intervals, enabling the automatic and timely downloading of new videos.
"""

import os
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, JobEvent

from utils import sanitize_filename  
from video_downloader import main as video_downloader_main
from notifier import Notifier
from config_loader import load_config

# Setup logger
logger = logging.getLogger('scheduler')
config = load_config()

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
    - None
    
    Returns:
    - argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Schedule the video downloader job.")
    parser.add_argument('--test', action='store_true', help="Run the job immediately for testing.")
    return parser.parse_args()

def listener(event: JobEvent) -> None:
    """Handles scheduler job events.

    Args:
    - event (apscheduler.events.JobEvent): The event triggered by the scheduler.

    Returns:
    - None
    """
    if event.exception:
        logger.error(f"Scheduler job crashed with exception: {event.exception}")
    else:
        logger.info("Scheduler job completed successfully.")

def job() -> None:
    """Executes the video download job and sends notifications if videos were downloaded.

    Args:
    - None
    
    Returns:
    - None
    """
    start_time = datetime.now()
    logger.info(f"Starting scheduled video download at {start_time}")
    
    downloaded_titles = video_downloader_main()
    
    if downloaded_titles:
        notifier = Notifier()
        downloaded_video_paths = [os.path.join(config["VIDEO_DIRECTORY"], sanitize_filename(title) + config["VIDEO_EXTENSION"]) 
                                 for title in downloaded_titles]
        notifier.send_notification(downloaded_video_paths)
    
    end_time = datetime.now()
    logger.info(f"Finished downloading {len(downloaded_titles)} videos at {end_time}")

def next_run_time() -> datetime:
    """Determines the next run time based on the current time and configured run hours.

    Args:
    - None
    
    Returns:
    - datetime: The next run time.
    """
    now = datetime.now()
    morning_run = now.replace(hour=config["MORNING_RUN_HOUR"], minute=config["MORNING_RUN_MINUTE"], second=0)
    evening_run = now.replace(hour=config["EVENING_RUN_HOUR"], minute=config["EVENING_RUN_MINUTE"], second=0)
    
    if now < morning_run:
        return morning_run
    elif now < evening_run:
        return evening_run
    else:
        return morning_run + timedelta(days=1)

if __name__ == "__main__":
    """
    Usage:
    1. To run a test job immediately, use the --test flag:
        python scheduler.py --test

    2. To start the scheduler normally without the --test flag:
        python scheduler.py

    The --test flag allows for a one-time immediate execution of the video download job for testing purposes. 
    Without the --test flag, the scheduler will start and run the video download job at the specified intervals.
    """
    args = parse_arguments()

    if args.test:
        logger.info("Starting test run...")
        job()
        logger.info("Test run completed.")
    else:
        scheduler = BlockingScheduler()
        scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        scheduler.add_job(job, 'interval', hours=12, next_run_time=next_run_time())
        logger.info("Scheduler started...")
        scheduler.start()
