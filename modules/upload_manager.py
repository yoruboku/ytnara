"""
Upload Manager Module
Handles automated uploading to YouTube and Instagram using Selenium
"""

import os
import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass

# Import shared models
from .models import ContentItem

class UploadManager:
    """Automated upload management for multiple platforms"""
    
    def __init__(self):
        self.drivers = {}  # Store browser instances
        self.accounts = self._load_account_config()
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
        
        # Upload settings
        self.upload_delay = (30, 60)  # Random delay between uploads (seconds)
        self.max_retries = 3
        
    def _load_account_config(self) -> Dict:
        """Load account configuration"""
        config_path = Path("data/accounts.json")
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading account config: {str(e)}")
        
        # Default configuration structure
        return {
            "youtube": [
                {"name": "account1", "logged_in": False},
                {"name": "account2", "logged_in": False}
            ],
            "instagram": [
                {"name": "account1", "logged_in": False},
                {"name": "account2", "logged_in": False}
            ]
        }
    
    def _save_account_config(self):
        """Save account configuration"""
        config_path = Path("data/accounts.json")
        config_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.accounts, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving account config: {str(e)}")
    
    def _create_driver(self, platform: str, account_name: str) -> webdriver.Chrome:
        """Create a Chrome driver with appropriate settings"""
        options = Options()
        
        # User data directory for persistent sessions
        user_data_dir = self.session_dir / platform / account_name
        user_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome options for better compatibility and stealth
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # Experimental options for stealth
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        })
        
        # Set user agent to avoid detection
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Try to create driver with ChromeDriverManager for automatic driver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except ImportError:
                # Fallback to system ChromeDriver
                driver = webdriver.Chrome(options=options)
            
            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            return driver
            
        except Exception as e:
            logging.error(f"Error creating Chrome driver: {str(e)}")
            raise
    
    async def initialize_sessions(self):
        """Initialize browser sessions for all accounts"""
        logging.info("Initializing browser sessions...")
        
        for platform in ["youtube", "instagram"]:
            for account in self.accounts[platform]:
                account_name = account["name"]
                
                if not account.get("logged_in", False):
                    logging.info(f"Setting up {platform} account: {account_name}")
                    
                    driver = self._create_driver(platform, account_name)
                    self.drivers[f"{platform}_{account_name}"] = driver
                    
                    # Navigate to login page
                    if platform == "youtube":
                        driver.get("https://studio.youtube.com")
                    elif platform == "instagram":
                        driver.get("https://www.instagram.com")
                    
                    # Wait for user to log in
                    input(f"Please log in to {platform} account '{account_name}' and press Enter when done...")
                    
                    # Mark as logged in
                    account["logged_in"] = True
                    
                    # Keep driver for later use
                    logging.info(f"Successfully initialized {platform} account: {account_name}")
        
        # Save updated configuration
        self._save_account_config()
        logging.info("All browser sessions initialized")
    
    async def upload_to_all_platforms(self, content_item):
        """Upload content to all configured platforms"""
        upload_results = {}
        
        # Upload to YouTube accounts
        for i, account in enumerate(self.accounts["youtube"]):
            account_name = account["name"]
            
            try:
                result = await self._upload_to_youtube(content_item, account_name)
                upload_results[f"youtube_{account_name}"] = result
                
                if result:
                    content_item.uploaded_platforms.append(f"youtube_{account_name}")
                    logging.info(f"Successfully uploaded to YouTube account: {account_name}")
                else:
                    logging.error(f"Failed to upload to YouTube account: {account_name}")
                
                # Add delay between uploads
                if i < len(self.accounts["youtube"]) - 1:
                    delay = random.randint(*self.upload_delay)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logging.error(f"Error uploading to YouTube account {account_name}: {str(e)}")
                upload_results[f"youtube_{account_name}"] = False
        
        # Upload to Instagram accounts
        for i, account in enumerate(self.accounts["instagram"]):
            account_name = account["name"]
            
            try:
                result = await self._upload_to_instagram(content_item, account_name)
                upload_results[f"instagram_{account_name}"] = result
                
                if result:
                    content_item.uploaded_platforms.append(f"instagram_{account_name}")
                    logging.info(f"Successfully uploaded to Instagram account: {account_name}")
                else:
                    logging.error(f"Failed to upload to Instagram account: {account_name}")
                
                # Add delay between uploads
                if i < len(self.accounts["instagram"]) - 1:
                    delay = random.randint(*self.upload_delay)
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logging.error(f"Error uploading to Instagram account {account_name}: {str(e)}")
                upload_results[f"instagram_{account_name}"] = False
        
        return upload_results
    
    async def _upload_to_youtube(self, content_item, account_name: str) -> bool:
        """Upload content to YouTube"""
        driver_key = f"youtube_{account_name}"
        
        # Get or create driver
        if driver_key not in self.drivers:
            self.drivers[driver_key] = self._create_driver("youtube", account_name)
        
        driver = self.drivers[driver_key]
        
        try:
            # Navigate to YouTube Studio upload page
            driver.get("https://studio.youtube.com/channel/UC/videos/upload")
            
            # Wait for upload button and click it
            upload_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='file']"))
            )
            
            # Upload the video file
            video_path = content_item.edited_path or content_item.downloaded_path
            if not video_path or not Path(video_path).exists():
                logging.error(f"Video file not found: {video_path}")
                return False
            
            upload_button.send_keys(str(Path(video_path).absolute()))
            
            # Wait for upload to start
            await asyncio.sleep(5)
            
            # Fill in video details
            await self._fill_youtube_details(driver, content_item)
            
            # Wait for processing and publish
            return await self._publish_youtube_video(driver)
            
        except Exception as e:
            logging.error(f"Error uploading to YouTube: {str(e)}")
            return False
    
    async def _fill_youtube_details(self, driver, content_item):
        """Fill in YouTube video details"""
        try:
            # Generate optimized title
            title = self._generate_youtube_title(content_item)
            
            # Fill title
            title_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='textbox' and @aria-label='Add a title that describes your video (type @ to mention a channel)']"))
            )
            title_field.clear()
            title_field.send_keys(title)
            
            # Fill description
            description = self._generate_youtube_description(content_item)
            description_field = driver.find_element(By.XPATH, "//div[@id='textbox' and @aria-label='Tell viewers about your video (type @ to mention a channel)']")
            description_field.clear()
            description_field.send_keys(description)
            
            # Set thumbnail (if available)
            await self._set_youtube_thumbnail(driver, content_item)
            
            # Set as "Not made for kids"
            try:
                not_for_kids = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
                )
                not_for_kids.click()
            except TimeoutException:
                pass  # May already be selected or not visible
            
            # Click Next to go to visibility settings
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
            )
            next_button.click()
            
            # Skip monetization page
            await asyncio.sleep(2)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
            )
            next_button.click()
            
            # Skip checks page
            await asyncio.sleep(2)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='next-button']"))
            )
            next_button.click()
            
        except Exception as e:
            logging.error(f"Error filling YouTube details: {str(e)}")
    
    async def _set_youtube_thumbnail(self, driver, content_item):
        """Set custom thumbnail for YouTube video"""
        try:
            # Create thumbnail if not exists
            thumbnail_path = Path(content_item.edited_path).with_suffix('.jpg')
            
            if not thumbnail_path.exists() and content_item.edited_path:
                # Generate thumbnail from video
                from modules.video_processor import VideoProcessor
                processor = VideoProcessor()
                await processor.create_thumbnail(content_item.edited_path, str(thumbnail_path))
            
            if thumbnail_path.exists():
                # Upload thumbnail
                thumbnail_button = driver.find_element(By.XPATH, "//input[@id='file-loader']")
                thumbnail_button.send_keys(str(thumbnail_path.absolute()))
                await asyncio.sleep(3)
                
        except Exception as e:
            logging.debug(f"Could not set thumbnail: {str(e)}")
    
    async def _publish_youtube_video(self, driver) -> bool:
        """Publish the YouTube video"""
        try:
            # Set visibility to Public
            public_radio = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']"))
            )
            public_radio.click()
            
            # Click Publish
            publish_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//ytcp-button[@id='done-button']"))
            )
            publish_button.click()
            
            # Wait for confirmation
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Video published')]"))
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Error publishing YouTube video: {str(e)}")
            return False
    
    async def _upload_to_instagram(self, content_item, account_name: str) -> bool:
        """Upload content to Instagram"""
        driver_key = f"instagram_{account_name}"
        
        # Get or create driver
        if driver_key not in self.drivers:
            self.drivers[driver_key] = self._create_driver("instagram", account_name)
        
        driver = self.drivers[driver_key]
        
        try:
            # Navigate to Instagram
            driver.get("https://www.instagram.com")
            await asyncio.sleep(3)
            
            # Click new post button
            new_post_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//div[contains(@class, 'x1i10hfl')]"))
            )
            new_post_button.click()
            
            # Upload video file
            video_path = content_item.edited_path or content_item.downloaded_path
            if not video_path or not Path(video_path).exists():
                logging.error(f"Video file not found: {video_path}")
                return False
            
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(str(Path(video_path).absolute()))
            
            # Wait for upload and processing
            await asyncio.sleep(10)
            
            # Click Next
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            
            # Skip editing page
            await asyncio.sleep(3)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            
            # Fill caption
            caption = self._generate_instagram_caption(content_item)
            caption_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption...']"))
            )
            caption_field.clear()
            caption_field.send_keys(caption)
            
            # Share the post
            share_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')]"))
            )
            share_button.click()
            
            # Wait for confirmation
            await asyncio.sleep(5)
            
            return True
            
        except Exception as e:
            logging.error(f"Error uploading to Instagram: {str(e)}")
            return False
    
    def _generate_youtube_title(self, content_item) -> str:
        """Generate SEO-optimized YouTube title"""
        # Get main keywords
        main_keywords = content_item.keywords[:3]  # Top 3 keywords
        
        # Create engaging title
        title_templates = [
            f"{main_keywords[0].title()} - Epic Moments Compilation",
            f"Best {main_keywords[0].title()} Clips You Need to See",
            f"{main_keywords[0].title()} Highlights - Must Watch",
            f"Amazing {main_keywords[0].title()} Content",
            f"{main_keywords[0].title()} - Viral Moments"
        ]
        
        # Select random template and ensure it's under 100 characters
        title = random.choice(title_templates)
        if len(title) > 97:
            title = title[:97] + "..."
        
        return title
    
    def _generate_youtube_description(self, content_item) -> str:
        """Generate YouTube video description"""
        keywords_str = ", ".join(content_item.keywords[:10])
        
        description = f"""
🎬 Amazing content compilation featuring the best moments!

🔥 What you'll see in this video:
• Epic highlights and memorable moments
• Carefully curated content for maximum entertainment
• High-quality compilation you won't want to miss

📝 Keywords: {keywords_str}

⚡ Credits to original creator: @{content_item.creator}

🎯 Subscribe for more amazing content!

#viral #compilation #entertainment #trending
        """.strip()
        
        return description
    
    def _generate_instagram_caption(self, content_item) -> str:
        """Generate Instagram post caption"""
        hashtags = []
        
        # Add keyword-based hashtags
        for keyword in content_item.keywords[:10]:
            hashtag = "#" + keyword.replace(" ", "").lower()
            if len(hashtag) > 2:
                hashtags.append(hashtag)
        
        # Add generic hashtags
        generic_hashtags = [
            "#viral", "#trending", "#entertainment", "#funny", 
            "#amazing", "#compilation", "#mustwatch", "#epic"
        ]
        hashtags.extend(generic_hashtags)
        
        # Limit to 30 hashtags (Instagram limit)
        hashtags = hashtags[:30]
        
        caption = f"""
🔥 Epic compilation alert! 

Credit: @{content_item.creator}

{' '.join(hashtags)}
        """.strip()
        
        return caption
    
    def cleanup_drivers(self):
        """Close all browser drivers"""
        for driver_key, driver in self.drivers.items():
            try:
                driver.quit()
                logging.info(f"Closed browser session: {driver_key}")
            except Exception as e:
                logging.error(f"Error closing driver {driver_key}: {str(e)}")
        
        self.drivers.clear()
    
    def get_upload_stats(self) -> Dict:
        """Get upload statistics"""
        stats = {
            "total_accounts": len(self.accounts["youtube"]) + len(self.accounts["instagram"]),
            "logged_in_accounts": 0,
            "active_sessions": len(self.drivers)
        }
        
        for platform in ["youtube", "instagram"]:
            for account in self.accounts[platform]:
                if account.get("logged_in", False):
                    stats["logged_in_accounts"] += 1
        
        return stats
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup_drivers()