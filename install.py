#!/usr/bin/env python3
"""
YT-Nara One-Command Installer
Run this after: git clone
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a single package"""
    # Try normal pip first
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package, "--quiet"
        ])
        return True
    except subprocess.CalledProcessError:
        # Try with --user flag
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--user", "--quiet"
            ])
            return True
        except subprocess.CalledProcessError:
            # Try with --break-system-packages (for externally managed environments)
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--break-system-packages", "--quiet"
                ])
                return True
            except subprocess.CalledProcessError:
                return False

def main():
    print("🚀 YT-Nara Installer")
    print("=" * 30)
    
    # Required packages
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
    
    print("📦 Installing dependencies...")
    
    # Detect if we're in an externally managed environment
    externally_managed = False
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--help"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        externally_managed = True
    
    if externally_managed:
        print("⚠️ Detected externally managed environment, using alternative installation methods...")
    
    # Try different installation methods
    install_methods = [
        (["--quiet"], "normal pip"),
        (["--user", "--quiet"], "user installation"),
        (["--break-system-packages", "--quiet"], "system override")
    ]
    
    installed = False
    for flags, method_name in install_methods:
        try:
            print(f"   Trying {method_name}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + packages + flags)
            print("✅ All dependencies installed successfully")
            installed = True
            break
        except subprocess.CalledProcessError:
            continue
    
    if not installed:
        print("⚠️ Batch install failed, trying individual packages...")
        
        failed_packages = []
        for package in packages:
            print(f"   Installing {package.split('>=')[0]}...", end=" ")
            if install_package(package):
                print("✅")
            else:
                print("❌")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n❌ Failed to install: {', '.join(p.split('>=')[0] for p in failed_packages)}")
            print("💡 Try installing them manually:")
            for package in failed_packages:
                print(f"   pip install {package}")
            return False
        else:
            print("✅ All dependencies installed")
    
    print("\n🧪 Testing installation...")
    
    # Test imports
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
    
    failed_imports = []
    for name, module in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n❌ Import test failed for: {', '.join(failed_imports)}")
        return False
    
    print("\n🎉 Installation Complete!")
    print("=" * 30)
    print("✅ YT-Nara is ready to use!")
    print("\n🚀 Quick Start:")
    print("   python3 yt_nara.py")
    print("\n📖 Help:")
    print("   python3 yt_nara.py --help")
    print("\n⚡ Example:")
    print('   python3 yt_nara.py --topic "one piece" --cycles 2')
    print("\n💡 Note: The script will auto-create directories and config files")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation failed!")
            print("💡 Try: pip install -r requirements.txt")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)