"""
Shared data models for YT-Nara
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ContentItem:
    """Represents a piece of content to be processed"""
    url: str
    title: str
    platform: str
    creator: str
    keywords: List[str] = field(default_factory=list)
    
    # Processing status
    downloaded_path: Optional[str] = None
    edited_path: Optional[str] = None
    uploaded_platforms: List[str] = field(default_factory=list)
    
    # Metadata
    duration: Optional[int] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    relevance_score: float = 0.0
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    transcript: Optional[str] = None
    
    # Processing timestamps
    discovered_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'url': self.url,
            'title': self.title,
            'platform': self.platform,
            'creator': self.creator,
            'keywords': self.keywords,
            'downloaded_path': self.downloaded_path,
            'edited_path': self.edited_path,
            'uploaded_platforms': self.uploaded_platforms,
            'duration': self.duration,
            'view_count': self.view_count,
            'upload_date': self.upload_date,
            'relevance_score': self.relevance_score,
            'description': self.description,
            'tags': self.tags,
            'comments': self.comments,
            'transcript': self.transcript,
            'discovered_at': self.discovered_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create from dictionary"""
        item = cls(
            url=data['url'],
            title=data['title'],
            platform=data['platform'],
            creator=data['creator'],
            keywords=data.get('keywords', []),
            downloaded_path=data.get('downloaded_path'),
            edited_path=data.get('edited_path'),
            uploaded_platforms=data.get('uploaded_platforms', []),
            duration=data.get('duration'),
            view_count=data.get('view_count'),
            upload_date=data.get('upload_date'),
            relevance_score=data.get('relevance_score', 0.0),
            description=data.get('description'),
            tags=data.get('tags', []),
            comments=data.get('comments', []),
            transcript=data.get('transcript')
        )
        
        if data.get('discovered_at'):
            item.discovered_at = datetime.fromisoformat(data['discovered_at'])
        if data.get('processed_at'):
            item.processed_at = datetime.fromisoformat(data['processed_at'])
            
        return item