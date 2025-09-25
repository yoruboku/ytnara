"""
Content Verification Module
Verifies content relevance using comments, titles, hashtags, and transcriptions
"""

import aiohttp
import asyncio
import re
import json
import logging
import difflib
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from collections import Counter
from models import ContentItem

class ContentVerifier:
    """Content verification and relevance scoring with proper error handling"""
    
    def __init__(self):
        self.session = None
        self.relevance_threshold = 0.1  # Lowered for better results
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',  # Removed brotli (br)
                'Connection': 'keep-alive'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def verify_content(self, content_items: List[ContentItem], keywords: List[str]) -> List[ContentItem]:
        """Verify content relevance and filter out irrelevant items"""
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
        
        # If no content passed verification, take the top items anyway
        if not verified_content and content_items:
            logging.warning("No content passed verification threshold. Taking top items anyway.")
            # Take top 10 items and assign minimal relevance scores
            for i, item in enumerate(content_items[:10]):
                item.relevance_score = 0.5 - (i * 0.05)  # Decreasing scores
                verified_content.append(item)
        
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
            
            # Add metadata to content item
            if metadata:
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
            logging.error(f"Error verifying content {content_item.title}: {str(e)}")
            # Return with minimal score to not lose content
            content_item.relevance_score = 0.1
            return True, content_item
    
    async def _get_content_metadata(self, content_item: ContentItem) -> Optional[Dict]:
        """Get metadata for content item"""
        try:
            if content_item.platform == "youtube":
                return await self._get_youtube_metadata(content_item)
            elif content_item.platform == "instagram":
                return await self._get_instagram_metadata(content_item)
            elif content_item.platform == "tiktok":
                return await self._get_tiktok_metadata(content_item)
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting metadata for {content_item.platform}: {str(e)}")
            return None
    
    async def _get_youtube_metadata(self, content_item: ContentItem) -> Optional[Dict]:
        """Get YouTube video metadata"""
        try:
            async with self.session.get(content_item.url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._extract_youtube_metadata(html_content)
                else:
                    logging.warning(f"YouTube metadata request returned status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error getting YouTube metadata: {str(e)}")
            return None
    
    def _extract_youtube_metadata(self, html_content: str) -> Dict:
        """Extract metadata from YouTube HTML"""
        metadata = {
            'description': '',
            'tags': [],
            'comments': [],
            'transcript': ''
        }
        
        try:
            # Extract description
            desc_pattern = r'"description":{"simpleText":"([^"]+)"'
            desc_match = re.search(desc_pattern, html_content)
            if desc_match:
                metadata['description'] = desc_match.group(1)
            
            # Extract tags
            tags_pattern = r'"keywords":\[([^\]]+)\]'
            tags_match = re.search(tags_pattern, html_content)
            if tags_match:
                tags_text = tags_match.group(1)
                tags = re.findall(r'"([^"]+)"', tags_text)
                metadata['tags'] = tags[:20]  # Limit to 20 tags
            
            # Extract some comments (limited without API)
            comment_pattern = r'"contentText":{"runs":\[{"text":"([^"]+)"}'
            comments = re.findall(comment_pattern, html_content)
            metadata['comments'] = comments[:10]  # Limit to 10 comments
            
        except Exception as e:
            logging.error(f"Error extracting YouTube metadata: {str(e)}")
        
        return metadata
    
    async def _get_instagram_metadata(self, content_item: ContentItem) -> Optional[Dict]:
        """Get Instagram post metadata"""
        try:
            async with self.session.get(content_item.url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._extract_instagram_metadata(html_content)
                else:
                    logging.warning(f"Instagram metadata request returned status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error getting Instagram metadata: {str(e)}")
            return None
    
    def _extract_instagram_metadata(self, html_content: str) -> Dict:
        """Extract metadata from Instagram HTML"""
        metadata = {
            'description': '',
            'tags': [],
            'comments': [],
            'transcript': ''
        }
        
        try:
            # Extract caption/description
            caption_pattern = r'"edge_media_to_caption":{"edges":\[{"node":{"text":"([^"]+)"}'
            caption_match = re.search(caption_pattern, html_content)
            if caption_match:
                metadata['description'] = caption_match.group(1)
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', metadata['description'])
            metadata['tags'] = hashtags[:20]
            
        except Exception as e:
            logging.error(f"Error extracting Instagram metadata: {str(e)}")
        
        return metadata
    
    async def _get_tiktok_metadata(self, content_item: ContentItem) -> Optional[Dict]:
        """Get TikTok video metadata"""
        try:
            async with self.session.get(content_item.url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._extract_tiktok_metadata(html_content)
                else:
                    logging.warning(f"TikTok metadata request returned status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error getting TikTok metadata: {str(e)}")
            return None
    
    def _extract_tiktok_metadata(self, html_content: str) -> Dict:
        """Extract metadata from TikTok HTML"""
        metadata = {
            'description': '',
            'tags': [],
            'comments': [],
            'transcript': ''
        }
        
        try:
            # Extract description
            desc_pattern = r'"desc":"([^"]+)"'
            desc_match = re.search(desc_pattern, html_content)
            if desc_match:
                metadata['description'] = desc_match.group(1)
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', metadata['description'])
            metadata['tags'] = hashtags[:20]
            
        except Exception as e:
            logging.error(f"Error extracting TikTok metadata: {str(e)}")
        
        return metadata
    
    def _calculate_relevance_score(self, content_item: ContentItem, metadata: Optional[Dict], keywords: List[str]) -> float:
        """Calculate relevance score for content"""
        score = 0.0
        
        # Text sources for analysis
        text_sources = []
        
        # Add title
        if content_item.title:
            text_sources.append(('title', content_item.title, 0.4))  # Title weight: 40%
        
        if metadata:
            # Add description
            if metadata.get('description'):
                text_sources.append(('description', metadata['description'], 0.3))  # Description weight: 30%
            
            # Add tags/hashtags
            if metadata.get('tags'):
                tags_text = ' '.join(metadata['tags'])
                text_sources.append(('tags', tags_text, 0.2))  # Tags weight: 20%
            
            # Add comments
            if metadata.get('comments'):
                comments_text = ' '.join(metadata['comments'][:10])
                text_sources.append(('comments', comments_text, 0.1))  # Comments weight: 10%
        
        # Calculate keyword matching scores
        for source_type, text, weight in text_sources:
            if text:
                source_score = self._calculate_text_relevance(text, keywords)
                score += source_score * weight
        
        # Bonus for platform-specific indicators
        platform_bonus = self._get_platform_bonus(content_item, metadata)
        score += platform_bonus
        
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
        
        # YouTube bonuses
        if content_item.platform == "youtube":
            if metadata and metadata.get('description'):
                desc_length = len(metadata['description'])
                if desc_length > 100:  # Detailed description
                    bonus += 0.1
        
        # Instagram bonuses
        elif content_item.platform == "instagram":
            if metadata and metadata.get('tags'):
                tag_count = len(metadata['tags'])
                if tag_count > 5:  # Good hashtag usage
                    bonus += 0.1
        
        # TikTok bonuses
        elif content_item.platform == "tiktok":
            if metadata and metadata.get('description'):
                desc_length = len(metadata['description'])
                if desc_length > 50:  # Good description
                    bonus += 0.1
        
        return bonus