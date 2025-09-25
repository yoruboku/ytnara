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

# Create logs directory first
Path('logs').mkdir(exist_ok=True)

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

# Import custom modules after ContentItem is defined
from modules.wikipedia_research import WikipediaResearcher
from modules.content_discovery import ContentDiscovery
from modules.content_verification import ContentVerifier
from modules.video_processor import VideoProcessor
from modules.upload_manager import UploadManager
from modules.scheduler import ContentScheduler
from modules.ui import TerminalUI
from modules.config import Config
from modules.database import ContentDatabase

class YTNara:
    """Main YT-Nara automation class"""
    
    def __init__(self):
        self.config = Config()
        self.ui = TerminalUI()
        self.db = ContentDatabase()
        self.wiki_researcher = WikipediaResearcher()
        self.content_discovery = ContentDiscovery()
        self.content_verifier = ContentVerifier()
        self.video_processor = VideoProcessor()
        self.upload_manager = UploadManager()
        self.scheduler = ContentScheduler()
        
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
        self.ui.print_info(f"Starting YT-Nara automation for topic: {topic}")
        
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