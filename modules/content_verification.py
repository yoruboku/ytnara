"""
Content Verification Module
Verifies content relevance using comments, titles, hashtags, and transcriptions
"""

import asyncio
import aiohttp
import re
import json
import logging
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urlparse, parse_qs
import difflib
from collections import Counter

# Import shared models
from .models import ContentItem

class ContentVerifier:
    """Content verification and relevance scoring"""
    
    def __init__(self):
        self.session = None
        self.relevance_threshold = 0.3  # Minimum relevance score to keep content
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def verify_content(self, content_items: List[ContentItem], keywords: List[str]) -> List[ContentItem]:
        """Verify content relevance and filter out irrelevant items"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        verified_content = []
        
        # Process content in batches to avoid overwhelming servers
        batch_size = 10
        for i in range(0, len(content_items), batch_size):
            batch = content_items[i:i + batch_size]
            
            # Verify each item in the batch
            tasks = [self._verify_single_content(item, keywords) for item in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect verified content
            for result in results:
                if isinstance(result, tuple) and result[0]:  # (is_verified, content_item)
                    verified_content.append(result[1])
                elif isinstance(result, Exception):
                    logging.warning(f"Content verification error: {str(result)}")
            
            # Add delay between batches
            if i + batch_size < len(content_items):
                await asyncio.sleep(2)
        
        # Sort by relevance score (highest first)
        verified_content.sort(key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)
        
        logging.info(f"Verified {len(verified_content)} out of {len(content_items)} content items")
        return verified_content
    
    async def _verify_single_content(self, content_item: ContentItem, keywords: List[str]) -> Tuple[bool, ContentItem]:
        """Verify a single content item"""
        try:
            # Get content metadata
            metadata = await self._get_content_metadata(content_item)
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(content_item, metadata, keywords)
            
            # Add relevance score to content item
            content_item.relevance_score = relevance_score
            
            # Update content item with additional metadata
            if metadata:
                content_item.title = metadata.get('title', content_item.title)
                content_item.creator = metadata.get('creator', content_item.creator)
                content_item.description = metadata.get('description', '')
                content_item.tags = metadata.get('tags', [])
                content_item.comments = metadata.get('comments', [])
                content_item.transcript = metadata.get('transcript', '')
            
            # Verify if content meets threshold
            is_verified = relevance_score >= self.relevance_threshold
            
            if is_verified:
                logging.debug(f"Verified content: {content_item.title} (score: {relevance_score:.2f})")
            
            return is_verified, content_item
            
        except Exception as e:
            logging.error(f"Error verifying content {content_item.url}: {str(e)}")
            return False, content_item
    
    async def _get_content_metadata(self, content_item: ContentItem) -> Optional[Dict]:
        """Get metadata for content verification"""
        try:
            if content_item.platform == "youtube":
                return await self._get_youtube_metadata(content_item.url)
            elif content_item.platform == "instagram":
                return await self._get_instagram_metadata(content_item.url)
            elif content_item.platform == "tiktok":
                return await self._get_tiktok_metadata(content_item.url)
            
        except Exception as e:
            logging.error(f"Error getting metadata for {content_item.url}: {str(e)}")
        
        return None
    
    async def _get_youtube_metadata(self, url: str) -> Optional[Dict]:
        """Get YouTube video metadata"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    metadata = {}
                    
                    # Extract title
                    title_match = re.search(r'"title":"([^"]+)"', html_content)
                    if title_match:
                        metadata['title'] = title_match.group(1)
                    
                    # Extract description
                    desc_match = re.search(r'"shortDescription":"([^"]*)"', html_content)
                    if desc_match:
                        metadata['description'] = desc_match.group(1)
                    
                    # Extract channel name
                    channel_match = re.search(r'"author":"([^"]+)"', html_content)
                    if channel_match:
                        metadata['creator'] = channel_match.group(1)
                    
                    # Extract tags/keywords
                    tags_match = re.search(r'"keywords":\[(.*?)\]', html_content)
                    if tags_match:
                        tags_str = tags_match.group(1)
                        tags = re.findall(r'"([^"]+)"', tags_str)
                        metadata['tags'] = tags
                    
                    # Extract some comments (from initial page load)
                    comments = self._extract_youtube_comments(html_content)
                    metadata['comments'] = comments
                    
                    # Try to extract transcript/captions
                    transcript = await self._get_youtube_transcript(url)
                    if transcript:
                        metadata['transcript'] = transcript
                    
                    return metadata
        
        except Exception as e:
            logging.error(f"Error getting YouTube metadata: {str(e)}")
        
        return None
    
    def _extract_youtube_comments(self, html_content: str) -> List[str]:
        """Extract comments from YouTube HTML"""
        comments = []
        
        try:
            # Pattern for comment text in YouTube's data
            comment_pattern = r'"content":"([^"]+)"'
            matches = re.findall(comment_pattern, html_content)
            
            # Filter and clean comments
            for match in matches[:20]:  # Limit to first 20 comments
                if len(match) > 10 and not match.startswith('http'):  # Skip short comments and URLs
                    # Decode unicode escapes
                    comment = match.encode().decode('unicode_escape')
                    comments.append(comment)
        
        except Exception as e:
            logging.error(f"Error extracting YouTube comments: {str(e)}")
        
        return comments
    
    async def _get_youtube_transcript(self, url: str) -> Optional[str]:
        """Get YouTube video transcript/captions"""
        try:
            # Extract video ID from URL
            video_id_match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url)
            if not video_id_match:
                return None
            
            video_id = video_id_match.group(1)
            
            # Try to get auto-generated captions
            caption_url = f"https://www.youtube.com/api/timedtext?lang=en&v={video_id}&fmt=json3"
            
            async with self.session.get(caption_url) as response:
                if response.status == 200:
                    caption_data = await response.json()
                    
                    # Extract text from captions
                    transcript_parts = []
                    events = caption_data.get('events', [])
                    
                    for event in events:
                        segs = event.get('segs', [])
                        for seg in segs:
                            text = seg.get('utf8', '').strip()
                            if text:
                                transcript_parts.append(text)
                    
                    return ' '.join(transcript_parts)
        
        except Exception as e:
            logging.debug(f"Could not get YouTube transcript: {str(e)}")
        
        return None
    
    async def _get_instagram_metadata(self, url: str) -> Optional[Dict]:
        """Get Instagram post metadata"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    metadata = {}
                    
                    # Try to extract from JSON-LD
                    json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
                    if json_ld_match:
                        try:
                            json_data = json.loads(json_ld_match.group(1))
                            if isinstance(json_data, list):
                                json_data = json_data[0]
                            
                            metadata['title'] = json_data.get('caption', '')
                            metadata['creator'] = json_data.get('author', {}).get('name', '')
                            metadata['description'] = json_data.get('caption', '')
                            
                        except json.JSONDecodeError:
                            pass
                    
                    # Extract hashtags from content
                    hashtag_pattern = r'#(\w+)'
                    hashtags = re.findall(hashtag_pattern, html_content)
                    metadata['tags'] = hashtags
                    
                    # Try to extract comments
                    comments = self._extract_instagram_comments(html_content)
                    metadata['comments'] = comments
                    
                    return metadata
        
        except Exception as e:
            logging.error(f"Error getting Instagram metadata: {str(e)}")
        
        return None
    
    def _extract_instagram_comments(self, html_content: str) -> List[str]:
        """Extract comments from Instagram HTML"""
        comments = []
        
        try:
            # Pattern for comment text in Instagram's data
            comment_pattern = r'"text":"([^"]+)"'
            matches = re.findall(comment_pattern, html_content)
            
            for match in matches[:15]:  # Limit to first 15 comments
                if len(match) > 5:
                    comments.append(match)
        
        except Exception as e:
            logging.error(f"Error extracting Instagram comments: {str(e)}")
        
        return comments
    
    async def _get_tiktok_metadata(self, url: str) -> Optional[Dict]:
        """Get TikTok video metadata"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    metadata = {}
                    
                    # Extract from TikTok's JSON data
                    json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
                    if json_match:
                        try:
                            json_data = json.loads(json_match.group(1))
                            
                            # Navigate TikTok's complex data structure
                            props = json_data.get('props', {}).get('pageProps', {})
                            item_info = props.get('itemInfo', {}).get('itemStruct', {})
                            
                            if item_info:
                                metadata['title'] = item_info.get('desc', '')
                                metadata['description'] = item_info.get('desc', '')
                                
                                author = item_info.get('author', {})
                                metadata['creator'] = author.get('uniqueId', '')
                                
                                # Extract hashtags from description
                                desc = item_info.get('desc', '')
                                hashtags = re.findall(r'#(\w+)', desc)
                                metadata['tags'] = hashtags
                            
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback: extract from HTML patterns
                    if not metadata:
                        title_match = re.search(r'"desc":"([^"]+)"', html_content)
                        if title_match:
                            metadata['title'] = title_match.group(1)
                            metadata['description'] = title_match.group(1)
                        
                        author_match = re.search(r'"uniqueId":"([^"]+)"', html_content)
                        if author_match:
                            metadata['creator'] = author_match.group(1)
                    
                    return metadata
        
        except Exception as e:
            logging.error(f"Error getting TikTok metadata: {str(e)}")
        
        return None
    
    def _calculate_relevance_score(self, content_item: ContentItem, metadata: Optional[Dict], keywords: List[str]) -> float:
        """Calculate relevance score for content"""
        score = 0.0
        
        # Text sources for analysis
        text_sources = []
        
        # Add title
        if content_item.title:
            text_sources.append(('title', content_item.title, 0.3))  # Title weight: 30%
        
        if metadata:
            # Add description
            if metadata.get('description'):
                text_sources.append(('description', metadata['description'], 0.2))  # Description weight: 20%
            
            # Add tags/hashtags
            if metadata.get('tags'):
                tags_text = ' '.join(metadata['tags'])
                text_sources.append(('tags', tags_text, 0.2))  # Tags weight: 20%
            
            # Add comments
            if metadata.get('comments'):
                comments_text = ' '.join(metadata['comments'][:10])  # First 10 comments
                text_sources.append(('comments', comments_text, 0.15))  # Comments weight: 15%
            
            # Add transcript
            if metadata.get('transcript'):
                text_sources.append(('transcript', metadata['transcript'], 0.15))  # Transcript weight: 15%
        
        # Calculate keyword matching scores
        for source_type, text, weight in text_sources:
            if text:
                source_score = self._calculate_text_relevance(text, keywords)
                score += source_score * weight
        
        # Bonus for platform-specific indicators
        platform_bonus = self._get_platform_bonus(content_item, metadata)
        score += platform_bonus
        
        # Penalty for very short content
        if metadata and metadata.get('description'):
            desc_length = len(metadata['description'])
            if desc_length < 20:  # Very short description
                score *= 0.8
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_text_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score for a piece of text"""
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower()
        keyword_matches = 0
        total_keywords = len(keywords)
        
        # Direct keyword matching
        for keyword in keywords:
            if keyword.lower() in text_lower:
                keyword_matches += 1
        
        # Fuzzy matching for similar words
        text_words = re.findall(r'\b\w+\b', text_lower)
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for word in text_words:
                # Use difflib for fuzzy matching
                similarity = difflib.SequenceMatcher(None, keyword_lower, word).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    keyword_matches += 0.5  # Partial match
                    break
        
        # Calculate score
        relevance_score = keyword_matches / total_keywords if total_keywords > 0 else 0
        
        return min(relevance_score, 1.0)
    
    def _get_platform_bonus(self, content_item: ContentItem, metadata: Optional[Dict]) -> float:
        """Get platform-specific bonus points"""
        bonus = 0.0
        
        if content_item.platform == "youtube":
            # Bonus for videos with good engagement indicators
            if metadata and metadata.get('comments'):
                if len(metadata['comments']) > 5:
                    bonus += 0.05
            
            # Bonus for videos with transcripts (usually means they're substantial)
            if metadata and metadata.get('transcript'):
                bonus += 0.05
        
        elif content_item.platform == "instagram":
            # Bonus for posts with hashtags
            if metadata and metadata.get('tags'):
                if len(metadata['tags']) > 3:
                    bonus += 0.05
        
        elif content_item.platform == "tiktok":
            # Bonus for videos with descriptions
            if metadata and metadata.get('description'):
                if len(metadata['description']) > 20:
                    bonus += 0.05
        
        return bonus
    
    async def get_content_quality_metrics(self, content_item: ContentItem) -> Dict:
        """Get quality metrics for a content item"""
        metrics = {
            'relevance_score': getattr(content_item, 'relevance_score', 0),
            'has_transcript': False,
            'comment_count': 0,
            'tag_count': 0,
            'description_length': 0
        }
        
        try:
            metadata = await self._get_content_metadata(content_item)
            
            if metadata:
                metrics['has_transcript'] = bool(metadata.get('transcript'))
                metrics['comment_count'] = len(metadata.get('comments', []))
                metrics['tag_count'] = len(metadata.get('tags', []))
                metrics['description_length'] = len(metadata.get('description', ''))
        
        except Exception as e:
            logging.error(f"Error getting quality metrics: {str(e)}")
        
        return metrics
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())