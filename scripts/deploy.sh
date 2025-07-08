#!/bin/bash

# File: deploy.sh
# Version: 1.3.1
# Description: This script automates the deployment process of the cnnvideo-timer application.
# It clones the repository, sets up a virtual environment, installs necessary packages,
# sets the time zone, and schedules the application to run daily.

function check_commands {
    commands=("git" "python3" "pip3")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            echo "Error: $cmd could not be found, please install it."
            exit 1
        fi
    done
}

function clone_repository {
    if [ ! -d "cnnvideo-timer" ]; then
        git clone https://github.com/znhskzj/cnnvideo-timer.git
        if [ $? -ne 0 ]; then
            echo "Error: Failed to clone the repository."
            exit 1
        fi
    else
        echo "Directory cnnvideo-timer already exists. Skipping cloning."
    fi
}

function setup_virtual_environment {
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create a virtual environment."
            exit 1
        fi
    else
        echo "Virtual environment already exists. Skipping creation."
    fi
}

function install_dependencies {
    source venv/bin/activate
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install required packages."
        exit 1
    fi
}

function configure_timezone {
    timedatectl set-timezone America/New_York
    if [ $? -ne 0 ]; then
        echo "Error: Failed to set the time zone."
        exit 1
    fi
}

function schedule_cron_job {
    (crontab -l 2>/dev/null; echo "0 20 * * * cd $(pwd) && ./venv/bin/python3 src/scheduler.py >> cron.log 2>&1") | crontab -
    if [ $? -ne 0 ]; then
        echo "Error: Failed to update crontab."
        exit 1
    fi
}

# Main script execution
check_commands
clone_repository
cd cnnvideo-timer || exit
setup_virtual_environment
install_dependencies
configure_timezone
schedule_cron_job

echo "Deployment completed successfully."