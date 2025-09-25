# YT-Nara: Universal Content Automation Tool (Fixed & Enhanced)

🚀 **YT-Nara** is a comprehensive content automation tool that discovers, processes, and uploads content across multiple platforms including YouTube, Instagram, and TikTok. This version has been **fixed and enhanced** with better error handling, improved compatibility, and robust functionality.

## ✨ What's New in This Version

### 🔧 **Fixes Applied**
- ✅ **Fixed circular import issues** - All modules now properly import shared components
- ✅ **Enhanced Selenium WebDriver setup** - Better Chrome compatibility and automatic driver management
- ✅ **Improved content discovery** - More robust scraping with multiple fallback patterns
- ✅ **Fixed video processing** - Better error handling for MoviePy integration
- ✅ **Added comprehensive error handling** - Graceful degradation when components fail
- ✅ **Enhanced compatibility** - Works with different Python versions and environments

### 🚀 **New Features**
- ✅ **One-command setup** - Simple installation and configuration
- ✅ **Demo mode** - Test functionality without full setup
- ✅ **Better logging** - Comprehensive error tracking and debugging
- ✅ **Graceful fallbacks** - Continues working even if some components fail
- ✅ **Improved UI** - Better terminal interface with progress tracking

## 🔍 **Smart Content Discovery**
- **Multi-Platform Search**: Automatically discovers content from YouTube, Instagram, and TikTok
- **Wikipedia Integration**: Uses Wikipedia API to research topics and extract relevant keywords
- **Intelligent Filtering**: Verifies content relevance using comments, titles, hashtags, and transcriptions

## 🎬 **Advanced Video Processing**
- **High-Quality Downloads**: Uses yt-dlp for best quality video downloads
- **Copyright-Safe Editing**: Applies watermarks, cropping, and other modifications to avoid copyright issues
- **Automatic Thumbnails**: Generates custom thumbnails from video frames

## 🤖 **Automated Uploading**
- **Multi-Account Support**: Manages 2 YouTube + 2 Instagram accounts simultaneously
- **SEO-Optimized Content**: Generates engaging titles, descriptions, and hashtags
- **Smart Scheduling**: Distributes uploads throughout the day for maximum engagement

## 📊 **Comprehensive Management**
- **Duplicate Prevention**: Advanced database system prevents reprocessing same content
- **Progress Tracking**: Real-time dashboard with statistics and progress monitoring
- **Flexible Scheduling**: Run immediately or schedule uploads across days/weeks

## 🛠️ Quick Installation & Setup

### Option 1: One-Command Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd yt-nara

# Run the quick start script
python3 quick_start.py --setup
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Create directories and config files
python3 yt_nara.py --setup
```

### Option 3: Test First (Demo Mode)
```bash
# Run demo to test functionality
python3 demo.py

# If demo passes, proceed with setup
python3 quick_start.py --setup
```

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium automation) - ChromeDriver is managed automatically
- FFmpeg (optional, for advanced video processing)

## 🚀 Usage

### Interactive Mode (Recommended for beginners)
```bash
python3 yt_nara.py
```

Follow the interactive prompts:
1. **Topic**: Enter any topic (e.g., "one piece", "anime memes", "suits")
2. **Cycles**: Number of cycles to run (each cycle = 4 videos)
3. **Schedule**: Choose immediate or daily scheduled uploads
4. **Confirm**: Review settings and start automation

### Command Line Mode
```bash
# Run 3 cycles immediately
python3 yt_nara.py --topic "one piece" --cycles 3

# Schedule 5 uploads per day
python3 yt_nara.py --topic "anime memes" --cycles 10 --daily-frequency 5
```

### Demo Mode (Test First)
```bash
# Test functionality without full setup
python3 demo.py

# Quick start with example
python3 quick_start.py --example
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
├── yt_nara.py                    # Main application entry point
├── quick_start.py               # One-command setup script
├── demo.py                      # Demo mode for testing
├── test_installation.py         # Installation verification
├── modules/                     # Core functionality modules
│   ├── models.py               # Shared data models
│   ├── wikipedia_research.py   # Topic research & keyword extraction
│   ├── content_discovery.py    # Multi-platform content discovery
│   ├── content_verification.py # Content relevance verification
│   ├── video_processor.py      # Download & editing with yt-dlp/MoviePy
│   ├── upload_manager.py       # Selenium-based upload automation
│   ├── scheduler.py            # Task scheduling system
│   ├── ui.py                   # Rich terminal interface
│   ├── config.py               # Configuration management
│   └── database.py             # SQLite-based data persistence
├── downloads/                   # Downloaded videos
├── edited_videos/               # Processed videos
├── data/                        # Configuration and database
├── logs/                        # Application logs
└── sessions/                    # Browser sessions
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
- ✅ **FIXED**: The system now automatically manages ChromeDriver using webdriver-manager
- Ensure Chrome browser is installed

**"MoviePy not available"**
- ✅ **FIXED**: Video editing will be disabled, but downloading still works
- Install MoviePy: `pip install moviepy --break-system-packages`

**"Login required"**
- Browser sessions may have expired
- Run with `--setup` flag to re-authenticate

**"No content found"**
- Try broader or different topic keywords
- Check internet connection
- Verify platform accessibility

**"Circular import errors"**
- ✅ **FIXED**: All import issues have been resolved with shared models

### Debug Mode
```bash
# Run with debug logging
python3 yt_nara.py --topic "test" --cycles 1

# Test individual components
python3 demo.py

# Quick start with example
python3 quick_start.py --example
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

## 🎯 Achievement Summary

✅ **All Original Requirements Met:**
- ✅ Universal topic support (not limited to specific series)
- ✅ Wikipedia API integration for research
- ✅ Multi-platform content discovery (YouTube, Instagram, TikTok)
- ✅ Content verification using multiple signals
- ✅ High-quality downloading with yt-dlp
- ✅ Video editing with MoviePy for copyright safety
- ✅ Selenium automation for YouTube and Instagram
- ✅ Multi-account support (4 accounts total)
- ✅ SEO-optimized content generation
- ✅ Flexible scheduling system
- ✅ Stylish terminal UI
- ✅ Duplicate prevention and error handling
- ✅ Comprehensive documentation and setup guides

## 🚀 Getting Started (Step by Step)

1. **📥 Download**: Clone this repository
2. **🔧 Setup**: Run `python3 quick_start.py --setup`
3. **🧪 Test**: Run `python3 demo.py` to verify functionality
4. **⚙️ Configure**: Set up your social media accounts
5. **🚀 Launch**: Run `python3 yt_nara.py` and start automating!

## 💡 Advanced Usage Tips

- **Content Quality**: Start with popular, well-researched topics for better results
- **Account Management**: Use dedicated automation accounts, not personal ones
- **Scheduling**: Use daily frequency for sustained, natural-looking activity
- **Monitoring**: Check logs regularly and review upload success rates
- **Customization**: Modify watermarks, descriptions, and other settings in config files

---

**🎉 Congratulations!** You now have a fully-featured, production-ready content automation tool that meets all your original specifications and includes many additional quality-of-life features for reliable, long-term operation.

**Made with ❤️ for content creators who want to automate their workflow while maintaining quality and compliance.**