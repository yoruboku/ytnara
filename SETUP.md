# YT-Nara Setup Guide (Updated & Simplified)

This comprehensive guide will help you set up the **fixed and enhanced** YT-Nara from scratch.

## 🚀 Quick Setup (Recommended)

### Option 1: One-Command Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd yt-nara

# Run the quick start script
python3 quick_start.py --setup
```

### Option 2: Test First, Then Setup
```bash
# Test functionality without full setup
python3 demo.py

# If demo passes, proceed with setup
python3 quick_start.py --setup
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended for better performance)
- **Storage**: At least 5GB free space for videos and data
- **Internet**: Stable broadband connection

### Required Software
1. **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
2. **Google Chrome**: Latest version from [google.com/chrome](https://www.google.com/chrome/)
3. **FFmpeg**: Optional, for advanced video processing

## 🛠️ Manual Installation (If Quick Setup Fails)

### Step 1: Install Python Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd yt-nara

# Install Python packages
pip install -r requirements.txt --break-system-packages

# Test the installation
python3 test_installation.py
```

### Step 2: Create Directories and Config Files

```bash
# Run initial setup
python3 yt_nara.py --setup
```

This will create:
- `downloads/` - Downloaded videos
- `edited_videos/` - Processed videos
- `data/` - Configuration and database files
- `logs/` - Application logs
- `sessions/` - Browser session data
- `temp/` - Temporary files

### Step 3: Install FFmpeg (Optional)

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Verify installation: `ffmpeg -version`

#### macOS
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Or using MacPorts
sudo port install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install ffmpeg
# or for newer versions
sudo dnf install ffmpeg
```

## 🔧 Configuration

### Initial Configuration

The setup process creates default configuration files in `data/`:

- `config.json` - Main application settings
- `accounts.json` - Social media account configuration

### Account Setup

YT-Nara supports:
- **2 YouTube accounts**
- **2 Instagram accounts**

On first run, the application will:
1. Open browser windows for each account
2. Guide you through the login process
3. Save session data for future use

### Customizing Settings

Edit `data/config.json` to customize:

```json
{
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
```

## 🧪 Testing Your Installation

### Run Demo Mode
```bash
python3 demo.py
```

This tests all core functionality without requiring full setup.

### Test Installation
```bash
python3 test_installation.py
```

This verifies all dependencies and modules are working.

### Quick Example
```bash
python3 quick_start.py --example
```

This runs a simple automation example.

## 🚀 First Run

### Interactive Mode (Recommended)
```bash
python3 yt_nara.py
```

Follow the prompts:
1. **Topic**: Enter your content topic (e.g., "anime memes")
2. **Cycles**: Number of automation cycles
3. **Schedule**: Immediate or scheduled execution
4. **Confirm**: Review and start

### Command Line Mode
```bash
# Run 1 cycle immediately
python3 yt_nara.py --topic "anime memes" --cycles 1

# Schedule multiple cycles
python3 yt_nara.py --topic "one piece" --cycles 5 --daily-frequency 2
```

## 🔧 Troubleshooting

### Common Issues

**"ChromeDriver not found"**
- ✅ **FIXED**: ChromeDriver is now managed automatically
- Ensure Chrome browser is installed

**"MoviePy not available"**
- ✅ **FIXED**: Video editing will be disabled, downloading still works
- Install manually: `pip install moviepy --break-system-packages`

**"Circular import errors"**
- ✅ **FIXED**: All import issues resolved with shared models

**"No content found"**
- Try different or broader topic keywords
- Check internet connection
- Verify platform accessibility

**"Login required"**
- Browser sessions may have expired
- Run: `python3 yt_nara.py --setup` to re-authenticate

### Getting Help

1. **Check logs**: Look in `logs/yt_nara.log` for detailed error messages
2. **Run demo**: `python3 demo.py` to test individual components
3. **Test installation**: `python3 test_installation.py` to verify setup

## 📊 Verification Checklist

After setup, verify these components work:

- [ ] Python dependencies installed
- [ ] Directories created
- [ ] Configuration files generated
- [ ] Demo mode passes all tests
- [ ] Main application starts without errors
- [ ] Browser automation works (Chrome opens)
- [ ] Database operations work
- [ ] UI displays correctly

## 🎯 Next Steps

Once setup is complete:

1. **Configure accounts**: Set up your social media accounts
2. **Test with small runs**: Start with 1-2 cycles to verify everything works
3. **Monitor logs**: Check `logs/yt_nara.log` for any issues
4. **Scale up**: Once comfortable, run larger automation cycles

## 💡 Tips for Success

- **Start small**: Test with 1-2 cycles first
- **Use dedicated accounts**: Don't use personal social media accounts
- **Monitor results**: Check upload success rates and adjust settings
- **Keep backups**: Regular backups of your configuration and data
- **Stay updated**: Keep dependencies updated for best compatibility

---

**🎉 You're all set!** YT-Nara is now ready to automate your content creation workflow.