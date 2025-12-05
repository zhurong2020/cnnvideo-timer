@echo off
REM SmartNews Learn - Installation Script for Windows

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     SmartNews Learn v2.0 - Installation Script           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed or not in PATH!
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✓ Python is installed
echo.

REM Check FFmpeg
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠ FFmpeg is not installed or not in PATH
    echo.
    echo   Please install FFmpeg:
    echo   1. Download from: https://www.gyan.dev/ffmpeg/builds/
    echo   2. Extract to a folder (e.g., C:\ffmpeg)
    echo   3. Add to PATH: C:\ffmpeg\bin
    echo.
    echo   Or use the bin folder in this project and add to PATH
    echo.
    pause
) else (
    echo ✓ FFmpeg is installed
)
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ✗ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ✗ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

REM Optional: Install Whisper
set /p INSTALL_WHISPER="Install faster-whisper for AI subtitle generation? (y/n): "
if /i "%INSTALL_WHISPER%"=="y" (
    echo Installing faster-whisper...
    pip install faster-whisper
    echo ✓ faster-whisper installed
) else (
    echo ⊘ Skipped faster-whisper installation
    echo   ^(You can install later with: pip install faster-whisper^)
)
echo.

REM Setup config
if not exist "config\config.env" (
    echo Setting up configuration...
    copy "config\config.env.example" "config\config.env"
    echo ✓ Configuration file created: config\config.env
    echo   Please edit this file with your settings
) else (
    echo ✓ Configuration file already exists
)
echo.

REM Create data directories
echo Creating data directories...
if not exist "data\temp" mkdir data\temp
if not exist "log" mkdir log
echo ✓ Data directories created
echo.

echo ═══════════════════════════════════════════════════════════
echo ✓ Installation completed successfully!
echo ═══════════════════════════════════════════════════════════
echo.
echo Next steps:
echo.
echo 1. Edit configuration (optional):
echo    notepad config\config.env
echo.
echo 2. Test installation:
echo    venv\Scripts\activate
echo    python test_api.py
echo.
echo 3. Start API server:
echo    python server.py
echo.
echo 4. Or use CLI:
echo    python main.py
echo.
echo For documentation, see:
echo   - README.md      - Full documentation
echo   - QUICKSTART.md  - Quick start guide
echo   - EXAMPLES.md    - Usage examples
echo.
echo API Documentation:
echo   http://localhost:8000/docs (after starting server)
echo.
pause
