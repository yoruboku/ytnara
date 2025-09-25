#!/usr/bin/env python3
"""
YT-Nara Quick Start Script
One-command setup and run for YT-Nara
"""

import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(command, description):
    """Run a command and show progress"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False

def quick_setup():
    """Quick setup for YT-Nara"""
    print("🚀 YT-Nara Quick Start")
    print("=" * 30)
    
    # Check if already set up
    if Path("data/config.json").exists() and Path("data/accounts.json").exists():
        print("✅ YT-Nara appears to be already set up")
        return True
    
    print("📦 Setting up YT-Nara...")
    
    # Install dependencies
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installing dependencies"):
        return False
    
    # Create directories
    directories = ['downloads', 'edited_videos', 'data', 'logs', 'sessions', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created directories")
    
    # Create basic config files
    import json
    
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
    
    print("✅ Created configuration files")
    print("✅ Setup complete!")
    
    return True

async def run_simple_example():
    """Run a simple example"""
    print("\n🎬 Running simple example...")
    
    try:
        # Import and run YT-Nara
        from yt_nara import YTNara
        
        yt_nara = YTNara()
        
        # Run with simple parameters
        topic = "anime memes"
        cycles = 1
        daily_frequency = None  # Run immediately
        
        print(f"📝 Topic: {topic}")
        print(f"🔄 Cycles: {cycles}")
        print(f"⏰ Mode: Immediate execution")
        
        await yt_nara.run_automation(topic, cycles, daily_frequency)
        
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running example: {str(e)}")
        print("💡 Try running the full setup first: python3 yt_nara.py --setup")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup":
            if quick_setup():
                print("\n🎉 Setup complete! Now run: python3 yt_nara.py")
            else:
                print("\n❌ Setup failed. Check errors above.")
                return 1
        elif sys.argv[1] == "--test":
            print("🧪 Running quick test...")
            try:
                from test_installation import main as test_main
                return test_main()
            except ImportError:
                print("❌ Test script not found")
                return 1
        elif sys.argv[1] == "--example":
            if quick_setup():
                asyncio.run(run_simple_example())
            else:
                print("❌ Setup failed")
                return 1
        else:
            print("Usage: python3 quick_start.py [--setup|--test|--example]")
            return 1
    else:
        print("🚀 YT-Nara Quick Start")
        print("=" * 30)
        print("Choose an option:")
        print("1. Setup YT-Nara")
        print("2. Run test")
        print("3. Run example")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            if quick_setup():
                print("\n🎉 Setup complete! Now run: python3 yt_nara.py")
            else:
                print("\n❌ Setup failed. Check errors above.")
                return 1
        elif choice == "2":
            try:
                from test_installation import main as test_main
                return test_main()
            except ImportError:
                print("❌ Test script not found")
                return 1
        elif choice == "3":
            if quick_setup():
                asyncio.run(run_simple_example())
            else:
                print("❌ Setup failed")
                return 1
        elif choice == "4":
            print("👋 Goodbye!")
            return 0
        else:
            print("❌ Invalid choice")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())