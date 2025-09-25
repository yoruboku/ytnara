"""
Video Processing Module
Handles video downloading and editing with proper error handling
"""

import asyncio
import logging
import subprocess
import os
from pathlib import Path
from typing import Optional
from models import ContentItem

# Try to import MoviePy with fallback
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        from moviepy import VideoFileClip, TextClip, CompositeVideoClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False
        logging.warning("MoviePy not available - video editing will be disabled")

class VideoProcessor:
    """Video processing with proper error handling and fallbacks"""
    
    def __init__(self):
        self.download_dir = Path("downloads")
        self.edited_dir = Path("edited_videos")
        self.download_dir.mkdir(exist_ok=True)
        self.edited_dir.mkdir(exist_ok=True)
    
    async def download_content(self, content_item: ContentItem) -> Optional[str]:
        """Download content using yt-dlp with retry logic"""
        if not content_item.url:
            logging.error("No URL provided for download")
            return None
        
        try:
            # Generate filename
            filename = self._generate_filename(content_item)
            output_path = self.download_dir / filename
            
            # Check if already downloaded
            if output_path.exists():
                logging.info(f"Content already downloaded: {filename}")
                return str(output_path)
            
            # Download with yt-dlp
            cmd = [
                "yt-dlp",
                "--output", str(output_path),
                "--format", "best[height<=720]",  # Limit to 720p to avoid huge files
                "--max-filesize", "100M",  # Limit file size
                "--no-playlist",
                content_item.url
            ]
            
            # Try download with retries
            for attempt in range(3):
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        # Verify the file was created and is valid
                        if await self._verify_video_file(output_path):
                            content_item.downloaded_path = str(output_path)
                            logging.info(f"Successfully downloaded: {filename}")
                            return str(output_path)
                        else:
                            logging.warning(f"Downloaded file is invalid: {filename}")
                            if output_path.exists():
                                output_path.unlink()  # Remove invalid file
                    else:
                        logging.warning(f"Download attempt {attempt + 1} failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    logging.warning(f"Download timeout on attempt {attempt + 1}")
                except Exception as e:
                    logging.error(f"Download error on attempt {attempt + 1}: {str(e)}")
                
                # Wait before retry
                if attempt < 2:
                    await asyncio.sleep(5)
            
            logging.error(f"Failed to download after 3 attempts: {content_item.url}")
            return None
            
        except Exception as e:
            logging.error(f"Error downloading content: {str(e)}")
            return None
    
    async def edit_video(self, content_item: ContentItem) -> Optional[str]:
        """Edit video with watermark and other modifications"""
        if not content_item.downloaded_path:
            logging.error("No downloaded file to edit")
            return None
        
        if not MOVIEPY_AVAILABLE:
            logging.warning("MoviePy not available - skipping video editing")
            return content_item.downloaded_path
        
        try:
            input_path = Path(content_item.downloaded_path)
            if not input_path.exists():
                logging.error(f"Downloaded file not found: {input_path}")
                return content_item.downloaded_path
            
            # Generate edited filename
            edited_filename = self._generate_edited_filename(content_item)
            output_path = self.edited_dir / edited_filename
            
            # Check if already edited
            if output_path.exists():
                logging.info(f"Video already edited: {edited_filename}")
                content_item.edited_path = str(output_path)
                return str(output_path)
            
            # Edit video
            edited_path = await self._apply_edits(input_path, output_path, content_item)
            
            if edited_path and Path(edited_path).exists():
                content_item.edited_path = str(edited_path)
                logging.info(f"Successfully edited video: {edited_filename}")
                return str(edited_path)
            else:
                logging.warning("Video editing failed, using original")
                return content_item.downloaded_path
                
        except Exception as e:
            logging.error(f"Error editing video: {str(e)}")
            return content_item.downloaded_path
    
    async def _apply_edits(self, input_path: Path, output_path: Path, content_item: ContentItem) -> Optional[str]:
        """Apply edits to video"""
        try:
            # Load video
            video = VideoFileClip(str(input_path))
            
            # Limit duration to 60 seconds for memes/shorts
            if video.duration > 60:
                video = video.subclip(0, 60)
            
            # Add watermark text
            watermark = TextClip(
                "YT-Nara",
                fontsize=24,
                color='white',
                font='Arial-Bold'
            ).set_position(('right', 'bottom')).set_duration(video.duration)
            
            # Composite video with watermark
            final_video = CompositeVideoClip([video, watermark])
            
            # Write the result
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Close clips to free memory
            video.close()
            watermark.close()
            final_video.close()
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Error applying video edits: {str(e)}")
            return None
    
    def _generate_filename(self, content_item: ContentItem) -> str:
        """Generate filename for downloaded content"""
        # Clean title for filename
        safe_title = "".join(c for c in content_item.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Get platform and ID
        platform = content_item.platform
        if platform == "youtube":
            video_id = content_item.url.split('v=')[1].split('&')[0] if 'v=' in content_item.url else "unknown"
            return f"youtube_{video_id}_{safe_title}.%(ext)s"
        elif platform == "instagram":
            post_id = content_item.url.split('/p/')[1].split('/')[0] if '/p/' in content_item.url else "unknown"
            return f"instagram_{post_id}_{safe_title}.%(ext)s"
        elif platform == "tiktok":
            video_id = content_item.url.split('/video/')[1].split('?')[0] if '/video/' in content_item.url else "unknown"
            return f"tiktok_{video_id}_{safe_title}.%(ext)s"
        else:
            return f"{platform}_{safe_title}.%(ext)s"
    
    def _generate_edited_filename(self, content_item: ContentItem) -> str:
        """Generate filename for edited content"""
        input_path = Path(content_item.downloaded_path)
        base_name = input_path.stem
        return f"edited_{base_name}.mp4"
    
    async def _verify_video_file(self, file_path: Path) -> bool:
        """Verify that the downloaded file is a valid video"""
        try:
            if not file_path.exists():
                return False
            
            # Check file size
            if file_path.stat().st_size < 1024:  # At least 1KB
                return False
            
            # If MoviePy is available, try to load the video
            if MOVIEPY_AVAILABLE:
                try:
                    video = VideoFileClip(str(file_path))
                    duration = video.duration
                    video.close()
                    
                    # Check if duration is reasonable (not 0 and not too long)
                    if duration <= 0 or duration > 600:  # Max 10 minutes
                        return False
                    
                    return True
                except Exception:
                    return False
            else:
                # Basic check without MoviePy
                return file_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']
                
        except Exception as e:
            logging.error(f"Error verifying video file: {str(e)}")
            return False