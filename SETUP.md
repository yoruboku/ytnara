# YT-Nara Setup Guide

This comprehensive guide will help you set up YT-Nara from scratch, including all dependencies and configurations.

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
3. **FFmpeg**: For video processing

## 🚀 Step-by-Step Installation

### Step 1: Install Python Dependencies

```bash
# Clone the repository (or download and extract)
cd yt-nara

# Install Python packages
pip install -r requirements.txt

# For development (optional)
pip install -r requirements-dev.txt
```

### Step 2: Install FFmpeg

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

#### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Step 3: Install ChromeDriver

#### Automatic Installation (Recommended)
```bash
# Install webdriver-manager for automatic ChromeDriver management
pip install webdriver-manager
```

#### Manual Installation
1. Check your Chrome version: `chrome://version/`
2. Download matching ChromeDriver from [chromedriver.chromium.org](https://chromedriver.chromium.org/)
3. Extract and place in system PATH

#### Verify ChromeDriver
```bash
chromedriver --version
```

### Step 4: Initial Setup

```bash
# Run the setup wizard
python yt_nara.py --setup
```

This will:
- Create necessary directories
- Check all dependencies
- Create default configuration files
- Set up the database

## 🔐 Account Configuration

### YouTube Accounts Setup

1. **Create YouTube Accounts** (if you don't have them):
   - Go to [youtube.com](https://youtube.com)
   - Create 2 separate Google accounts
   - Enable YouTube channels for both accounts

2. **Enable YouTube Studio Access**:
   - Visit [studio.youtube.com](https://studio.youtube.com) for each account
   - Complete any required setup steps

### Instagram Accounts Setup

1. **Create Instagram Accounts** (if you don't have them):
   - Go to [instagram.com](https://instagram.com)
   - Create 2 separate accounts
   - Verify email addresses

2. **Account Requirements**:
   - Accounts should not be brand new (wait 24-48 hours after creation)
   - Complete profile setup (bio, profile picture)
   - Post at least 1-2 pieces of content manually first

### First-Time Login Process

When you first run YT-Nara, it will:

1. **Open Chrome Windows**: One for each account (4 total)
2. **Guide You Through Login**: You'll need to manually log in to each account
3. **Save Sessions**: Login sessions are saved for future use
4. **Verify Access**: Confirm each account can access upload features

**Important**: Keep these browser windows open during the login process. YT-Nara will guide you through each step.

## 📁 Directory Structure After Setup

```
yt-nara/
├── downloads/              # Downloaded videos
├── edited_videos/          # Processed videos ready for upload
├── data/                   # Configuration and database files
│   ├── config.json        # Main configuration
│   ├── accounts.json      # Account status
│   ├── content.db         # SQLite database
│   └── schedule.json      # Scheduled tasks
├── logs/                   # Application logs
│   └── yt_nara.log       # Main log file
├── sessions/              # Browser session data
│   ├── youtube/           # YouTube account sessions
│   │   ├── account1/
│   │   └── account2/
│   └── instagram/         # Instagram account sessions
│       ├── account1/
│       └── account2/
└── temp/                  # Temporary files
```

## ⚙️ Configuration Options

### Basic Configuration (`data/config.json`)

```json
{
  "video_processing": {
    "max_video_duration": 60,
    "output_format": "mp4",
    "quality": "720p",
    "watermark_enabled": true,
    "watermark_text": "YT-Nara",
    "watermark_position": "bottom_right"
  },
  "upload": {
    "max_retries": 3,
    "retry_delay": 30,
    "upload_delay_min": 30,
    "upload_delay_max": 60
  },
  "content_discovery": {
    "max_results_per_platform": 20,
    "relevance_threshold": 0.3
  }
}
```

### Account Configuration (`data/accounts.json`)

```json
{
  "youtube": [
    {"name": "account1", "logged_in": false},
    {"name": "account2", "logged_in": false}
  ],
  "instagram": [
    {"name": "account1", "logged_in": false},
    {"name": "account2", "logged_in": false}
  ]
}
```

## 🧪 Testing Your Setup

### Quick Test Run
```bash
# Test with a simple topic
python yt_nara.py --topic "test content" --cycles 1
```

### Verify Each Component

1. **Wikipedia Research**:
   ```bash
   python -c "from modules.wikipedia_research import WikipediaResearcher; import asyncio; print(asyncio.run(WikipediaResearcher().research_topic('test')))"
   ```

2. **Content Discovery**:
   ```bash
   python -c "from modules.content_discovery import ContentDiscovery; print('Content discovery module loaded')"
   ```

3. **Video Processing**:
   ```bash
   ffmpeg -version
   ```

4. **Browser Automation**:
   ```bash
   python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit(); print('Selenium working')"
   ```

## 🔧 Troubleshooting Setup Issues

### Common Problems and Solutions

#### Python Import Errors
```bash
# Problem: ModuleNotFoundError
# Solution: Ensure all requirements are installed
pip install -r requirements.txt --upgrade
```

#### ChromeDriver Issues
```bash
# Problem: ChromeDriver version mismatch
# Solution: Update ChromeDriver
pip install webdriver-manager --upgrade
```

#### FFmpeg Not Found
```bash
# Problem: FFmpeg not in PATH
# Solution: Add FFmpeg to system PATH or reinstall

# Test FFmpeg
ffmpeg -version
```

#### Permission Errors
```bash
# Problem: Permission denied on Linux/macOS
# Solution: Check file permissions
chmod +x yt_nara.py
```

#### Browser Login Issues
- **Clear browser cache**: Remove session directories and try again
- **Disable 2FA temporarily**: For initial setup (re-enable after)
- **Use incognito mode**: If regular login fails
- **Check account status**: Ensure accounts aren't restricted

### Debug Mode
```bash
# Run with debug logging
python yt_nara.py --topic "debug test" --cycles 1 --debug
```

### Log Analysis
Check `logs/yt_nara.log` for detailed error information:
```bash
tail -f logs/yt_nara.log
```

## 🛡️ Security and Privacy

### Data Protection
- **Local Storage**: All data is stored locally on your machine
- **Session Security**: Browser sessions are encrypted and stored securely
- **No External Servers**: YT-Nara doesn't send data to external servers

### Account Security
- **Use Strong Passwords**: For all social media accounts
- **Enable 2FA**: After initial setup (may need to disable temporarily during setup)
- **Regular Updates**: Keep YT-Nara and dependencies updated

### Best Practices
- **Separate Accounts**: Use dedicated accounts for automation
- **Content Rights**: Only use content you have rights to
- **Rate Limiting**: Don't modify built-in delays
- **Monitoring**: Regularly check account status and upload success rates

## 📊 Performance Optimization

### System Optimization
- **Close Unnecessary Programs**: Free up RAM and CPU
- **SSD Storage**: Use SSD for faster video processing
- **Network**: Ensure stable, fast internet connection

### Configuration Tuning
```json
{
  "performance": {
    "max_concurrent_downloads": 2,
    "video_quality": "720p",
    "enable_gpu_acceleration": true
  }
}
```

## 🔄 Maintenance

### Regular Tasks
- **Clear Old Videos**: Remove processed videos to free space
- **Check Logs**: Monitor for errors or issues
- **Update Dependencies**: Keep software updated
- **Backup Configuration**: Save your settings

### Automated Cleanup
```bash
# Clean old files (run weekly)
python yt_nara.py --cleanup --days 7
```

## 🆘 Getting Help

### Before Asking for Help
1. Check this setup guide
2. Review the main README.md
3. Check logs for error messages
4. Try the troubleshooting steps

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community support
- **Documentation**: Check the wiki for advanced topics

### Providing Information
When asking for help, include:
- Operating system and version
- Python version
- Error messages from logs
- Steps to reproduce the issue

---

**🎉 Congratulations!** You should now have YT-Nara fully set up and ready to use. Start with a simple topic and small number of cycles to test everything is working correctly.