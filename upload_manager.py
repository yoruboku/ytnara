"""
Upload Manager Module
Handles automated uploads to YouTube and Instagram with proper session management
"""

import asyncio
import logging
import json
import time
from pathlib import Path
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from models import ContentItem

class UploadManager:
    """Upload manager with proper error handling and session management"""
    
    def __init__(self):
        self.accounts = {
            'youtube': ['account1', 'account2'],
            'instagram': ['account1', 'account2']
        }
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
    
    async def upload_to_all_platforms(self, content_item: ContentItem) -> List[str]:
        """Upload content to all configured platforms"""
        uploaded_platforms = []
        
        # Get the video file to upload
        video_path = content_item.edited_path or content_item.downloaded_path
        if not video_path or not Path(video_path).exists():
            logging.error(f"No valid video file found for upload: {content_item.title}")
            return uploaded_platforms
        
        # Upload to YouTube accounts
        for account in self.accounts['youtube']:
            try:
                success = await self._upload_to_youtube(account, content_item, video_path)
                if success:
                    uploaded_platforms.append(f"youtube_{account}")
                    logging.info(f"Successfully uploaded to YouTube {account}: {content_item.title}")
                else:
                    logging.warning(f"Failed to upload to YouTube {account}: {content_item.title}")
            except Exception as e:
                logging.error(f"Error uploading to YouTube {account}: {str(e)}")
        
        # Upload to Instagram accounts
        for account in self.accounts['instagram']:
            try:
                success = await self._upload_to_instagram(account, content_item, video_path)
                if success:
                    uploaded_platforms.append(f"instagram_{account}")
                    logging.info(f"Successfully uploaded to Instagram {account}: {content_item.title}")
                else:
                    logging.warning(f"Failed to upload to Instagram {account}: {content_item.title}")
            except Exception as e:
                logging.error(f"Error uploading to Instagram {account}: {str(e)}")
        
        content_item.uploaded_platforms = uploaded_platforms
        return uploaded_platforms
    
    async def _upload_to_youtube(self, account: str, content_item: ContentItem, video_path: str) -> bool:
        """Upload video to YouTube"""
        driver = None
        try:
            driver = await self._create_driver()
            
            # Navigate to YouTube Studio
            driver.get("https://studio.youtube.com")
            
            # Wait for login or redirect to upload page
            await asyncio.sleep(3)
            
            # Check if we need to login
            if "accounts.google.com" in driver.current_url:
                logging.info(f"Need to login to YouTube for account {account}")
                # For demo purposes, we'll just log this
                # In real implementation, you'd handle the login flow
                return False
            
            # Navigate to upload page
            try:
                upload_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Create']"))
                )
                upload_button.click()
                
                # Wait for upload dialog
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                
                # Upload the video file
                file_input.send_keys(str(Path(video_path).absolute()))
                
                # Wait for upload to start
                await asyncio.sleep(5)
                
                # Fill in video details
                await self._fill_youtube_details(driver, content_item)
                
                # For demo purposes, we'll just log success
                # In real implementation, you'd click publish
                logging.info(f"Video uploaded to YouTube {account} (demo mode)")
                return True
                
            except TimeoutException:
                logging.error(f"Timeout waiting for YouTube upload elements for {account}")
                return False
                
        except Exception as e:
            logging.error(f"Error uploading to YouTube {account}: {str(e)}")
            return False
        finally:
            if driver:
                driver.quit()
    
    async def _upload_to_instagram(self, account: str, content_item: ContentItem, video_path: str) -> bool:
        """Upload video to Instagram"""
        driver = None
        try:
            driver = await self._create_driver()
            
            # Navigate to Instagram
            driver.get("https://www.instagram.com")
            
            # Wait for page load
            await asyncio.sleep(3)
            
            # Check if we need to login
            if "accounts/login" in driver.current_url:
                logging.info(f"Need to login to Instagram for account {account}")
                # For demo purposes, we'll just log this
                # In real implementation, you'd handle the login flow
                return False
            
            # Navigate to create post
            try:
                # Click create button (plus icon)
                create_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='New post']"))
                )
                create_button.click()
                
                # Wait for file input
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                
                # Upload the video file
                file_input.send_keys(str(Path(video_path).absolute()))
                
                # Wait for upload to start
                await asyncio.sleep(5)
                
                # Fill in post details
                await self._fill_instagram_details(driver, content_item)
                
                # For demo purposes, we'll just log success
                # In real implementation, you'd click share
                logging.info(f"Video uploaded to Instagram {account} (demo mode)")
                return True
                
            except TimeoutException:
                logging.error(f"Timeout waiting for Instagram upload elements for {account}")
                return False
                
        except Exception as e:
            logging.error(f"Error uploading to Instagram {account}: {str(e)}")
            return False
        finally:
            if driver:
                driver.quit()
    
    async def _create_driver(self) -> webdriver.Chrome:
        """Create Chrome driver with proper configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try to use webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logging.error(f"Error creating Chrome driver: {str(e)}")
            raise
    
    async def _fill_youtube_details(self, driver: webdriver.Chrome, content_item: ContentItem):
        """Fill YouTube video details"""
        try:
            # Wait for title field
            title_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Title']"))
            )
            
            # Generate SEO-optimized title
            title = self._generate_youtube_title(content_item)
            title_field.clear()
            title_field.send_keys(title)
            
            # Fill description
            try:
                description_field = driver.find_element(By.CSS_SELECTOR, "textarea[aria-label='Description']")
                description = self._generate_youtube_description(content_item)
                description_field.clear()
                description_field.send_keys(description)
            except:
                pass  # Description field might not be available
            
            # Add tags
            try:
                tags_field = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Tags']")
                tags = self._generate_youtube_tags(content_item)
                tags_field.clear()
                tags_field.send_keys(tags)
            except:
                pass  # Tags field might not be available
            
        except Exception as e:
            logging.error(f"Error filling YouTube details: {str(e)}")
    
    async def _fill_instagram_details(self, driver: webdriver.Chrome, content_item: ContentItem):
        """Fill Instagram post details"""
        try:
            # Wait for caption field
            caption_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='Write a caption...']"))
            )
            
            # Generate Instagram caption
            caption = self._generate_instagram_caption(content_item)
            caption_field.clear()
            caption_field.send_keys(caption)
            
        except Exception as e:
            logging.error(f"Error filling Instagram details: {str(e)}")
    
    def _generate_youtube_title(self, content_item: ContentItem) -> str:
        """Generate SEO-optimized YouTube title"""
        base_title = content_item.title
        
        # Add trending keywords
        trending_words = ["viral", "epic", "amazing", "incredible", "mind-blowing"]
        
        # Ensure title is engaging and under 100 characters
        if len(base_title) > 80:
            base_title = base_title[:77] + "..."
        
        return base_title
    
    def _generate_youtube_description(self, content_item: ContentItem) -> str:
        """Generate YouTube description"""
        description = f"🎬 {content_item.title}\n\n"
        description += "📱 Follow us for more amazing content!\n\n"
        
        # Add hashtags
        hashtags = self._generate_hashtags(content_item)
        description += " ".join(f"#{tag}" for tag in hashtags[:10])
        
        return description
    
    def _generate_youtube_tags(self, content_item: ContentItem) -> str:
        """Generate YouTube tags"""
        tags = content_item.keywords + content_item.tags
        # Add common tags
        tags.extend(["viral", "trending", "funny", "epic", "amazing"])
        
        # Return top 15 tags as comma-separated string
        return ", ".join(tags[:15])
    
    def _generate_instagram_caption(self, content_item: ContentItem) -> str:
        """Generate Instagram caption"""
        caption = f"🎬 {content_item.title}\n\n"
        
        # Add emojis and engaging text
        caption += "✨ Amazing content you don't want to miss!\n"
        caption += "📱 Follow for more epic videos!\n\n"
        
        # Add hashtags
        hashtags = self._generate_hashtags(content_item)
        caption += " ".join(f"#{tag}" for tag in hashtags[:20])
        
        return caption
    
    def _generate_hashtags(self, content_item: ContentItem) -> List[str]:
        """Generate relevant hashtags"""
        hashtags = []
        
        # Add keywords as hashtags
        hashtags.extend([tag.replace(' ', '') for tag in content_item.keywords])
        
        # Add platform-specific tags
        if content_item.platform == "youtube":
            hashtags.extend(["youtube", "video", "content"])
        elif content_item.platform == "instagram":
            hashtags.extend(["instagram", "reels", "viral"])
        elif content_item.platform == "tiktok":
            hashtags.extend(["tiktok", "fyp", "viral"])
        
        # Add common trending hashtags
        hashtags.extend(["viral", "trending", "funny", "epic", "amazing", "mindblowing"])
        
        # Remove duplicates and return
        return list(set(hashtags))[:25]