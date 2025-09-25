"""
Wikipedia Research Module
Handles research and keyword extraction from Wikipedia
"""

import aiohttp
import asyncio
import re
import logging
from typing import List, Dict, Set
from urllib.parse import quote

class WikipediaResearcher:
    """Wikipedia research and keyword extraction with proper error handling"""
    
    def __init__(self):
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def research_topic(self, topic: str) -> List[str]:
        """Research a topic and extract relevant keywords"""
        try:
            # Add small delay to avoid rate limiting
            await asyncio.sleep(0.5)
            
            # Search for the topic
            search_results = await self._search_wikipedia(topic)
            
            if not search_results:
                logging.warning(f"No Wikipedia results found for topic: {topic}")
                # Return topic with common related terms as fallback
                return self._generate_fallback_keywords(topic)
            
            # Get the main article
            main_page = search_results[0]['title']
            article_content = await self._get_article_content(main_page)
            
            # Extract keywords from the article
            keywords = self._extract_keywords(article_content, topic)
            
            # Get related topics
            related_topics = await self._get_related_topics(main_page)
            keywords.extend(related_topics[:10])
            
            # Remove duplicates and return
            unique_keywords = list(set(keywords))
            
            logging.info(f"Extracted {len(unique_keywords)} keywords for topic: {topic}")
            return unique_keywords[:50]
            
        except Exception as e:
            logging.error(f"Error researching topic {topic}: {str(e)}")
            return self._generate_fallback_keywords(topic)
    
    def _generate_fallback_keywords(self, topic: str) -> List[str]:
        """Generate fallback keywords when Wikipedia fails"""
        base_keywords = [topic]
        
        # Add common content-related terms
        content_terms = ['edit', 'compilation', 'moments', 'clips', 'best', 'funny', 'epic', 'memes', 'viral', 'trending']
        for term in content_terms:
            base_keywords.append(f"{topic} {term}")
        
        return base_keywords
    
    async def _search_wikipedia(self, query: str) -> List[Dict]:
        """Search Wikipedia for articles"""
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 5,
            'srprop': 'title|snippet'
        }
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('query', {}).get('search', [])
                else:
                    logging.warning(f"Wikipedia API returned status {response.status}")
                    return []
        except Exception as e:
            logging.error(f"Error searching Wikipedia: {str(e)}")
            return []
    
    async def _get_article_content(self, title: str) -> str:
        """Get the content of a Wikipedia article"""
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'exsectionformat': 'plain'
        }
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get('query', {}).get('pages', {})
                    
                    for page_id, page_data in pages.items():
                        if 'extract' in page_data:
                            return page_data['extract']
                    
                    return ""
                else:
                    logging.warning(f"Wikipedia API returned status {response.status} for article: {title}")
                    return ""
        except Exception as e:
            logging.error(f"Error getting article content: {str(e)}")
            return ""
    
    def _extract_keywords(self, content: str, topic: str) -> List[str]:
        """Extract relevant keywords from article content"""
        if not content:
            return [topic]
        
        keywords = set()
        
        # Add the original topic
        keywords.add(topic.lower())
        
        # Extract proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        keywords.update([noun.lower() for noun in proper_nouns if len(noun) > 2])
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]+)"', content)
        keywords.update([term.lower() for term in quoted_terms if len(term) > 2])
        
        # Extract terms in parentheses
        parentheses_terms = re.findall(r'\(([^)]+)\)', content)
        for term in parentheses_terms:
            if len(term) > 2 and not term.isdigit():
                keywords.add(term.lower())
        
        # Filter out common words
        common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'his', 'her', 'its', 'their', 'our', 'your', 'he', 'she', 'it',
            'they', 'we', 'you', 'who', 'what', 'when', 'where', 'why', 'how',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
            'will', 'just', 'should', 'now', 'may', 'also', 'been', 'have', 'has',
            'had', 'is', 'was', 'are', 'were', 'be', 'being', 'do', 'does', 'did'
        }
        
        filtered_keywords = [
            keyword for keyword in keywords 
            if len(keyword) > 2 and keyword not in common_words
        ]
        
        return filtered_keywords
    
    async def _get_related_topics(self, title: str) -> List[str]:
        """Get related topics/categories from Wikipedia"""
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'categories|links',
            'cllimit': 20,
            'pllimit': 20
        }
        
        related_topics = []
        
        try:
            async with self.session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get('query', {}).get('pages', {})
                    
                    for page_id, page_data in pages.items():
                        # Extract from categories
                        categories = page_data.get('categories', [])
                        for cat in categories:
                            cat_title = cat.get('title', '').replace('Category:', '')
                            if cat_title and len(cat_title) > 2:
                                related_topics.append(cat_title.lower())
                        
                        # Extract from links
                        links = page_data.get('links', [])
                        for link in links[:10]:
                            link_title = link.get('title', '')
                            if link_title and len(link_title) > 2:
                                related_topics.append(link_title.lower())
        
        except Exception as e:
            logging.error(f"Error getting related topics: {str(e)}")
        
        return related_topics