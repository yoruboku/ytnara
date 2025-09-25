"""
Database Module
Handles data persistence and duplicate prevention
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import ContentItem

class Database:
    """Database manager for content tracking and duplicate prevention"""
    
    def __init__(self, db_path: str = "data/content.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create processed_content table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processed_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        creator TEXT,
                        keywords TEXT,
                        downloaded_path TEXT,
                        edited_path TEXT,
                        uploaded_platforms TEXT,
                        duration INTEGER,
                        view_count INTEGER,
                        upload_date TEXT,
                        relevance_score REAL DEFAULT 0.0,
                        description TEXT,
                        tags TEXT,
                        comments TEXT,
                        transcript TEXT,
                        discovered_at TEXT,
                        processed_at TEXT,
                        status TEXT DEFAULT 'discovered'
                    )
                ''')
                
                # Create upload_history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS upload_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER,
                        platform TEXT NOT NULL,
                        account TEXT NOT NULL,
                        uploaded_at TEXT,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY (content_id) REFERENCES processed_content (id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
    
    def save_content(self, content_item: ContentItem) -> bool:
        """Save content item to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert lists to JSON strings
                keywords_json = json.dumps(content_item.keywords)
                uploaded_platforms_json = json.dumps(content_item.uploaded_platforms)
                tags_json = json.dumps(content_item.tags)
                comments_json = json.dumps(content_item.comments)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO processed_content 
                    (url, title, platform, creator, keywords, downloaded_path, edited_path,
                     uploaded_platforms, duration, view_count, upload_date, relevance_score,
                     description, tags, comments, transcript, discovered_at, processed_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content_item.url,
                    content_item.title,
                    content_item.platform,
                    content_item.creator,
                    keywords_json,
                    content_item.downloaded_path,
                    content_item.edited_path,
                    uploaded_platforms_json,
                    content_item.duration,
                    content_item.view_count,
                    content_item.upload_date,
                    content_item.relevance_score,
                    content_item.description,
                    tags_json,
                    comments_json,
                    content_item.transcript,
                    content_item.discovered_at.isoformat(),
                    content_item.processed_at.isoformat() if content_item.processed_at else None,
                    'completed' if content_item.processed_at else 'discovered'
                ))
                
                conn.commit()
                logging.info(f"Saved content to database: {content_item.title}")
                return True
                
        except Exception as e:
            logging.error(f"Error saving content to database: {str(e)}")
            return False
    
    def get_content_by_url(self, url: str) -> Optional[ContentItem]:
        """Get content item by URL"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM processed_content WHERE url = ?', (url,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_content_item(row)
                return None
                
        except Exception as e:
            logging.error(f"Error getting content by URL: {str(e)}")
            return None
    
    def is_url_processed(self, url: str) -> bool:
        """Check if URL has been processed"""
        return self.get_content_by_url(url) is not None
    
    def get_unprocessed_content(self, limit: int = 100) -> List[ContentItem]:
        """Get unprocessed content items"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM processed_content 
                    WHERE status = 'discovered' 
                    ORDER BY discovered_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [self._row_to_content_item(row) for row in rows]
                
        except Exception as e:
            logging.error(f"Error getting unprocessed content: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total processed
                cursor.execute('SELECT COUNT(*) FROM processed_content')
                total_processed = cursor.fetchone()[0]
                
                # Completed
                cursor.execute('SELECT COUNT(*) FROM processed_content WHERE status = "completed"')
                completed = cursor.fetchone()[0]
                
                # Failed
                cursor.execute('SELECT COUNT(*) FROM processed_content WHERE status = "failed"')
                failed = cursor.fetchone()[0]
                
                # Average relevance score
                cursor.execute('SELECT AVG(relevance_score) FROM processed_content WHERE relevance_score > 0')
                avg_relevance = cursor.fetchone()[0] or 0
                
                # Platform statistics
                cursor.execute('''
                    SELECT platform, COUNT(*) 
                    FROM processed_content 
                    GROUP BY platform
                ''')
                platform_stats = dict(cursor.fetchall())
                
                return {
                    'total_processed': total_processed,
                    'completed': completed,
                    'failed': failed,
                    'avg_relevance': round(avg_relevance, 2),
                    'platform_stats': platform_stats
                }
                
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def _row_to_content_item(self, row: tuple) -> ContentItem:
        """Convert database row to ContentItem"""
        content_item = ContentItem(
            url=row[1],
            title=row[2],
            platform=row[3],
            creator=row[4] or "Unknown",
            keywords=json.loads(row[5]) if row[5] else [],
            downloaded_path=row[6],
            edited_path=row[7],
            uploaded_platforms=json.loads(row[8]) if row[8] else [],
            duration=row[9],
            view_count=row[10],
            upload_date=row[11],
            relevance_score=row[12] or 0.0,
            description=row[13],
            tags=json.loads(row[14]) if row[14] else [],
            comments=json.loads(row[15]) if row[15] else [],
            transcript=row[16]
        )
        
        # Parse timestamps
        if row[17]:
            content_item.discovered_at = datetime.fromisoformat(row[17])
        if row[18]:
            content_item.processed_at = datetime.fromisoformat(row[18])
        
        return content_item