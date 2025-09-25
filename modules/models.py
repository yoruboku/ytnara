"""
Shared Data Models
Contains shared data classes to avoid circular imports
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContentItem:
    """Represents a piece of content to be processed"""
    url: str
    title: str
    platform: str
    creator: str
    keywords: List[str]
    downloaded_path: Optional[str] = None
    edited_path: Optional[str] = None
    uploaded_platforms: Optional[List[str]] = None
    relevance_score: float = 0.0
    duration: Optional[float] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    comments: Optional[List[str]] = None
    transcript: Optional[str] = None
    
    def __post_init__(self):
        if self.uploaded_platforms is None:
            self.uploaded_platforms = []
        if self.tags is None:
            self.tags = []
        if self.comments is None:
            self.comments = []