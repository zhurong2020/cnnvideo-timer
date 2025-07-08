# CNN Video Timer
CNN Video Timer is a tool designed for scheduling the checking and downloading of videos from CNN, with automated link extraction, video downloading, and timed task execution, complemented by email notifications upon download completion.

## Feature Introduction
CNN Video Timer is a tool for scheduling the checking and downloading of CNN videos. It can automatically extract the links of CNN10 English news YouTube videos, download the videos, and can be configured to execute these tasks at scheduled times. Upon the completion of downloads, it can send notifications via email.

This project is planned for refactoring to implement more features, and a link to the new project will be published shortly.

## File Structure

The project now follows a more organized structure:

-   `.gitignore`: Excludes files including logs, metadata, downloaded videos, local configurations, keys, temporary files, virtual environment, etc.
-   `config/`: Contains configuration files.
    -   `configenv`: Reference configuration file, needs to be renamed to `config.env` and set with the respective parameters.
-   `docs/`: Contains all project documentation.
    -   `CHANGELOG.md`: Version update records for each module.
    -   `FAQ.md`: Frequently Asked Questions, especially for Linux installation issues.
    -   `LICENSE.md`: MIT License details.
    -   `README.md`: This documentation.
    -   `README_CN.md`: Chinese version of the README.
-   `scripts/`: Contains deployment and build scripts.
    -   `deploy.sh`: One-click installation script for Linux Ubuntu, used for automatic project deployment.
    -   `install.bat`: Installation script for Windows users.
    -   `build.bat`: Packaging module for administrators.
-   `src/`: Contains all Python source code.
    -   `baidu_cloud_uploader.py`: Baidu Cloud upload module.
    -   `config_loader.py`: Configuration loading module.
    -   `downloader_checker.py`: Download checker module.
    -   `link_extractor.py`: Link extraction module.
    -   `metadata_manager.py`: Metadata management module.
    -   `notifier.py`: Notification module.
    -   `scheduler.py`: Scheduler module.
    -   `utils.py`: Utility module.
    -   `video_downloader.py`: Video downloader module.
    -   `youtube_metadata_checker.py`: YouTube metadata checker module.
-   `venv/`: Python virtual environment (ignored by Git).
-   `requirements.txt`: Project dependencies.
-   `bin/`: Houses third-party tools, currently `ffmpeg.exe`, `ffprobe.exe` and `ffplay.exe`.
-   `log/`: Holds log files, log filename is `video_downloader.log`.
-   `metadata/`: Holds metadata information for downloaded videos, metadata filename is `metadata.json`.
-   `videos/`: Holds downloaded video files, videos are organized by date.

## Update Log
Please refer to the `docs/CHANGELOG.md` file for a detailed update log.

## Dependencies
-   Python 3
-   FFmpeg, please download `ffmpeg.exe` and place it in the `bin` subdirectory of this project, download link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
-   Other Python libraries: `apscheduler`, `python-dotenv`, `requests`, `yt_dlp`, for specific version numbers please refer to `requirements.txt` file.

## How to Use
### Windows
#### Method One (Recommended)
1.  Download directly from https://github.com/znhskzj/cnnvideo-timer/releases/download/v0.9.1/cnn10vd_setup.exe.
2.  Run the exe file downloaded to your local machine, and follow the steps to complete the installation. This will create a program group in the Start menu and a desktop icon (if selected).

#### Method Two
1.  Download directly: https://github.com/znhskzj/cnnvideo-timer/releases/download/v0.9.1/releaseffmpeg.zip.
2.  Create a new directory locally, and extract the above file.
3.  Execute the `scripts/install.bat` script (for Windows 10 or above users, if below Windows 10, you'll need to install extraction software manually and refer to Method 3 below).

#### Method Three
1.  In the repository at https://github.com/zhurong2020/cnnvideo-timer, download the latest version from the release page.
2.  If you haven't downloaded `ffmpeg.exe` before, please download `releaseffmpeg.zip`.
3.  Extract to a separate working directory, create a `bin` subdirectory, place the `ffmpeg.exe` in this subdirectory, and add this directory to the system environment path.
4.  Rename `config/configenv` to `config/config.env`.
5.  Execute the `cnn10vd.exe` file, the video files will be downloaded to the `video` subdirectory in the current directory.

#### Programmers
1.  Please go to https://github.com/zhurong2020/cnnvideo-timer to download the source code.
2.  Rename `config/configenv` to `config/config.env` and configure the parameters.
3.  **Set up a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  Various fancy usages include real-time downloading, scheduled downloading, downloading multiple videos, switching to other news channels for downloading, changing download file specifications, viewing YouTube video metadata, uploading to Baidu Cloud Disk, etc.
5.  To run the scheduler: `python src/scheduler.py`
6.  Stars, forks, and PRs are welcomed.

### Mac and Linux
1.  Ensure Python is installed.
2.  Run the following command for one-click automatic project deployment (Ubuntu and Debian):

    ```bash
    curl -sSL https://raw.githubusercontent.com/zhurong2020/cnnvideo-timer/main/scripts/deploy.sh | bash
    ```

    For manual deployment, ensure the `scripts/deploy.sh` script has execution permissions. Use the following commands to check and set:
    ```bash
    chmod +x scripts/deploy.sh
    ```

## Common Questions
For installation issues on Linux, please refer to the `docs/FAQ.md` document.

## Contribution
If you have any questions or suggestions, or wish to contribute to the project, you can contact us via email or raise an Issue or Pull Request in the project.

## License
This project is licensed under the MIT License - see the `docs/LICENSE.md` file for details.

## Risk Warning
When using this tool and downloading videos, please comply with relevant laws and regulations, as well as the terms and conditions of the video creators, and respect copyrights.

## Contact Information
For any questions or suggestions, please email: admin@zhurong.link