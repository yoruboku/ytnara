# YT-Nara: Universal Content Automation Tool

🚀 **YT-Nara** is a comprehensive content automation tool that discovers, processes, and uploads content across multiple platforms including YouTube, Instagram, and TikTok.

## ✨ Features

### 🔍 **Smart Content Discovery**
- **Multi-Platform Search**: Automatically discovers content from YouTube, Instagram, and TikTok
- **Wikipedia Integration**: Uses Wikipedia API to research topics and extract relevant keywords
- **Intelligent Filtering**: Verifies content relevance using comments, titles, hashtags, and transcriptions

### 🎬 **Advanced Video Processing**
- **High-Quality Downloads**: Uses yt-dlp for best quality video downloads
- **Copyright-Safe Editing**: Applies watermarks, cropping, and other modifications to avoid copyright issues
- **Automatic Thumbnails**: Generates custom thumbnails from video frames

### 🤖 **Automated Uploading**
- **Multi-Account Support**: Manages 2 YouTube + 2 Instagram accounts simultaneously
- **SEO-Optimized Content**: Generates engaging titles, descriptions, and hashtags
- **Smart Scheduling**: Distributes uploads throughout the day for maximum engagement

### 📊 **Comprehensive Management**
- **Duplicate Prevention**: Advanced database system prevents reprocessing same content
- **Progress Tracking**: Real-time dashboard with statistics and progress monitoring
- **Flexible Scheduling**: Run immediately or schedule uploads across days/weeks

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium automation)
- FFmpeg (for video processing)

### Step 1: Clone and Setup
```bash
git clone https://github.com/yoruboku/ytnara.git
cd ytnara
pip install -r requirements.txt
```

### Step 2: Install ChromeDriver
Download ChromeDriver from https://chromedriver.chromium.org/ and ensure it's in your PATH.

### Step 3: Install FFmpeg
- **Windows**: Download from https://ffmpeg.org/download.html
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Step 4: Initial Setup
```bash
python yt_nara.py --setup
```

## 🚀 Quick Start

### Interactive Mode
```bash
python yt_nara.py
```

Follow the interactive prompts to:
1. Enter your topic (e.g., "one piece", "anime memes", "suits")
2. Set number of cycles (each cycle = 4 videos)
3. Choose scheduling options
4. Confirm and start automation

### Command Line Mode
```bash
# Run 3 cycles immediately
python yt_nara.py --topic "one piece" --cycles 3

# Schedule 5 uploads per day for multiple days
python yt_nara.py --topic "anime memes" --cycles 10 --daily-frequency 5
```

## 🔧 Configuration

### Account Setup
On first run, YT-Nara will open browser windows for you to log into your accounts:
- 2 YouTube accounts
- 2 Instagram accounts

Sessions are saved for future use.

### Customization Options
Edit `data/config.json` to customize:
- Video quality settings
- Watermark text and position
- Upload delays and retries
- Content discovery limits

## 📁 Project Structure

```
yt-nara/
├── yt_nara.py              # Main application
├── modules/                # Core modules
│   ├── wikipedia_research.py   # Topic research
│   ├── content_discovery.py    # Platform content discovery
│   ├── content_verification.py # Content relevance checking
│   ├── video_processor.py      # Download and editing
│   ├── upload_manager.py       # Platform uploading
│   ├── scheduler.py            # Task scheduling
│   ├── ui.py                   # Terminal interface
│   ├── config.py              # Configuration management
│   └── database.py            # Data persistence
├── downloads/              # Downloaded videos
├── edited_videos/          # Processed videos
├── data/                   # Configuration and database
├── logs/                   # Application logs
└── sessions/              # Browser sessions
```

## 🎯 How It Works

1. **Research Phase**: Searches Wikipedia for your topic to extract relevant keywords
2. **Discovery Phase**: Uses keywords to find content across YouTube, Instagram, and TikTok
3. **Verification Phase**: Analyzes titles, descriptions, comments, and transcripts to ensure relevance
4. **Processing Phase**: Downloads videos and applies copyright-safe modifications
5. **Upload Phase**: Distributes content across your accounts with optimized metadata
6. **Scheduling Phase**: Manages timing to maximize engagement and avoid spam detection

## 📊 Dashboard Features

- **Real-time Statistics**: Track discovered, verified, downloaded, and uploaded content
- **Progress Monitoring**: Visual progress bars and status updates
- **Schedule Overview**: See upcoming uploads and timing
- **Error Tracking**: Monitor failed uploads and retry attempts

## ⚠️ Important Notes

### Legal and Ethical Usage
- **Respect Copyright**: Only use content you have rights to or that falls under fair use
- **Credit Creators**: The tool automatically credits original creators
- **Platform Compliance**: Follow YouTube and Instagram terms of service
- **Content Guidelines**: Ensure uploaded content meets platform community guidelines

### Rate Limiting
- Built-in delays prevent platform rate limiting
- Randomized upload times appear more natural
- Account rotation distributes activity

### Quality Control
- Duplicate detection prevents reprocessing
- Relevance scoring ensures quality content
- Failed upload retry system with exponential backoff

## 🔧 Troubleshooting

### Common Issues

**"ChromeDriver not found"**
- Ensure ChromeDriver is installed and in PATH
- Check Chrome browser version compatibility

**"FFmpeg not found"**
- Install FFmpeg and ensure it's in system PATH
- Restart terminal after installation

**"Login required"**
- Browser sessions may have expired
- Run with `--setup` flag to re-authenticate

**"No content found"**
- Try broader or different topic keywords
- Check internet connection
- Verify platform accessibility

### Debug Mode
```bash
python yt_nara.py --topic "test" --cycles 1 --debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚡ Advanced Usage

### Custom Scheduling
```python
from modules.scheduler import ContentScheduler

scheduler = ContentScheduler()
# Custom scheduling logic here
```

### Batch Processing
```bash
# Process multiple topics
python yt_nara.py --topic "topic1,topic2,topic3" --cycles 2
```

### API Integration
The modular design allows easy integration with external APIs and services.

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check the wiki for detailed guides
- **Community**: Join discussions in GitHub Discussions

---

**Made with ❤️ for content creators who want to automate their workflow while maintaining quality and compliance.**
