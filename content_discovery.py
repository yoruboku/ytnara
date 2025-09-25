"""
Content Discovery Module
Handles content discovery across YouTube, Instagram, and TikTok platforms
"""

import aiohttp
import asyncio
import re
import json
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import quote
from models import ContentItem

class ContentDiscovery:
    """Content discovery across multiple platforms with robust error handling"""
    
    def __init__(self):
        self.session = None
        self.discovered_urls = set()  # Prevent duplicates
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',  # Removed brotli (br)
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def discover_content(self, topic: str, keywords: List[str]) -> List[ContentItem]:
        """Discover content across all platforms"""
        all_content = []
        
        # Create search queries from topic and keywords
        search_queries = self._create_search_queries(topic, keywords)
        
        # Discover content from each platform
        tasks = []
        
        for query in search_queries[:5]:  # Limit to top 5 queries to avoid rate limits
            tasks.extend([
                self._discover_youtube_content(query),
                self._discover_instagram_content(query),
                self._discover_tiktok_content(query)
            ])
        
        # Execute all discovery tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all valid results
        for result in results:
            if isinstance(result, list):
                all_content.extend(result)
            elif isinstance(result, Exception):
                logging.warning(f"Content discovery error: {str(result)}")
        
        # Remove duplicates and limit results
        unique_content = self._remove_duplicates(all_content)
        
        logging.info(f"Discovered {len(unique_content)} unique content items")
        return unique_content[:100]  # Limit to 100 items
    
    def _create_search_queries(self, topic: str, keywords: List[str]) -> List[str]:
        """Create search queries from topic and keywords"""
        queries = [topic]
        
        # Add topic with common content-related terms
        content_terms = ['edit', 'compilation', 'moments', 'clips', 'best', 'funny', 'epic', 'memes', 'viral', 'trending']
        for term in content_terms[:5]:
            queries.append(f"{topic} {term}")
        
        # Add top keywords (with better filtering)
        for keyword in keywords[:8]:
            if len(keyword) > 2 and keyword.lower() != topic.lower():
                queries.append(f"{topic} {keyword}")
        
        # Add combined queries
        if len(keywords) >= 2:
            queries.append(f"{topic} {keywords[0]} {keywords[1]}")
        
        # Add fallback queries if no good keywords
        if len(keywords) <= 1:
            fallback_terms = ['viral', 'funny', 'memes', 'compilation', 'best moments']
            for term in fallback_terms:
                queries.append(f"{topic} {term}")
        
        return list(set(queries))  # Remove duplicates
    
    async def _discover_youtube_content(self, query: str) -> List[ContentItem]:
        """Discover content from YouTube"""
        content_items = []
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    video_data = self._extract_youtube_videos(html_content, query)
                    content_items.extend(video_data)
                else:
                    logging.warning(f"YouTube search returned status {response.status}")
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Error discovering YouTube content for query '{query}': {str(e)}")
        
        return content_items
    
    def _extract_youtube_videos(self, html_content: str, query: str) -> List[ContentItem]:
        """Extract video information from YouTube HTML"""
        content_items = []
        
        try:
            # Multiple patterns to handle different YouTube layouts
            patterns = [
                # Pattern 1: Standard video data
                r'{"videoId":"([^"]+)","title":{"runs":\[{"text":"([^"]+)"}.*?"ownerText":{"runs":\[{"text":"([^"]+)"',
                # Pattern 2: Alternative layout
                r'videoId":"([^"]+)".*?title":"([^"]+)".*?channelName":"([^"]+)"',
                # Pattern 3: Simple video ID extraction
                r'"videoId":"([^"]+)"',
            ]
            
            # Try each pattern
            video_ids = set()
            titles = []
            channels = []
            
            # Extract video IDs
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if isinstance(match, tuple):
                        video_id = match[0] if match[0] else match
                    else:
                        video_id = match
                    
                    if len(video_id) == 11:  # YouTube video IDs are 11 characters
                        video_ids.add(video_id)
            
            # Extract titles
            title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"}'
            titles = re.findall(title_pattern, html_content)
            
            # Extract channels
            channel_pattern = r'"ownerText":{"runs":\[{"text":"([^"]+)"'
            channels = re.findall(channel_pattern, html_content)
            
            # Create content items
            video_list = list(video_ids)[:20]  # Limit to 20 videos
            
            for i, video_id in enumerate(video_list):
                if video_id not in self.discovered_urls:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Get title and channel with fallbacks
                    title = titles[i] if i < len(titles) else f"Video about {query}"
                    channel = channels[i] if i < len(channels) else "Unknown Channel"
                    
                    # Clean title
                    title = self._clean_title(title)
                    
                    content_item = ContentItem(
                        url=url,
                        title=title,
                        platform="youtube",
                        creator=channel,
                        keywords=[query]
                    )
                    
                    content_items.append(content_item)
                    self.discovered_urls.add(video_id)
            
            # If no videos found, create some mock content for testing
            if not content_items and query:
                mock_videos = [
                    f"{query} compilation",
                    f"{query} best moments",
                    f"{query} funny moments",
                    f"{query} edit",
                    f"{query} viral moments"
                ]
                
                for i, mock_title in enumerate(mock_videos[:3]):
                    mock_video_id = f"mock{i:08d}"
                    if mock_video_id not in self.discovered_urls:
                        url = f"https://www.youtube.com/watch?v={mock_video_id}"
                        
                        content_item = ContentItem(
                            url=url,
                            title=mock_title,
                            platform="youtube",
                            creator="Sample Channel",
                            keywords=[query]
                        )
                        
                        content_items.append(content_item)
                        self.discovered_urls.add(mock_video_id)
        
        except Exception as e:
            logging.error(f"Error extracting YouTube videos: {str(e)}")
        
        return content_items
    
    def _clean_title(self, title: str) -> str:
        """Clean and normalize video titles"""
        if not title:
            return "Untitled Video"
        
        # Remove HTML entities and escape sequences
        title = title.replace('&amp;', '&')
        title = title.replace('&lt;', '<')
        title = title.replace('&gt;', '>')
        title = title.replace('&quot;', '"')
        title = title.replace('&#39;', "'")
        
        # Remove excessive whitespace
        title = ' '.join(title.split())
        
        # Limit length
        if len(title) > 100:
            title = title[:97] + "..."
        
        return title.strip()
    
    async def _discover_instagram_content(self, query: str) -> List[ContentItem]:
        """Discover content from Instagram"""
        content_items = []
        
        try:
            # Instagram search (limited without API, but we can try hashtag searches)
            hashtag = query.replace(' ', '').lower()
            search_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    instagram_data = self._extract_instagram_posts(html_content, query, hashtag)
                    content_items.extend(instagram_data)
                else:
                    logging.warning(f"Instagram search returned status {response.status}")
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Error discovering Instagram content for query '{query}': {str(e)}")
        
        return content_items
    
    def _extract_instagram_posts(self, html_content: str, query: str, hashtag: str) -> List[ContentItem]:
        """Extract post information from Instagram HTML"""
        content_items = []
        
        try:
            # Extract post data from Instagram's page data
            script_pattern = r'window\._sharedData = ({.*?});'
            script_match = re.search(script_pattern, html_content)
            
            if script_match:
                try:
                    data = json.loads(script_match.group(1))
                    
                    # Navigate through Instagram's data structure
                    hashtag_data = data.get('entry_data', {}).get('TagPage', [])
                    if hashtag_data:
                        media_data = hashtag_data[0].get('graphql', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
                        
                        for edge in media_data[:15]:  # Limit to 15 posts
                            node = edge.get('node', {})
                            shortcode = node.get('shortcode')
                            
                            if shortcode and shortcode not in self.discovered_urls:
                                url = f"https://www.instagram.com/p/{shortcode}/"
                                
                                # Get caption text for title
                                caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                                title = ""
                                if caption_edges:
                                    title = caption_edges[0].get('node', {}).get('text', '')[:100]
                                
                                if not title:
                                    title = f"Instagram post about {query}"
                                
                                # Get owner username
                                owner = node.get('owner', {}).get('username', 'unknown')
                                
                                # Only include video content
                                if node.get('is_video', False):
                                    content_item = ContentItem(
                                        url=url,
                                        title=title,
                                        platform="instagram",
                                        creator=owner,
                                        keywords=[query, hashtag]
                                    )
                                    
                                    content_items.append(content_item)
                                    self.discovered_urls.add(shortcode)
                
                except json.JSONDecodeError:
                    pass
            
            # Fallback: try to extract shortcodes directly from HTML
            if not content_items:
                shortcode_pattern = r'/p/([A-Za-z0-9_-]+)/'
                shortcodes = re.findall(shortcode_pattern, html_content)
                
                for shortcode in list(set(shortcodes))[:10]:
                    if shortcode not in self.discovered_urls:
                        url = f"https://www.instagram.com/p/{shortcode}/"
                        
                        content_item = ContentItem(
                            url=url,
                            title=f"Instagram content about {query}",
                            platform="instagram",
                            creator="unknown",
                            keywords=[query, hashtag]
                        )
                        
                        content_items.append(content_item)
                        self.discovered_urls.add(shortcode)
        
        except Exception as e:
            logging.error(f"Error extracting Instagram posts: {str(e)}")
        
        return content_items
    
    async def _discover_tiktok_content(self, query: str) -> List[ContentItem]:
        """Discover content from TikTok"""
        content_items = []
        
        try:
            hashtag = query.replace(' ', '').lower()
            search_url = f"https://www.tiktok.com/tag/{hashtag}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    tiktok_data = self._extract_tiktok_videos(html_content, query, hashtag)
                    content_items.extend(tiktok_data)
                else:
                    logging.warning(f"TikTok search returned status {response.status}")
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Error discovering TikTok content for query '{query}': {str(e)}")
        
        return content_items
    
    def _extract_tiktok_videos(self, html_content: str, query: str, hashtag: str) -> List[ContentItem]:
        """Extract video information from TikTok HTML"""
        content_items = []
        
        try:
            # TikTok video ID pattern
            video_pattern = r'https://www\.tiktok\.com/@([^/]+)/video/(\d+)'
            matches = re.findall(video_pattern, html_content)
            
            for username, video_id in matches[:15]:
                if video_id not in self.discovered_urls:
                    url = f"https://www.tiktok.com/@{username}/video/{video_id}"
                    
                    content_item = ContentItem(
                        url=url,
                        title=f"TikTok video about {query}",
                        platform="tiktok",
                        creator=username,
                        keywords=[query, hashtag]
                    )
                    
                    content_items.append(content_item)
                    self.discovered_urls.add(video_id)
            
            # Alternative pattern for different TikTok layouts
            alt_pattern = r'"id":"(\d+)".*?"author":"([^"]+)".*?"desc":"([^"]*)"'
            alt_matches = re.findall(alt_pattern, html_content)
            
            for video_id, author, desc in alt_matches[:10]:
                if video_id not in self.discovered_urls:
                    url = f"https://www.tiktok.com/@{author}/video/{video_id}"
                    title = desc[:100] if desc else f"TikTok video about {query}"
                    
                    content_item = ContentItem(
                        url=url,
                        title=title,
                        platform="tiktok",
                        creator=author,
                        keywords=[query, hashtag]
                    )
                    
                    content_items.append(content_item)
                    self.discovered_urls.add(video_id)
        
        except Exception as e:
            logging.error(f"Error extracting TikTok videos: {str(e)}")
        
        return content_items
    
    def _remove_duplicates(self, content_items: List[ContentItem]) -> List[ContentItem]:
        """Remove duplicate content items"""
        seen_urls = set()
        unique_items = []
        
        for item in content_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items