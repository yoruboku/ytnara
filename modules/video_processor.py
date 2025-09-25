"""
Video Processor Module
Handles video downloading with yt-dlp and editing with MoviePy
"""

import os
import asyncio
import subprocess
import logging
import tempfile
import hashlib
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import json
import random
import string

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
    from moviepy.video.fx import resize, crop
    from moviepy.audio.fx import volumex
    MOVIEPY_AVAILABLE = True
except ImportError:
    # Fallback imports for different MoviePy versions
    try:
        from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
        from moviepy.video.fx.resize import resize
        from moviepy.video.fx.crop import crop
        from moviepy.audio.fx.volumex import volumex
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False
        logging.warning("MoviePy not available - video editing will be disabled")
import yt_dlp

# Import will be resolved at runtime
# from yt_nara import ContentItem

class VideoProcessor:
    """Video downloading and editing functionality"""
    
    def __init__(self):
        self.download_dir = Path("downloads")
        self.edited_dir = Path("edited_videos")
        self.temp_dir = Path("temp")
        
        # Create directories
        self.download_dir.mkdir(exist_ok=True)
        self.edited_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # yt-dlp configuration
        self.ytdl_opts = {
            'format': 'best[height<=1080][ext=mp4]/best[ext=mp4]/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'ignoreerrors': True,
            'no_warnings': True,
            'extractflat': False,
            'writethumbnail': True,
        }
        
        # Watermark settings
        self.watermark_text = "YT-Nara"
        self.watermark_position = ('right', 'bottom')
        
    async def download_content(self, content_item) -> Optional[str]:
        """Download content using yt-dlp"""
        try:
            logging.info(f"Downloading: {content_item.url}")
            
            # Generate unique filename to avoid conflicts
            safe_title = self._sanitize_filename(content_item.title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            output_template = str(self.download_dir / f"{safe_title}_{timestamp}_{unique_id}.%(ext)s")
            
            # Update yt-dlp options for this download
            opts = self.ytdl_opts.copy()
            opts['outtmpl'] = output_template
            
            # Platform-specific optimizations
            if content_item.platform == "youtube":
                opts['format'] = 'best[height<=1080][ext=mp4]/best[ext=mp4]/best'
            elif content_item.platform == "instagram":
                opts['format'] = 'best[ext=mp4]/best'
            elif content_item.platform == "tiktok":
                opts['format'] = 'best[ext=mp4]/best'
            
            # Add retry logic and better error handling
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Download the video
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        # Get video info first
                        info = await self._get_video_info(content_item.url, ydl)
                        if not info:
                            logging.warning(f"Could not get video info for: {content_item.url} (attempt {attempt + 1})")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(5)  # Wait before retry
                                continue
                            else:
                                return None
                        
                        # Update content item with additional info
                        content_item.duration = info.get('duration', 0)
                        content_item.view_count = info.get('view_count', 0)
                        content_item.upload_date = info.get('upload_date', '')
                        
                        # Skip very long videos
                        if content_item.duration and content_item.duration > 600:  # 10 minutes
                            logging.warning(f"Skipping long video ({content_item.duration}s): {content_item.url}")
                            return None
                        
                        # Download the video
                        await self._download_video(content_item.url, ydl)
                        break  # Success, exit retry loop
                        
                except Exception as e:
                    logging.warning(f"Download attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(10)  # Wait before retry
                        continue
                    else:
                        raise
            
            # Find the downloaded file
            downloaded_file = self._find_downloaded_file(safe_title, timestamp, unique_id)
            
            if downloaded_file and downloaded_file.exists():
                logging.info(f"Successfully downloaded: {downloaded_file}")
                
                # Verify the file is valid
                if await self._verify_video_file(downloaded_file):
                    return str(downloaded_file)
                else:
                    logging.error(f"Downloaded file is corrupted: {downloaded_file}")
                    # Try to clean up corrupted file
                    try:
                        downloaded_file.unlink()
                    except Exception:
                        pass
                    return None
            else:
                logging.error(f"Could not find downloaded file for: {content_item.url}")
                return None
                
        except Exception as e:
            logging.error(f"Error downloading content {content_item.url}: {str(e)}")
            return None
    
    async def _get_video_info(self, url: str, ydl: yt_dlp.YoutubeDL) -> Optional[Dict]:
        """Get video information without downloading"""
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
            return info
        except Exception as e:
            logging.error(f"Error getting video info: {str(e)}")
            return None
    
    async def _download_video(self, url: str, ydl: yt_dlp.YoutubeDL) -> None:
        """Download video in a separate thread"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: ydl.download([url]))
        except Exception as e:
            logging.error(f"Error downloading video: {str(e)}")
            raise
    
    def _find_downloaded_file(self, safe_title: str, timestamp: str, unique_id: str) -> Optional[Path]:
        """Find the downloaded video file"""
        # Common video extensions
        extensions = ['.mp4', '.webm', '.mkv', '.avi', '.mov']
        
        for ext in extensions:
            filename = f"{safe_title}_{timestamp}_{unique_id}{ext}"
            file_path = self.download_dir / filename
            
            if file_path.exists():
                return file_path
        
        # Fallback: search for files with similar names
        pattern = f"{safe_title}_{timestamp}_{unique_id}"
        for file_path in self.download_dir.glob(f"{pattern}*"):
            if file_path.suffix.lower() in extensions:
                return file_path
        
        return None
    
    async def _verify_video_file(self, file_path: Path) -> bool:
        """Verify that the video file is valid and playable"""
        try:
            # Check file size
            if file_path.stat().st_size < 1024:  # Less than 1KB
                return False
            
            if not MOVIEPY_AVAILABLE:
                # If MoviePy is not available, just check if file exists and has reasonable size
                return file_path.exists() and file_path.stat().st_size > 1024
            
            # Try to open with MoviePy
            loop = asyncio.get_event_loop()
            
            def check_video():
                try:
                    with VideoFileClip(str(file_path)) as clip:
                        # Check basic properties
                        return (clip.duration > 0 and 
                               clip.w > 0 and 
                               clip.h > 0)
                except Exception:
                    return False
            
            is_valid = await loop.run_in_executor(None, check_video)
            return is_valid
            
        except Exception as e:
            logging.error(f"Error verifying video file: {str(e)}")
            return False
    
    async def edit_video(self, content_item) -> Optional[str]:
        """Edit video with basic modifications to avoid copyright"""
        if not MOVIEPY_AVAILABLE:
            logging.warning("MoviePy not available - skipping video editing")
            return content_item.downloaded_path
        
        if not content_item.downloaded_path:
            logging.error("No downloaded file to edit")
            return None
        
        try:
            input_path = Path(content_item.downloaded_path)
            if not input_path.exists():
                logging.error(f"Input file does not exist: {input_path}")
                return None
            
            # Generate output filename
            output_filename = f"edited_{input_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            output_path = self.edited_dir / output_filename
            
            logging.info(f"Editing video: {input_path}")
            
            # Edit video in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self._edit_video_sync, str(input_path), str(output_path), content_item)
            
            if success and output_path.exists():
                logging.info(f"Successfully edited video: {output_path}")
                return str(output_path)
            else:
                logging.error(f"Failed to edit video: {input_path}")
                return None
                
        except Exception as e:
            logging.error(f"Error editing video: {str(e)}")
            return None
    
    def _edit_video_sync(self, input_path: str, output_path: str, content_item) -> bool:
        """Synchronous video editing function"""
        try:
            with VideoFileClip(input_path) as video:
                # Get video properties
                duration = video.duration
                width, height = video.size
                
                # Apply modifications to avoid copyright
                edited_clips = []
                
                # 1. Crop video slightly (remove 5% from each side)
                crop_margin = int(min(width, height) * 0.05)
                cropped_video = crop(video, 
                                   x1=crop_margin, 
                                   y1=crop_margin, 
                                   x2=width-crop_margin, 
                                   y2=height-crop_margin)
                
                # 2. Resize to standard resolution (to change file signature)
                if width > 1920 or height > 1080:
                    resized_video = resize(cropped_video, height=1080)
                elif width < 1280 or height < 720:
                    resized_video = resize(cropped_video, height=720)
                else:
                    resized_video = cropped_video
                
                # 3. Adjust audio volume slightly
                if resized_video.audio:
                    resized_video = resized_video.fx(volumex, 0.95)
                
                # 4. Add watermark
                watermark = self._create_watermark(resized_video.size, duration)
                if watermark:
                    final_video = CompositeVideoClip([resized_video, watermark])
                else:
                    final_video = resized_video
                
                # 5. Limit duration if too long (max 60 seconds for most platforms)
                max_duration = 60
                if duration > max_duration:
                    # Take the most engaging part (middle section)
                    start_time = max(0, (duration - max_duration) / 2)
                    final_video = final_video.subclip(start_time, start_time + max_duration)
                
                # Write the final video
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=str(self.temp_dir / 'temp-audio.m4a'),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                return True
                
        except Exception as e:
            logging.error(f"Error in synchronous video editing: {str(e)}")
            return False
    
    def _create_watermark(self, video_size: Tuple[int, int], duration: float) -> Optional[TextClip]:
        """Create a watermark for the video"""
        try:
            width, height = video_size
            
            # Create text watermark
            watermark = TextClip(
                self.watermark_text,
                fontsize=int(min(width, height) * 0.03),  # 3% of smaller dimension
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            ).set_duration(duration)
            
            # Position watermark
            margin = int(min(width, height) * 0.02)  # 2% margin
            
            if self.watermark_position == ('right', 'bottom'):
                watermark = watermark.set_position(('right', 'bottom')).set_margin(margin)
            elif self.watermark_position == ('left', 'bottom'):
                watermark = watermark.set_position(('left', 'bottom')).set_margin(margin)
            elif self.watermark_position == ('right', 'top'):
                watermark = watermark.set_position(('right', 'top')).set_margin(margin)
            else:  # left, top
                watermark = watermark.set_position(('left', 'top')).set_margin(margin)
            
            # Make watermark semi-transparent
            watermark = watermark.set_opacity(0.7)
            
            return watermark
            
        except Exception as e:
            logging.error(f"Error creating watermark: {str(e)}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename.strip('_')
    
    async def get_video_info(self, file_path: str) -> Dict:
        """Get information about a video file"""
        try:
            def get_info():
                with VideoFileClip(file_path) as clip:
                    return {
                        'duration': clip.duration,
                        'fps': clip.fps,
                        'size': clip.size,
                        'has_audio': clip.audio is not None
                    }
            
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, get_info)
            return info
            
        except Exception as e:
            logging.error(f"Error getting video info: {str(e)}")
            return {}
    
    async def create_thumbnail(self, video_path: str, output_path: str, time_offset: float = 1.0) -> bool:
        """Create a thumbnail from video"""
        try:
            def create_thumb():
                with VideoFileClip(video_path) as clip:
                    # Get frame at specified time (or 1 second if video is long enough)
                    thumb_time = min(time_offset, clip.duration - 0.1)
                    frame = clip.get_frame(thumb_time)
                    
                    # Save as image
                    from PIL import Image
                    img = Image.fromarray(frame)
                    img.save(output_path, 'JPEG', quality=85)
                    return True
            
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, create_thumb)
            return success
            
        except Exception as e:
            logging.error(f"Error creating thumbnail: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for temp_file in self.temp_dir.glob('*'):
                if temp_file.is_file():
                    temp_file.unlink()
        except Exception as e:
            logging.error(f"Error cleaning up temp files: {str(e)}")
    
    def get_storage_info(self) -> Dict:
        """Get storage information"""
        def get_dir_size(path: Path) -> int:
            total_size = 0
            try:
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            except Exception:
                pass
            return total_size
        
        return {
            'downloads_size_mb': get_dir_size(self.download_dir) / (1024 * 1024),
            'edited_size_mb': get_dir_size(self.edited_dir) / (1024 * 1024),
            'temp_size_mb': get_dir_size(self.temp_dir) / (1024 * 1024)
        }