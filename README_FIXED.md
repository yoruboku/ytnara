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

# Test the installation
python3 test_installation.py
```

### Option 3: Test First (Demo Mode)
```bash
# Run demo to test functionality
python3 demo.py

# If demo passes, proceed with setup
python3 yt_nara.py --setup
```

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

## 🎯 How It Works

1. **🔍 Research Phase**: Searches Wikipedia for your topic to extract relevant keywords
2. **🎬 Discovery Phase**: Uses keywords to find content across YouTube, Instagram, and TikTok
3. **✅ Verification Phase**: Analyzes titles, descriptions, comments, and transcripts to ensure relevance
4. **⬇️ Processing Phase**: Downloads videos and applies copyright-safe modifications
5. **⬆️ Upload Phase**: Distributes content across your accounts with optimized metadata
6. **📅 Scheduling Phase**: Manages timing to maximize engagement and avoid spam detection

## 🔧 Key Features

### **Universal Topic Support**
- ✅ Works with any topic (anime, movies, memes, etc.) - not limited to specific series
- ✅ Wikipedia API integration for intelligent keyword extraction
- ✅ Dynamic content discovery based on research

### **Multi-Platform Content Discovery**
- ✅ YouTube content discovery with metadata extraction
- ✅ Instagram post discovery with hashtag analysis
- ✅ TikTok video discovery with creator verification
- ✅ Smart content verification using comments, titles, hashtags, transcriptions

### **Advanced Video Processing**
- ✅ yt-dlp integration for high-quality downloads
- ✅ MoviePy-based video editing with copyright-safe modifications:
  - Cropping and resizing
  - Watermark addition
  - Audio adjustment
  - Duration limiting
- ✅ Automatic thumbnail generation

### **Automated Upload System**
- ✅ Selenium-based browser automation
- ✅ Multi-account support (2 YouTube + 2 Instagram accounts)
- ✅ SEO-optimized titles, descriptions, and hashtags
- ✅ Creator credit system
- ✅ Persistent login sessions

### **Flexible Scheduling**
- ✅ Immediate execution or scheduled uploads
- ✅ Daily frequency control (e.g., 5 times per day)
- ✅ Smart distribution across days/weeks
- ✅ Retry logic with exponential backoff

### **Quality Control & Duplicate Prevention**
- ✅ SQLite database for tracking processed content
- ✅ URL hash-based duplicate detection
- ✅ Content relevance scoring
- ✅ Upload history tracking
- ✅ Comprehensive error handling

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
├── requirements.txt             # Python dependencies
├── README.md                   # Original documentation
└── README_FIXED.md             # This enhanced documentation
```

## 🎨 Stylish Terminal UI

The application features a beautiful terminal interface with:
- ✅ **Rich terminal interface** with colors and animations
- ✅ **Interactive prompts** for easy configuration
- ✅ **Real-time progress tracking** with visual progress bars
- ✅ **Statistics dashboard** showing discovered, verified, downloaded, edited, and uploaded content
- ✅ **Error handling** and user feedback
- ✅ **Live dashboard** with next task preview and timing

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
- The system now automatically manages ChromeDriver using webdriver-manager
- Ensure Chrome browser is installed

**"MoviePy not available"**
- Video editing will be disabled, but downloading still works
- Install MoviePy: `pip install moviepy --break-system-packages`

**"Login required"**
- Browser sessions may have expired
- Run with `--setup` flag to re-authenticate

**"No content found"**
- Try broader or different topic keywords
- Check internet connection
- Verify platform accessibility

### Debug Mode
```bash
# Run with debug logging
python3 yt_nara.py --topic "test" --cycles 1

# Test individual components
python3 demo.py
```

## 🧪 Testing

### Run Demo
```bash
python3 demo.py
```

### Test Installation
```bash
python3 test_installation.py
```

### Quick Start
```bash
python3 quick_start.py --example
```

## 📊 Monitoring & Analytics

### **Real-time Dashboard**
- Live progress tracking with Rich UI
- Statistics: discovered, verified, downloaded, edited, uploaded
- Next task preview and timing
- Error rate monitoring

### **Data Persistence**
- SQLite database for all operations
- Upload history with success/failure tracking
- Content metadata storage
- Configurable data retention policies

## 🔒 Security & Privacy

### **Local Operation**
- All data stored locally (no external servers)
- Encrypted browser session storage
- No data transmission to third parties
- User-controlled data retention

### **Account Safety**
- Session-based authentication (no password storage)
- Smart timing to appear human-like
- Built-in rate limiting
- Account isolation and rotation

## 📈 Performance & Scalability

### **Modular Architecture**
- Easily extensible for new platforms
- Plugin-style module system
- Configurable processing pipelines
- API-ready design

### **Performance Optimization**
- Asynchronous operations throughout
- Concurrent processing where safe
- Memory-efficient video handling
- Automatic cleanup of temporary files

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check the wiki for detailed guides
- **Community**: Join discussions in GitHub Discussions

---

**🎉 Congratulations!** You now have a fully-featured, production-ready content automation tool that meets all your original specifications and includes many additional quality-of-life features for reliable, long-term operation.

**Made with ❤️ for content creators who want to automate their workflow while maintaining quality and compliance.**