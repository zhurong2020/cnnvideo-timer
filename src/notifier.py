"""
notifier.py v1.4.2

This script is tasked with sending notification emails. It constructs and sends emails to notify users about the availability of new videos or any errors that might have occurred during the video checking or downloading processes.
"""

import smtplib
import logging
import os
import argparse
import sys
import datetime
from email.message import EmailMessage
from time import sleep
from random import randint
from typing import List
from config_loader import load_config

# Set up a logger for this module
logger = logging.getLogger('notifier')

class Notifier:

    def __init__(self) -> None:
        """Initialize the Notifier with configuration loaded from the environment file.

        Args:
        - None
        
        Returns:
        - None
        """
        self.config = load_config()
        self.retry_count = self.config.get("EMAIL_RETRY_COUNT", 3)  # Load retry count from config or use default
        self.recipients = [email.strip() for email in self.config["SMTP_RECEIVER"].split(',')]

    def send_notification(self, downloaded_videos: List[str]) -> None:
        """Send an email notification with the titles and sizes of downloaded videos.

        Args:
        - downloaded_videos (List[str]): A list of paths to the downloaded videos.
        
        Returns:
        - None
        """

        message_body = "The following videos have been downloaded:\n\n"
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        for video_path in downloaded_videos:
            video_filename = os.path.basename(video_path)
            video_size = os.path.getsize(video_path)  # Size in bytes
            video_size_mb = video_size / (1024 * 1024)  # Converting size to MB
            message_body += f"- {video_filename}, Size: {video_size_mb:.2f} MB\n"
        
        subject = f"New Videos Downloaded on {current_date}"
        self._send_email(subject, message_body)

    def _send_email(self, subject: str, body: str) -> None:
        """Send an email with the specified subject and body.

        Args:
        - subject (str): The subject of the email.
        - body (str): The body of the email.
        
        Returns:
        - None
        """
        message = EmailMessage()
        message.set_content(body)
        message['Subject'] = subject
        message['From'] = self.config["SMTP_SENDER"]
        message['To'] = self.recipients
        
        retries = 0
        while retries < self.retry_count:
            try:
                with smtplib.SMTP(self.config["SMTP_SERVER"], self.config["SMTP_PORT"]) as server:
                    server.starttls()
                    server.login(self.config["SMTP_USERNAME"], self.config["SMTP_PASSWORD"])
                    server.send_message(message)
                
                logger.info(f"Notification email sent successfully to {', '.join(self.recipients)}!")
                break  # Exit the loop if the email is sent successfully
                
            except smtplib.SMTPException as e:
                logger.error(f"Error sending notification email. Error: {e}. Retrying...")
                retries += 1
                sleep(randint(1, 5))  # Random sleep before retrying

# Usage example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a notification email with video filenames.")
    parser.add_argument('filenames', metavar='filename', type=str, nargs='*',
                        help='a filename to be included in the notification email')

    args = parser.parse_args()
    
    if not args.filenames:
        print("Error: Please provide at least one filename.")
        sys.exit(1)
    
    notifier = Notifier()
    notifier.send_notification(args.filenames)