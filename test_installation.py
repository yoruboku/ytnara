#!/usr/bin/env python3
"""
Quick installation test for YT-Nara
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("🐍 Testing Python version...")
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version.split()[0]} - OK")
        return True
    else:
        print(f"❌ Python {sys.version.split()[0]} - Need Python 3.8+")
        return False

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n📦 Testing dependencies...")
    
    dependencies = [
        'aiohttp',
        'selenium', 
        'moviepy',
        'yt_dlp',
        'rich',
        'colorama',
        'pyfiglet',
        'pandas',
        'numpy',
        'PIL'  # Pillow is imported as PIL
    ]
    
    failed = []
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Not installed")
            failed.append(dep)
    
    return len(failed) == 0

def test_yt_nara_modules():
    """Test YT-Nara modules"""
    print("\n🔧 Testing YT-Nara modules...")
    
    modules = [
        'modules.models',
        'modules.config',
        'modules.database', 
        'modules.wikipedia_research',
        'modules.content_discovery',
        'modules.content_verification',
        'modules.video_processor',
        'modules.upload_manager',
        'modules.scheduler',
        'modules.ui'
    ]
    
    failed = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {str(e)}")
            failed.append(module)
    
    return len(failed) == 0

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directories...")
    
    directories = [
        'downloads',
        'edited_videos', 
        'data',
        'logs',
        'sessions',
        'temp',
        'modules'
    ]
    
    missing = []
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - Missing")
            missing.append(directory)
    
    return len(missing) == 0

def test_main_script():
    """Test if main script can be imported"""
    print("\n🚀 Testing main script...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        from yt_nara import YTNara
        print("✅ yt_nara.py - Can import YTNara class")
        
        # Test initialization
        yt_nara = YTNara()
        print("✅ YTNara - Can create instance")
        
        return True
        
    except Exception as e:
        print(f"❌ yt_nara.py - {str(e)}")
        return False

def install_missing_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing missing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr}")
        return False

def create_missing_directories():
    """Create missing directories"""
    print("\n📁 Creating missing directories...")
    
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

def main():
    """Run all tests"""
    print("🧪 YT-Nara Installation Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test Python version
    if not test_python_version():
        all_passed = False
    
    # Test dependencies
    if not test_dependencies():
        print("\n⚠️ Some dependencies are missing. Installing...")
        if not install_missing_dependencies():
            all_passed = False
    
    # Test directories
    if not test_directories():
        print("\n⚠️ Some directories are missing. Creating...")
        create_missing_directories()
    
    # Test YT-Nara modules
    if not test_yt_nara_modules():
        all_passed = False
    
    # Test main script
    if not test_main_script():
        all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 All tests passed! YT-Nara is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run: python3 yt_nara.py --setup")
        print("2. Start using: python3 yt_nara.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Try running: python3 install.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())