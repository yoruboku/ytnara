#!/usr/bin/env python3
"""
YT-Nara Example Usage (Updated)
Demonstrates how to use YT-Nara programmatically with the fixed version
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """Example usage of YT-Nara"""
    
    print("🚀 YT-Nara Example Usage")
    print("=" * 40)
    
    try:
        # Import and initialize YT-Nara
        from yt_nara import YTNara
        yt_nara = YTNara()
        
        # Example 1: Simple automation
        print("🎬 Starting YT-Nara automation example...")
        
        topic = "anime memes"
        cycles = 1  # Start with 1 cycle for testing
        daily_frequency = None  # Run immediately
        
        print(f"📝 Topic: {topic}")
        print(f"🔄 Cycles: {cycles}")
        print(f"⏰ Mode: Immediate execution")
        
        await yt_nara.run_automation(topic, cycles, daily_frequency)
        print("✅ Automation completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt --break-system-packages")
        
    except Exception as e:
        print(f"❌ Error during automation: {str(e)}")
        logging.exception("Automation failed")
        print("💡 Try running the demo first: python3 demo.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n💥 Example crashed: {str(e)}")
        print("💡 Try running: python3 demo.py")