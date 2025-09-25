#!/usr/bin/env python3
"""
Quick fix to create necessary directories and install dependencies
"""

from pathlib import Path
import json
import subprocess
import sys

print("🔧 Quick Fix for YT-Nara")
print("=" * 30)

print("📦 Installing dependencies...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
    print("✅ Dependencies installed")
except subprocess.CalledProcessError:
    print("❌ Failed to install dependencies")
    print("💡 Try manually: pip install -r requirements.txt")

print("📁 Creating necessary directories...")

# Create all required directories
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

# Create basic config files
print("📝 Creating config files...")

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
print("🎉 Quick fix complete! Now try: python yt_nara.py")