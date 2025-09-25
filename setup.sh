#!/bin/bash
# YT-Nara One-Command Setup Script
# Run this after: git clone <repo>

echo "🚀 Setting up YT-Nara - Universal Content Automation Tool"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    print_info "Please install Python 3.8+ from: https://python.org"
    exit 1
fi

print_status "Python 3 found"

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    print_error "Python 3.8+ required, found $python_version"
    exit 1
fi

print_status "Python version $python_version (compatible)"

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 not found, installing..."
    python3 -m ensurepip --default-pip
fi

# Upgrade pip
print_info "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install requirements
print_info "Installing Python dependencies (this may take a few minutes)..."
if python3 -m pip install -r requirements.txt --quiet; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    print_info "Try running manually: pip3 install -r requirements.txt"
    exit 1
fi

# Create directories
print_info "Creating directories..."
mkdir -p downloads edited_videos data logs sessions temp
print_status "Directories created"

# Create config files
print_info "Creating configuration files..."
python3 -c "
import json
from pathlib import Path

# Create config
config = {
    'app': {'name': 'YT-Nara', 'version': '1.0.0'},
    'video_processing': {
        'max_video_duration': 60,
        'watermark_text': 'YT-Nara',
        'watermark_position': 'bottom_right'
    },
    'upload': {
        'max_retries': 3,
        'upload_delay_min': 30,
        'upload_delay_max': 60
    }
}

Path('data').mkdir(exist_ok=True)
with open('data/config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Create accounts config
accounts = {
    'youtube': [
        {'name': 'account1', 'logged_in': False},
        {'name': 'account2', 'logged_in': False}
    ],
    'instagram': [
        {'name': 'account1', 'logged_in': False},
        {'name': 'account2', 'logged_in': False}
    ]
}

with open('data/accounts.json', 'w') as f:
    json.dump(accounts, f, indent=2)

print('Config files created')
"

print_status "Configuration files created"

# Test installation
print_info "Testing installation..."
if python3 -c "
try:
    import aiohttp, selenium, moviepy, yt_dlp
    from rich.console import Console
    from modules.config import Config
    print('✅ All modules working')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" 2>/dev/null; then
    print_status "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Check for Chrome (optional but recommended)
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
    print_status "Chrome browser found"
else
    print_warning "Chrome browser not found"
    print_info "Install Chrome for full functionality: https://google.com/chrome"
fi

# Check for FFmpeg (optional but recommended)
if command -v ffmpeg &> /dev/null; then
    print_status "FFmpeg found"
else
    print_warning "FFmpeg not found"
    print_info "Install FFmpeg for video processing: https://ffmpeg.org"
fi

echo ""
echo "🎉 YT-Nara Setup Complete!"
echo "=========================="
echo ""
echo "📋 Quick Start:"
echo "   python3 yt_nara.py"
echo ""
echo "📖 Help:"
echo "   python3 yt_nara.py --help"
echo ""
echo "⚡ Example Usage:"
echo "   python3 yt_nara.py --topic 'one piece' --cycles 2"
echo ""
echo "🔧 First Time Setup (for social accounts):"
echo "   python3 yt_nara.py --setup"
echo ""
echo "💡 Tips:"
echo "   - Start with small cycles (1-2) to test"
echo "   - Use popular topics for better results"
echo "   - Install Chrome and FFmpeg for full features"
echo ""
print_status "Ready to automate content creation! 🚀"