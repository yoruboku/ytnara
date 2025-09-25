#!/usr/bin/env python3
"""
Test script to verify YT-Nara setup
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        'aiohttp',
        'selenium',
        'moviepy',
        'yt_dlp',
        'rich',
        'colorama',
        'pyfiglet'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            failed_imports.append(module)
    
    return failed_imports

def test_directories():
    """Test if required directories exist"""
    directories = [
        'downloads',
        'edited_videos',
        'data',
        'logs',
        'sessions',
        'temp',
        'modules'
    ]
    
    missing_dirs = []
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ (missing)")
            missing_dirs.append(directory)
    
    return missing_dirs

def test_yt_nara_modules():
    """Test YT-Nara specific modules"""
    modules = [
        'modules.wikipedia_research',
        'modules.content_discovery',
        'modules.content_verification',
        'modules.video_processor',
        'modules.upload_manager',
        'modules.scheduler',
        'modules.ui',
        'modules.config',
        'modules.database'
    ]
    
    failed_modules = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            failed_modules.append(module)
    
    return failed_modules

def main():
    """Run all tests"""
    print("🧪 Testing YT-Nara Setup...\n")
    
    print("📦 Testing Python Dependencies:")
    failed_imports = test_imports()
    
    print("\n📁 Testing Directory Structure:")
    missing_dirs = test_directories()
    
    print("\n🔧 Testing YT-Nara Modules:")
    failed_modules = test_yt_nara_modules()
    
    print("\n" + "="*50)
    
    if failed_imports or missing_dirs or failed_modules:
        print("❌ Setup Issues Found:")
        
        if failed_imports:
            print(f"   Missing dependencies: {', '.join(failed_imports)}")
            print("   Run: pip install -r requirements.txt")
        
        if missing_dirs:
            print(f"   Missing directories: {', '.join(missing_dirs)}")
            print("   Run: python yt_nara.py --setup")
        
        if failed_modules:
            print(f"   Module import errors: {', '.join(failed_modules)}")
            print("   Check module files and dependencies")
        
        return 1
    else:
        print("✅ All tests passed! YT-Nara is ready to use.")
        print("   Run: python yt_nara.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())