#!/usr/bin/env python3
"""
Super Simple YT-Nara Setup - One Command After Git Clone
"""

import subprocess
import sys
from pathlib import Path
import json

def main():
    print("🚀 YT-Nara Simple Setup")
    print("=" * 30)
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "aiohttp>=3.9.0", "selenium>=4.15.0", "moviepy>=1.0.3", 
            "yt-dlp>=2023.12.30", "rich>=13.7.0", "colorama>=0.4.6", 
            "pyfiglet>=1.0.2", "Pillow>=10.1.0", "imageio-ffmpeg>=0.4.9",
            "--quiet"
        ])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Create directories
    print("📁 Creating directories...")
    directories = ['downloads', 'edited_videos', 'data', 'logs', 'sessions', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")
    
    # Create config files
    print("⚙️ Creating config files...")
    
    config = {
        "app": {"name": "YT-Nara", "version": "1.0.0"},
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
    
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
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
    
    print("✅ Config files created")
    
    # Test installation
    print("🧪 Testing installation...")
    try:
        import aiohttp
        import selenium
        import moviepy
        import yt_dlp
        from rich.console import Console
        print("✅ All dependencies working")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("✅ YT-Nara is ready to use!")
    print("\n🚀 Quick Start:")
    print("   python3 yt_nara.py")
    print("\n📖 Help:")
    print("   python3 yt_nara.py --help")
    print("\n⚡ Example:")
    print('   python3 yt_nara.py --topic "one piece" --cycles 2')
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed! Try installing dependencies manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)