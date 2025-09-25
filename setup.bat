@echo off
REM YT-Nara One-Command Setup Script for Windows
REM Run this after: git clone <repo>

echo 🚀 Setting up YT-Nara - Universal Content Automation Tool
echo ==================================================

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed
    echo ℹ️ Please install Python 3.8+ from: https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Install/upgrade pip
echo ℹ️ Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo ℹ️ Installing Python dependencies (this may take a few minutes)...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo ℹ️ Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create directories
echo ℹ️ Creating directories...
mkdir downloads 2>nul
mkdir edited_videos 2>nul
mkdir data 2>nul
mkdir logs 2>nul
mkdir sessions 2>nul
mkdir temp 2>nul
echo ✅ Directories created

REM Create config files
echo ℹ️ Creating configuration files...
python -c "import json; from pathlib import Path; Path('data').mkdir(exist_ok=True); json.dump({'app': {'name': 'YT-Nara', 'version': '1.0.0'}, 'video_processing': {'max_video_duration': 60, 'watermark_text': 'YT-Nara', 'watermark_position': 'bottom_right'}, 'upload': {'max_retries': 3, 'upload_delay_min': 30, 'upload_delay_max': 60}}, open('data/config.json', 'w'), indent=2); json.dump({'youtube': [{'name': 'account1', 'logged_in': False}, {'name': 'account2', 'logged_in': False}], 'instagram': [{'name': 'account1', 'logged_in': False}, {'name': 'account2', 'logged_in': False}]}, open('data/accounts.json', 'w'), indent=2); print('Config files created')"

echo ✅ Configuration files created

REM Test installation
echo ℹ️ Testing installation...
python -c "import aiohttp, selenium, moviepy, yt_dlp; from rich.console import Console; from modules.config import Config; print('✅ All modules working')" 2>nul
if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

echo ✅ Installation test passed

REM Check for Chrome
where chrome >nul 2>&1
if not errorlevel 1 (
    echo ✅ Chrome browser found
) else (
    echo ⚠️ Chrome browser not found
    echo ℹ️ Install Chrome for full functionality: https://google.com/chrome
)

REM Check for FFmpeg
where ffmpeg >nul 2>&1
if not errorlevel 1 (
    echo ✅ FFmpeg found
) else (
    echo ⚠️ FFmpeg not found
    echo ℹ️ Install FFmpeg for video processing: https://ffmpeg.org
)

echo.
echo 🎉 YT-Nara Setup Complete!
echo ==========================
echo.
echo 📋 Quick Start:
echo    python yt_nara.py
echo.
echo 📖 Help:
echo    python yt_nara.py --help
echo.
echo ⚡ Example Usage:
echo    python yt_nara.py --topic "one piece" --cycles 2
echo.
echo 🔧 First Time Setup (for social accounts):
echo    python yt_nara.py --setup
echo.
echo 💡 Tips:
echo    - Start with small cycles (1-2) to test
echo    - Use popular topics for better results
echo    - Install Chrome and FFmpeg for full features
echo.
echo ✅ Ready to automate content creation! 🚀

pause