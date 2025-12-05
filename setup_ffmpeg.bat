@echo off
REM Temporary FFmpeg PATH setup for CNN Video Timer

echo Setting up FFmpeg PATH...
set PATH=C:\tools\ffmpeg\bin;%PATH%

echo Testing FFmpeg...
ffmpeg -version

if errorlevel 1 (
    echo.
    echo ERROR: FFmpeg not found at C:\tools\ffmpeg\bin
    echo Please check your FFmpeg installation path.
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS: FFmpeg is ready!
echo.
echo You can now:
echo   1. Run tests: python test_api.py
echo   2. Start server: python server.py
echo.
pause
