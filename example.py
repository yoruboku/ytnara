#!/usr/bin/env python3
"""
YT-Nara Example Usage
Demonstrates how to use YT-Nara programmatically
"""

import asyncio
import logging
from yt_nara import YTNara

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    """Example usage of YT-Nara"""
    
    # Initialize YT-Nara
    yt_nara = YTNara()
    
    # Example 1: Simple automation
    print("🚀 Starting YT-Nara automation example...")
    
    topic = "anime memes"
    cycles = 2
    daily_frequency = None  # Run immediately
    
    try:
        await yt_nara.run_automation(topic, cycles, daily_frequency)
        print("✅ Automation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during automation: {str(e)}")
        logging.exception("Automation failed")

if __name__ == "__main__":
    asyncio.run(main())