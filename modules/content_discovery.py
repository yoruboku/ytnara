"""
Content Discovery Module
Handles content discovery across YouTube, Instagram, and TikTok platforms
"""

import asyncio
import aiohttp
import re
import json
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import quote, urlencode
from datetime import datetime, timedelta
import random
from dataclasses import dataclass

# Import shared models
from .models import ContentItem

class ContentDiscovery:
    """Content discovery across multiple platforms"""
    
    def __init__(self):
        self.session = None
        self.discovered_urls = set()  # Prevent duplicates
        
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
    
    async def discover_content(self, topic: str, keywords: List[str]) -> List[ContentItem]:
        """Discover content across all platforms"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
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
        content_terms = ['edit', 'compilation', 'moments', 'clips', 'best', 'funny', 'epic']
        for term in content_terms[:3]:  # Limit to avoid too many queries
            queries.append(f"{topic} {term}")
        
        # Add top keywords
        for keyword in keywords[:5]:  # Use top 5 keywords
            if len(keyword) > 3:  # Skip very short keywords
                queries.append(f"{topic} {keyword}")
        
        # Add combined queries
        if len(keywords) >= 2:
            queries.append(f"{topic} {keywords[0]} {keywords[1]}")
        
        return list(set(queries))  # Remove duplicates
    
    async def _discover_youtube_content(self, query: str) -> List[ContentItem]:
        """Discover content from YouTube"""
        content_items = []
        
        try:
            # Use YouTube's search suggestions and trending
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    video_data = self._extract_youtube_videos(html_content, query)
                    content_items.extend(video_data)
            
            # Add small delay to avoid rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Error discovering YouTube content for query '{query}': {str(e)}")
        
        return content_items
    
    def _extract_youtube_videos(self, html_content: str, query: str) -> List[ContentItem]:
        """Extract video information from YouTube HTML"""
        content_items = []
        
        try:
            # Extract video data from YouTube's initial data
            video_pattern = r'{"videoId":"([^"]+)","title":{"runs":\[{"text":"([^"]+)"}.*?"ownerText":{"runs":\[{"text":"([^"]+)"'
            matches = re.findall(video_pattern, html_content)
            
            for video_id, title, channel in matches[:20]:  # Limit to 20 videos per query
                if video_id not in self.discovered_urls:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    content_item = ContentItem(
                        url=url,
                        title=title,
                        platform="youtube",
                        creator=channel,
                        keywords=[query]
                    )
                    
                    content_items.append(content_item)
                    self.discovered_urls.add(video_id)
            
            # Also try alternative pattern for different YouTube layouts
            alt_pattern = r'videoId":"([^"]+)".*?title":"([^"]+)".*?channelName":"([^"]+)"'
            alt_matches = re.findall(alt_pattern, html_content)
            
            for video_id, title, channel in alt_matches[:10]:
                if video_id not in self.discovered_urls:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    content_item = ContentItem(
                        url=url,
                        title=title,
                        platform="youtube",
                        creator=channel,
                        keywords=[query]
                    )
                    
                    content_items.append(content_item)
                    self.discovered_urls.add(video_id)
        
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
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logging.error(f"Error discovering Instagram content for query '{query}': {str(e)}")
        
        return content_items
    
    def _extract_instagram_posts(self, html_content: str, query: str, hashtag: str) -> List[ContentItem]:
        """Extract post information from Instagram HTML"""
        content_items = []
        
        try:
            # Extract post data from Instagram's page data
            # Instagram uses GraphQL, so we look for the data in script tags
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
                                    title = caption_edges[0].get('node', {}).get('text', '')[:100]  # First 100 chars
                                
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
                
                for shortcode in list(set(shortcodes))[:10]:  # Remove duplicates and limit
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
            # TikTok search (limited without API)
            hashtag = query.replace(' ', '').lower()
            search_url = f"https://www.tiktok.com/tag/{hashtag}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    tiktok_data = self._extract_tiktok_videos(html_content, query, hashtag)
                    content_items.extend(tiktok_data)
            
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
            
            for username, video_id in matches[:15]:  # Limit to 15 videos
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
    
    async def get_trending_topics(self, platform: str = "all") -> List[str]:
        """Get trending topics for content discovery"""
        trending_topics = []
        
        try:
            if platform in ["all", "youtube"]:
                youtube_trending = await self._get_youtube_trending()
                trending_topics.extend(youtube_trending)
            
            if platform in ["all", "tiktok"]:
                tiktok_trending = await self._get_tiktok_trending()
                trending_topics.extend(tiktok_trending)
            
        except Exception as e:
            logging.error(f"Error getting trending topics: {str(e)}")
        
        return list(set(trending_topics))  # Remove duplicates
    
    async def _get_youtube_trending(self) -> List[str]:
        """Get trending topics from YouTube"""
        try:
            trending_url = "https://www.youtube.com/feed/trending"
            
            async with self.session.get(trending_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Extract video titles from trending page
                    title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"}'
                    titles = re.findall(title_pattern, html_content)
                    
                    # Extract keywords from titles
                    keywords = []
                    for title in titles[:20]:  # Top 20 trending videos
                        words = re.findall(r'\b[A-Za-z]{3,}\b', title)
                        keywords.extend(words)
                    
                    return list(set([kw.lower() for kw in keywords]))[:10]
        
        except Exception as e:
            logging.error(f"Error getting YouTube trending: {str(e)}")
        
        return []
    
    async def _get_tiktok_trending(self) -> List[str]:
        """Get trending hashtags from TikTok"""
        try:
            # TikTok trending is harder to scrape, so we'll use common trending topics
            common_trending = [
                'fyp', 'viral', 'trending', 'funny', 'comedy', 'dance', 'music',
                'lifestyle', 'food', 'travel', 'fashion', 'beauty', 'fitness'
            ]
            
            return common_trending
        
        except Exception as e:
            logging.error(f"Error getting TikTok trending: {str(e)}")
        
        return []
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())