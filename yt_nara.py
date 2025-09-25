#!/usr/bin/env python3
"""
YT-Nara: Universal Content Automation Tool
Main application entry point
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/yt_nara.log'),
        logging.StreamHandler()
    ]
)

# Create logs directory
Path('logs').mkdir(exist_ok=True)

# Import modules
from models import ContentItem
from wikipedia_researcher import WikipediaResearcher
from content_discovery import ContentDiscovery
from content_verification import ContentVerifier
from video_processor import VideoProcessor
from upload_manager import UploadManager
from database import Database
from ui import TerminalUI

class YTNara:
    """Main YT-Nara automation class"""
    
    def __init__(self):
        self.ui = TerminalUI()
        self.db = Database()
        self.video_processor = VideoProcessor()
        self.upload_manager = UploadManager()
    
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
        
        try:
            # Step 1: Research topic on Wikipedia
            self.ui.print_step("Researching topic on Wikipedia...")
            async with WikipediaResearcher() as researcher:
                keywords = await researcher.research_topic(topic)
            self.ui.print_success(f"Found {len(keywords)} relevant keywords")
            
            # Step 2: Discover content across platforms
            self.ui.print_step("Discovering content across platforms...")
            async with ContentDiscovery() as discovery:
                discovered_content = await discovery.discover_content(topic, keywords)
            self.ui.print_success(f"Discovered {len(discovered_content)} potential content items")
            
            # Step 3: Verify and filter content
            self.ui.print_step("Verifying content relevance...")
            async with ContentVerifier() as verifier:
                verified_content = await verifier.verify_content(discovered_content, keywords)
            self.ui.print_success(f"Verified {len(verified_content)} relevant content items")
            
            # Step 4: Process content in cycles
            if daily_frequency:
                # Schedule for daily execution
                await self.schedule_daily_execution(verified_content, cycles, daily_frequency)
            else:
                # Run all cycles immediately
                await self.run_cycles(verified_content, cycles)
                
        except Exception as e:
            logging.exception("Error in automation process")
            self.ui.print_error(f"Automation failed: {str(e)}")
    
    async def run_cycles(self, content_list: list, cycles: int):
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
    
    async def process_cycle_content(self, content_list: list):
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
                uploaded_platforms = await self.upload_manager.upload_to_all_platforms(content)
                
                # Save to database
                self.db.save_content(content)
                
                self.ui.print_success(f"Successfully processed: {content.title}")
                
            except Exception as e:
                self.ui.print_error(f"Failed to process {content.title}: {str(e)}")
                continue
    
    async def schedule_daily_execution(self, content_list: list, cycles: int, daily_frequency: int):
        """Schedule daily execution of content processing"""
        self.ui.print_info(f"Scheduling {daily_frequency} uploads per day")
        
        # For now, just run all cycles immediately
        # In a full implementation, this would schedule tasks
        await self.run_cycles(content_list, cycles)
    
    def show_statistics(self):
        """Show database statistics"""
        stats = self.db.get_statistics()
        self.ui.show_statistics(stats)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YT-Nara: Universal Content Automation Tool')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--topic', help='Topic to search for')
    parser.add_argument('--cycles', type=int, help='Number of cycles to run')
    parser.add_argument('--daily-frequency', type=int, help='Number of uploads per day')
    parser.add_argument('--setup', action='store_true', help='Run initial setup')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    # Initialize YT-Nara
    yt_nara = YTNara()
    
    if args.setup:
        # Run setup mode
        yt_nara.ui.run_setup()
        return
    
    if args.stats:
        # Show statistics
        yt_nara.show_statistics()
        return
    
    if args.topic and args.cycles:
        # Command line mode
        daily_frequency = args.daily_frequency
        asyncio.run(yt_nara.run_automation(args.topic, args.cycles, daily_frequency))
    else:
        # Interactive mode
        yt_nara.run_interactive_mode()

if __name__ == "__main__":
    main()