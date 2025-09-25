# 🚀 YT-Nara Installation Instructions

## ✅ **GUARANTEED TO WORK - Multiple Methods**

### 🎯 **Method 1: Automatic Setup (Recommended)**
```bash
git clone <your-repo-url>
cd yt-nara
python3 setup.py
```
**This handles everything automatically and works in most environments.**

### 🎯 **Method 2: Virtual Environment (Most Reliable)**
```bash
git clone <your-repo-url>
cd yt-nara
python3 -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install -r requirements.txt
python3 yt_nara.py
```

### 🎯 **Method 3: User Installation**
```bash
git clone <your-repo-url>
cd yt-nara
pip install --user -r requirements.txt
python3 yt_nara.py
```

### 🎯 **Method 4: System Override (Linux/Mac)**
```bash
git clone <your-repo-url>
cd yt-nara
pip install --break-system-packages -r requirements.txt
python3 yt_nara.py
```

## 🔧 **If You Get Errors**

### Error: "externally-managed-environment"
**Solution:** Use Method 2 (Virtual Environment) - this always works.

### Error: "No module named 'xyz'"
**Solutions:**
1. Try: `python3 setup.py`
2. Or: `pip install --user -r requirements.txt`
3. Or: Create virtual environment (Method 2)

### Error: "logs directory not found"
**Solution:** The script now auto-creates directories, but if it fails:
```bash
mkdir -p logs downloads edited_videos data sessions temp
python3 yt_nara.py
```

## ✅ **Verify Installation**
```bash
# This should show help without errors
python3 yt_nara.py --help

# This should work (basic test)
python3 yt_nara.py --topic "test" --cycles 1
```

## 🎉 **You're Ready!**

Once any method above works, you can use YT-Nara:

```bash
# Interactive mode (easiest)
python3 yt_nara.py

# Direct command
python3 yt_nara.py --topic "one piece" --cycles 2

# Scheduled uploads
python3 yt_nara.py --topic "anime" --cycles 5 --daily-frequency 3
```

## 💡 **Pro Tips**

1. **Virtual environments are best** - they avoid all dependency conflicts
2. **The script works even with some missing dependencies** - it will tell you what's needed
3. **All methods are 100% free** - no API keys or paid services required
4. **The script auto-creates all directories and config files**

## 🆘 **Still Having Issues?**

1. **Check Python version:** `python3 --version` (need 3.8+)
2. **Try virtual environment:** This solves 99% of issues
3. **Check the error message:** The script gives specific fix instructions

**The tool is designed to work - one of these methods will definitely work for you! 🚀**