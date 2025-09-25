"""
Database Module
Handles data persistence and duplicate prevention
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

# Import shared models
from .models import ContentItem

class ContentDatabase:
    """Database for tracking processed content and preventing duplicates"""
    
    def __init__(self, db_path: str = "data/content.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self._processed_urls: Set[str] = set()
        self._load_processed_urls()
    
    def _init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS processed_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    url_hash TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    creator TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    downloaded_path TEXT,
                    edited_path TEXT,
                    uploaded_platforms TEXT,
                    relevance_score REAL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER,
                    platform_account TEXT NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    FOREIGN KEY (content_id) REFERENCES processed_content (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    discovered_count INTEGER DEFAULT 0,
                    verified_count INTEGER DEFAULT 0,
                    downloaded_count INTEGER DEFAULT 0,
                    edited_count INTEGER DEFAULT 0,
                    uploaded_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    session_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON processed_content (url_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_platform ON processed_content (platform)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_processed_at ON processed_content (processed_at)')
            
            conn.commit()
    
    def _load_processed_urls(self):
        """Load processed URLs into memory for fast duplicate checking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT url FROM processed_content')
                self._processed_urls = {row[0] for row in cursor.fetchall()}
                
                logging.info(f"Loaded {len(self._processed_urls)} processed URLs from database")
        except Exception as e:
            logging.error(f"Error loading processed URLs: {str(e)}")
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate a hash for the URL for duplicate detection"""
        # Normalize URL for better duplicate detection
        normalized_url = url.lower().strip()
        
        # Remove common URL parameters that don't affect content
        if '?' in normalized_url:
            base_url = normalized_url.split('?')[0]
        else:
            base_url = normalized_url
        
        return hashlib.sha256(base_url.encode()).hexdigest()
    
    def is_duplicate(self, url: str) -> bool:
        """Check if content has already been processed"""
        return url in self._processed_urls
    
    def save_processed_content(self, content_item) -> bool:
        """Save processed content to database"""
        try:
            if self.is_duplicate(content_item.url):
                logging.warning(f"Content already processed: {content_item.url}")
                return False
            
            url_hash = self._generate_url_hash(content_item.url)
            keywords_json = json.dumps(content_item.keywords)
            uploaded_platforms_json = json.dumps(content_item.uploaded_platforms or [])
            relevance_score = getattr(content_item, 'relevance_score', 0.0)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO processed_content 
                    (url, url_hash, title, platform, creator, keywords, 
                     downloaded_path, edited_path, uploaded_platforms, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content_item.url,
                    url_hash,
                    content_item.title,
                    content_item.platform,
                    content_item.creator,
                    keywords_json,
                    content_item.downloaded_path,
                    content_item.edited_path,
                    uploaded_platforms_json,
                    relevance_score
                ))
                
                content_id = cursor.lastrowid
                conn.commit()
                
                # Add to in-memory set
                self._processed_urls.add(content_item.url)
                
                logging.info(f"Saved processed content: {content_item.title}")
                return True
                
        except sqlite3.IntegrityError as e:
            logging.warning(f"Content already exists in database: {content_item.url}")
            return False
        except Exception as e:
            logging.error(f"Error saving processed content: {str(e)}")
            return False
    
    def log_upload_attempt(self, content_url: str, platform_account: str, success: bool, error_message: str = None):
        """Log an upload attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get content ID
                cursor = conn.execute('SELECT id FROM processed_content WHERE url = ?', (content_url,))
                result = cursor.fetchone()
                
                if result:
                    content_id = result[0]
                    
                    conn.execute('''
                        INSERT INTO upload_history 
                        (content_id, platform_account, success, error_message)
                        VALUES (?, ?, ?, ?)
                    ''', (content_id, platform_account, success, error_message))
                    
                    conn.commit()
                    
        except Exception as e:
            logging.error(f"Error logging upload attempt: {str(e)}")
    
    def get_processed_content(self, limit: int = 100, platform: str = None) -> List[Dict]:
        """Get processed content from database"""
        try:
            query = '''
                SELECT url, title, platform, creator, keywords, 
                       downloaded_path, edited_path, uploaded_platforms,
                       relevance_score, processed_at, status
                FROM processed_content
            '''
            params = []
            
            if platform:
                query += ' WHERE platform = ?'
                params.append(platform)
            
            query += ' ORDER BY processed_at DESC LIMIT ?'
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'url': row[0],
                        'title': row[1],
                        'platform': row[2],
                        'creator': row[3],
                        'keywords': json.loads(row[4]),
                        'downloaded_path': row[5],
                        'edited_path': row[6],
                        'uploaded_platforms': json.loads(row[7]) if row[7] else [],
                        'relevance_score': row[8],
                        'processed_at': row[9],
                        'status': row[10]
                    })
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting processed content: {str(e)}")
            return []
    
    def get_upload_history(self, limit: int = 100) -> List[Dict]:
        """Get upload history"""
        try:
            query = '''
                SELECT pc.title, pc.platform, uh.platform_account, 
                       uh.upload_time, uh.success, uh.error_message
                FROM upload_history uh
                JOIN processed_content pc ON uh.content_id = pc.id
                ORDER BY uh.upload_time DESC
                LIMIT ?
            '''
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'title': row[0],
                        'platform': row[1],
                        'platform_account': row[2],
                        'upload_time': row[3],
                        'success': bool(row[4]),
                        'error_message': row[5]
                    })
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting upload history: {str(e)}")
            return []
    
    def get_statistics(self, days: int = 7) -> Dict[str, int]:
        """Get processing statistics for the last N days"""
        try:
            query = '''
                SELECT 
                    COUNT(*) as total_processed,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    AVG(relevance_score) as avg_relevance
                FROM processed_content 
                WHERE processed_at >= datetime('now', '-{} days')
            '''.format(days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query)
                row = cursor.fetchone()
                
                if row:
                    return {
                        'total_processed': row[0] or 0,
                        'completed': row[1] or 0,
                        'failed': row[2] or 0,
                        'avg_relevance': round(row[3] or 0, 2)
                    }
                
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
        
        return {
            'total_processed': 0,
            'completed': 0,
            'failed': 0,
            'avg_relevance': 0.0
        }
    
    def get_platform_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get statistics by platform"""
        try:
            query = '''
                SELECT platform, 
                       COUNT(*) as total,
                       AVG(relevance_score) as avg_relevance
                FROM processed_content 
                GROUP BY platform
            '''
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query)
                
                results = {}
                for row in cursor.fetchall():
                    results[row[0]] = {
                        'total': row[1],
                        'avg_relevance': round(row[2] or 0, 2)
                    }
                
                return results
                
        except Exception as e:
            logging.error(f"Error getting platform statistics: {str(e)}")
            return {}
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up old records older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete old upload history
                cursor = conn.execute('''
                    DELETE FROM upload_history 
                    WHERE upload_time < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_uploads = cursor.rowcount
                
                # Delete old content stats
                cursor = conn.execute('''
                    DELETE FROM content_stats 
                    WHERE session_date < date('now', '-{} days')
                '''.format(days))
                
                deleted_stats = cursor.rowcount
                
                conn.commit()
                
                total_deleted = deleted_uploads + deleted_stats
                logging.info(f"Cleaned up {total_deleted} old records")
                
                return total_deleted
                
        except Exception as e:
            logging.error(f"Error cleaning up old records: {str(e)}")
            return 0
    
    def export_data(self, output_file: str) -> bool:
        """Export all data to JSON file"""
        try:
            data = {
                'processed_content': self.get_processed_content(limit=10000),
                'upload_history': self.get_upload_history(limit=10000),
                'statistics': self.get_statistics(days=365),
                'platform_statistics': self.get_platform_statistics(),
                'export_date': datetime.now().isoformat()
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.info(f"Data exported to {output_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            return False
    
    def get_duplicate_count(self) -> int:
        """Get the number of processed URLs (for duplicate prevention)"""
        return len(self._processed_urls)
    
    def clear_all_data(self):
        """Clear all data (use with caution!)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM upload_history')
                conn.execute('DELETE FROM content_stats')
                conn.execute('DELETE FROM processed_content')
                conn.commit()
            
            self._processed_urls.clear()
            logging.warning("All data cleared from database")
            
        except Exception as e:
            logging.error(f"Error clearing data: {str(e)}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        # Nothing specific to cleanup for SQLite