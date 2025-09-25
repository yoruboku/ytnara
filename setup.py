#!/usr/bin/env python3
"""
YT-Nara Setup Script - Works in any environment
"""

import subprocess
import sys
import os
from pathlib import Path
import json

def print_banner():
    print("🚀 YT-Nara Setup")
    print("=" * 30)

def detect_environment():
    """Detect the type of Python environment"""
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    # Check if system has externally managed Python
    externally_managed = False
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--dry-run", "requests"
        ], capture_output=True, text=True)
        if "externally-managed-environment" in result.stderr:
            externally_managed = True
    except:
        pass
    
    return in_venv, externally_managed

def install_dependencies():
    """Install dependencies with appropriate method"""
    packages = [
        "aiohttp>=3.9.0",
        "selenium>=4.15.0", 
        "moviepy>=1.0.3",
        "yt-dlp>=2023.12.30",
        "rich>=13.7.0",
        "colorama>=0.4.6",
        "pyfiglet>=1.0.2",
        "Pillow>=10.1.0",
        "imageio-ffmpeg>=0.4.9"
    ]
    
    in_venv, externally_managed = detect_environment()
    
    print("📦 Installing dependencies...")
    
    if in_venv:
        print("✅ Virtual environment detected - using normal pip")
        cmd = [sys.executable, "-m", "pip", "install"] + packages
    elif externally_managed:
        print("⚠️ Externally managed environment detected")
        print("   Trying user installation...")
        cmd = [sys.executable, "-m", "pip", "install", "--user"] + packages
    else:
        print("🔧 Using standard pip installation")
        cmd = [sys.executable, "-m", "pip", "install"] + packages
    
    try:
        subprocess.check_call(cmd + ["--quiet"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        if not in_venv and externally_managed:
            print("   User installation failed, trying system override...")
            try:
                cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages"] + packages
                subprocess.check_call(cmd + ["--quiet"])
                print("✅ Dependencies installed with system override")
                return True
            except subprocess.CalledProcessError:
                pass
        
        print("❌ Automatic installation failed")
        print("\n💡 Manual installation options:")
        print("   Option 1 (Recommended): Create virtual environment")
        print("     python3 -m venv myenv")
        print("     source myenv/bin/activate  # On Windows: myenv\\Scripts\\activate")
        print("     pip install -r requirements.txt")
        print()
        print("   Option 2: User installation")
        print("     pip install --user -r requirements.txt")
        print()
        print("   Option 3: System override (if you understand the risks)")
        print("     pip install --break-system-packages -r requirements.txt")
        
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ['logs', 'downloads', 'edited_videos', 'data', 'sessions', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def create_config_files():
    """Create configuration files"""
    print("⚙️ Creating config files...")
    
    # Config file
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
    
    # Accounts file
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

def test_installation():
    """Test if everything works"""
    print("🧪 Testing installation...")
    
    test_imports = [
        ("aiohttp", "aiohttp"),
        ("selenium", "selenium"),
        ("moviepy", "moviepy.editor"),
        ("yt-dlp", "yt_dlp"),
        ("rich", "rich.console"),
        ("colorama", "colorama"),
        ("pyfiglet", "pyfiglet"),
        ("Pillow", "PIL")
    ]
    
    failed = []
    for name, module in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name} - {str(e)}")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️ Failed imports: {', '.join(failed)}")
        print("💡 This might be normal in some environments. Try running the main script:")
        print("   python3 yt_nara.py --help")
        return False
    
    return True

def main():
    print_banner()
    
    # Create directories and config files first (these always work)
    create_directories()
    create_config_files()
    
    # Try to install dependencies
    if not install_dependencies():
        print("\n⚠️ Dependencies not installed automatically")
        print("📋 Next steps:")
        print("1. Install dependencies using one of the manual methods above")
        print("2. Then run: python3 yt_nara.py")
        return False
    
    # Test installation
    if not test_installation():
        print("\n❌ Some dependencies failed to import")
        print("💡 Try the manual installation methods shown above")
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
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try manual installation: pip install -r requirements.txt")
        sys.exit(1)