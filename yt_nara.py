#!/usr/bin/env python3
"""
YT-Nara: Universal Content Automation Tool
A comprehensive automation tool for discovering, editing, and uploading content across platforms.
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse

# Create all necessary directories first
required_dirs = ['logs', 'downloads', 'edited_videos', 'data', 'sessions', 'temp']
for directory in required_dirs:
    Path(directory).mkdir(exist_ok=True)

# Create basic config files if they don't exist
config_file = Path('data/config.json')
accounts_file = Path('data/accounts.json')

if not config_file.exists():
    import json
    default_config = {
        "app": {"name": "YT-Nara", "version": "1.0.0"},
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
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)

if not accounts_file.exists():
    import json
    default_accounts = {
        "youtube": [
            {"name": "account1", "logged_in": False},
            {"name": "account2", "logged_in": False}
        ],
        "instagram": [
            {"name": "account1", "logged_in": False},
            {"name": "account2", "logged_in": False}
        ]
    }
    with open(accounts_file, 'w') as f:
        json.dump(default_accounts, f, indent=2)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/yt_nara.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ContentItem:
    """Represents a piece of content to be processed"""
    url: str
    title: str
    platform: str
    creator: str
    keywords: List[str]
    downloaded_path: Optional[str] = None
    edited_path: Optional[str] = None
    uploaded_platforms: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.uploaded_platforms is None:
            self.uploaded_platforms = []

# Import custom modules with detailed error handling
missing_deps = []
modules_status = {}

try:
    from modules.config import Config
    from modules.database import ContentDatabase
    modules_status['basic'] = True
except ImportError as e:
    print(f"❌ Basic modules error: {e}")
    modules_status['basic'] = False

try:
    from modules.wikipedia_research import WikipediaResearcher
    modules_status['wikipedia'] = True
except ImportError as e:
    missing_deps.append(f"Wikipedia research: {e}")
    modules_status['wikipedia'] = False

try:
    from modules.content_discovery import ContentDiscovery
    modules_status['discovery'] = True
except ImportError as e:
    missing_deps.append(f"Content discovery: {e}")
    modules_status['discovery'] = False

try:
    from modules.content_verification import ContentVerifier
    modules_status['verification'] = True
except ImportError as e:
    missing_deps.append(f"Content verification: {e}")
    modules_status['verification'] = False

try:
    from modules.video_processor import VideoProcessor
    modules_status['video'] = True
except ImportError as e:
    missing_deps.append(f"Video processing: {e}")
    modules_status['video'] = False

try:
    from modules.upload_manager import UploadManager
    modules_status['upload'] = True
except ImportError as e:
    missing_deps.append(f"Upload manager: {e}")
    modules_status['upload'] = False

try:
    from modules.scheduler import ContentScheduler
    modules_status['scheduler'] = True
except ImportError as e:
    missing_deps.append(f"Scheduler: {e}")
    modules_status['scheduler'] = False

try:
    from modules.ui import TerminalUI
    modules_status['ui'] = True
except ImportError as e:
    missing_deps.append(f"UI: {e}")
    modules_status['ui'] = False

# Check if we have minimum required modules
if not modules_status['basic']:
    print("❌ Critical error: Basic modules not available!")
    sys.exit(1)

if missing_deps:
    print("⚠️ Some modules have dependency issues:")
    for dep in missing_deps:
        print(f"   - {dep}")
    print("\n🔧 Fixes:")
    print("   1. Run: python3 setup.py")
    print("   2. Or create virtual environment:")
    print("      python3 -m venv myenv && source myenv/bin/activate && pip install -r requirements.txt")
    print("   3. Or install manually:")
    print("      pip install --user aiohttp selenium moviepy yt-dlp rich colorama pyfiglet Pillow imageio-ffmpeg")
    
    # Allow basic functionality if UI is available
    if not modules_status['ui']:
        sys.exit(1)

class YTNara:
    """Main YT-Nara automation class"""
    
    def __init__(self):
        self.config = Config()
        self.db = ContentDatabase()
        
        # Initialize modules that are available
        if modules_status.get('ui', False):
            self.ui = TerminalUI()
        else:
            self.ui = None
            
        if modules_status.get('wikipedia', False):
            self.wiki_researcher = WikipediaResearcher()
        else:
            self.wiki_researcher = None
            
        if modules_status.get('discovery', False):
            self.content_discovery = ContentDiscovery()
        else:
            self.content_discovery = None
            
        if modules_status.get('verification', False):
            self.content_verifier = ContentVerifier()
        else:
            self.content_verifier = None
            
        if modules_status.get('video', False):
            self.video_processor = VideoProcessor()
        else:
            self.video_processor = None
            
        if modules_status.get('upload', False):
            self.upload_manager = UploadManager()
        else:
            self.upload_manager = None
            
        if modules_status.get('scheduler', False):
            self.scheduler = ContentScheduler()
        else:
            self.scheduler = None
        
        # Create necessary directories
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories for the application"""
        directories = [
            'downloads',
            'edited_videos',
            'logs',
            'data',
            'temp'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def run_interactive_mode(self):
        """Run the interactive mode with user prompts"""
        if not self.ui:
            print("❌ UI module not available. Please install dependencies:")
            print("   python3 setup.py")
            return
            
        self.ui.show_banner()
        
        try:
            # Get user inputs
            topic = self.ui.get_topic_input()
            cycles = self.ui.get_cycles_input()
            daily_frequency = self.ui.get_daily_frequency_input()
            
            # Show confirmation
            if not self.ui.show_confirmation(topic, cycles, daily_frequency):
                self.ui.print_info("Operation cancelled by user.")
                return
            
            # Start the automation process
            asyncio.run(self.run_automation(topic, cycles, daily_frequency))
            
        except KeyboardInterrupt:
            self.ui.print_warning("\nOperation interrupted by user.")
        except Exception as e:
            self.ui.print_error(f"An error occurred: {str(e)}")
            logging.exception("Error in interactive mode")
            raise
    
    async def run_automation(self, topic: str, cycles: int, daily_frequency: Optional[int]):
        """Run the main automation process"""
        # Check required modules
        missing_modules = []
        if not self.wiki_researcher:
            missing_modules.append("Wikipedia research")
        if not self.content_discovery:
            missing_modules.append("Content discovery")
        if not self.content_verifier:
            missing_modules.append("Content verification")
        if not self.video_processor:
            missing_modules.append("Video processing")
        if not self.upload_manager:
            missing_modules.append("Upload management")
            
        if missing_modules:
            print("❌ Cannot run automation - missing modules:")
            for module in missing_modules:
                print(f"   - {module}")
            print("\n🔧 Fix by running:")
            print("   python3 setup.py")
            print("   OR create virtual environment:")
            print("   python3 -m venv myenv && source myenv/bin/activate && pip install -r requirements.txt")
            return
            
        if self.ui:
            self.ui.print_info(f"Starting YT-Nara automation for topic: {topic}")
        else:
            print(f"Starting YT-Nara automation for topic: {topic}")
        
        # Step 1: Research topic on Wikipedia
        self.ui.print_step("Researching topic on Wikipedia...")
        keywords = await self.wiki_researcher.research_topic(topic)
        self.ui.print_success(f"Found {len(keywords)} relevant keywords")
        
        # Step 2: Discover content across platforms
        self.ui.print_step("Discovering content across platforms...")
        discovered_content = await self.content_discovery.discover_content(topic, keywords)
        self.ui.print_success(f"Discovered {len(discovered_content)} potential content items")
        
        # Step 3: Verify and filter content
        self.ui.print_step("Verifying content relevance...")
        verified_content = await self.content_verifier.verify_content(discovered_content, keywords)
        self.ui.print_success(f"Verified {len(verified_content)} relevant content items")
        
        # Step 4: Process content in cycles
        if daily_frequency:
            # Schedule for daily execution
            await self.schedule_daily_execution(verified_content, cycles, daily_frequency)
        else:
            # Run all cycles immediately
            await self.run_cycles(verified_content, cycles)
    
    async def run_cycles(self, content_list: List[ContentItem], cycles: int):
        """Run the specified number of cycles"""
        for cycle in range(cycles):
            self.ui.print_cycle_start(cycle + 1, cycles)
            
            # Select 4 videos for this cycle (1 per account)
            cycle_content = content_list[cycle * 4:(cycle + 1) * 4]
            
            if not cycle_content:
                self.ui.print_warning("No more content available for processing")
                break
            
            await self.process_cycle_content(cycle_content)
            
            # Add delay between cycles to avoid rate limiting
            if cycle < cycles - 1:
                self.ui.print_info("Waiting before next cycle...")
                await asyncio.sleep(30)
    
    async def process_cycle_content(self, content_list: List[ContentItem]):
        """Process a single cycle of content"""
        for content in content_list:
            try:
                # Download content
                self.ui.print_info(f"Downloading: {content.title}")
                content.downloaded_path = await self.video_processor.download_content(content)
                
                # Edit content
                self.ui.print_info(f"Editing: {content.title}")
                content.edited_path = await self.video_processor.edit_video(content)
                
                # Upload to platforms
                self.ui.print_info(f"Uploading: {content.title}")
                await self.upload_manager.upload_to_all_platforms(content)
                
                # Save to database
                self.db.save_processed_content(content)
                
                self.ui.print_success(f"Successfully processed: {content.title}")
                
            except Exception as e:
                self.ui.print_error(f"Failed to process {content.title}: {str(e)}")
                continue
    
    async def schedule_daily_execution(self, content_list: List[ContentItem], cycles: int, daily_frequency: int):
        """Schedule daily execution of content processing"""
        self.ui.print_info(f"Scheduling {daily_frequency} uploads per day")
        
        # Calculate time intervals between uploads
        interval_hours = 24 / daily_frequency
        
        # Schedule uploads throughout the day
        await self.scheduler.schedule_uploads(content_list, cycles, daily_frequency, interval_hours)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YT-Nara: Universal Content Automation Tool')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--topic', help='Topic to search for')
    parser.add_argument('--cycles', type=int, help='Number of cycles to run')
    parser.add_argument('--daily-frequency', type=int, help='Number of uploads per day')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')
    
    args = parser.parse_args()
    
    # Initialize YT-Nara
    yt_nara = YTNara()
    
    if args.setup:
        # Run setup mode
        yt_nara.ui.run_setup()
        return
    
    if args.topic:
        # Run in non-interactive mode
        asyncio.run(yt_nara.run_automation(
            args.topic,
            args.cycles or 1,
            args.daily_frequency
        ))
    else:
        # Run in interactive mode
        yt_nara.run_interactive_mode()

if __name__ == "__main__":
    main()