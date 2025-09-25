#!/usr/bin/env python3
"""
YT-Nara Installation Script
Automates the installation and setup process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, shell=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    if not success:
        print(f"⚠️ Warning: Could not upgrade pip: {stderr}")
    
    # Install requirements
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'downloads',
        'edited_videos',
        'data',
        'logs',
        'sessions',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")
    
    return True

def check_system_dependencies():
    """Check for system dependencies"""
    print("🔍 Checking system dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    else:
        print(f"✅ Python {sys.version.split()[0]}")
    
    # Check for Chrome/Chromium
    chrome_paths = [
        "google-chrome",
        "chromium-browser",
        "chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    chrome_found = False
    for chrome_path in chrome_paths:
        success, _, _ = run_command([chrome_path, "--version"], shell=True)
        if success:
            print("✅ Chrome browser found")
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️ Chrome browser not found - please install Google Chrome")
    
    # Check for FFmpeg
    success, stdout, _ = run_command(["ffmpeg", "-version"])
    if success:
        print("✅ FFmpeg found")
    else:
        print("⚠️ FFmpeg not found - video processing may not work")
        print("   Install FFmpeg from: https://ffmpeg.org/")
    
    return True

def create_config_files():
    """Create default configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Default config
    config = {
        "app": {
            "name": "YT-Nara",
            "version": "1.0.0",
            "debug": False
        },
        "video_processing": {
            "max_video_duration": 60,
            "watermark_text": "YT-Nara",
            "watermark_position": "bottom_right"
        },
        "upload": {
            "max_retries": 3,
            "upload_delay_min": 30,
            "upload_delay_max": 60
        }
    }
    
    import json
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Default accounts
    accounts = {
        "youtube": [
            {"name": "account1", "logged_in": False},
            {"name": "account2", "logged_in": False}
        ],
        "instagram": [
            {"name": "account1", "logged_in": False},
            {"name": "account2", "logged_in": False}
        ]
    }
    
    with open("data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    
    print("✅ Configuration files created")
    return True

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    try:
        # Test importing main modules
        import aiohttp
        import selenium
        import moviepy
        import yt_dlp
        from rich.console import Console
        
        print("✅ All dependencies working")
        
        # Test YT-Nara modules
        from modules.config import Config
        from modules.database import ContentDatabase
        
        print("✅ YT-Nara modules working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def show_next_steps():
    """Show next steps to user"""
    print("\n🎉 Installation Complete!")
    print("\n📋 Next Steps:")
    print("1. Run: python3 yt_nara.py --setup")
    print("   (This will help you set up your social media accounts)")
    print("\n2. Start using YT-Nara:")
    print("   python3 yt_nara.py")
    print("\n3. For help:")
    print("   python3 yt_nara.py --help")
    print("\n📖 Documentation:")
    print("   - README.md: Overview and usage")
    print("   - SETUP.md: Detailed setup guide")
    print("\n⚠️ Important:")
    print("   - Install Chrome browser if not already installed")
    print("   - Install FFmpeg for video processing")
    print("   - Have your social media accounts ready")

def main():
    """Main installation function"""
    print("🚀 YT-Nara Installation Script")
    print("=" * 40)
    
    # Check system
    if not check_system_dependencies():
        print("\n❌ System dependency check failed")
        return 1
    
    # Create directories
    if not create_directories():
        print("\n❌ Directory creation failed")
        return 1
    
    # Install Python dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        print("Try running manually: pip install -r requirements.txt")
        return 1
    
    # Create config files
    if not create_config_files():
        print("\n❌ Configuration file creation failed")
        return 1
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        return 1
    
    # Show next steps
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())