@echo off
:: install.bat version 1.0.0
:: This script performs the following steps:
:: 1. Creates a bin directory in the current directory.
:: 2. Moves ffmpeg.exe to the bin directory.
:: 3. Adds the bin directory to the system PATH.
:: 4. Informs the user that they can now run cnn10vd.exe to download videos.

setlocal

:: Step 1: Create the bin directory
echo Creating bin directory...
md bin

:: Check if the bin directory was created successfully
if errorlevel 1 (
    echo Failed to create bin directory. Aborting.
    exit /b 1
)

:: Step 2: Move ffmpeg.exe to the bin directory
echo Moving ffmpeg.exe to bin directory...
move ffmpeg.exe bin

:: Check if ffmpeg.exe was moved successfully
if errorlevel 1 (
    echo Failed to move ffmpeg.exe. Aborting.
    exit /b 1
)

:: Step 3: Add the bin directory to the system PATH
echo Adding bin directory to system PATH...
setx PATH "%PATH%;%CD%\bin"

:: Check if the PATH was updated successfully
if errorlevel 1 (
    echo Failed to update system PATH. Aborting.
    exit /b 1
)

:: Step 4: Rename configenv to config.env
echo Renaming configenv to config.env...
rename configenv config.env

:: Check if configenv was renamed successfully
if errorlevel 1 (
    echo Failed to rename configenv. Aborting.
    exit /b 1
)

:: Step 5: Inform the user
echo Installation completed successfully.
echo You can now run cnn10vd.exe to download videos.

pause
endlocal