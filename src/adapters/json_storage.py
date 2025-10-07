"""
JSON storage adapter - persists article data and bot state.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any
import os

from src.domain import Article, PostedArticle
from src.adapters.interfaces import ArticleStorage, StorageError

logger = logging.getLogger(__name__)


class JSONStorage(ArticleStorage):
    """JSON file-based storage for article data."""
    
    def __init__(self, filepath: str = "posted_articles.json"):
        """
        Initialize JSON storage.
        
        Args:
            filepath: Path to JSON storage file
        """
        self.filepath = Path(filepath)
        self._data: Optional[dict] = None
    
    @property
    def data(self) -> dict:
        """Lazy-load storage data."""
        if self._data is None:
            self._data = self._load_data()
        return self._data
    
    def _load_data(self) -> dict:
        """Load data from JSON file."""
        if not self.filepath.exists():
            logger.info(f"Storage file not found, creating: {self.filepath}")
            return {
                "posted_articles": [],
                "posted_uris": [],
                "queue": [],
                "posted_articles_history": []
            }
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Ensure required keys exist
            data.setdefault("posted_articles", [])
            data.setdefault("posted_uris", [])
            data.setdefault("queue", [])
            data.setdefault("posted_articles_history", [])
            
            logger.info(f"Loaded storage: {len(data['posted_uris'])} posted, {len(data['queue'])} queued")
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load storage: {e}")
            raise StorageError(f"Failed to load storage from {self.filepath}: {e}") from e
    
    def _save_data(self) -> bool:
        """Save data to JSON file."""
        try:
            # Create backup
            if self.filepath.exists():
                backup_path = self.filepath.with_suffix('.json.backup')
                self.filepath.replace(backup_path)
            
            # Write new data atomically
            temp_path = self.filepath.with_suffix('.json.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            
            # Atomic replace
            temp_path.replace(self.filepath)
            
            logger.info(f"Saved storage: {len(self._data['posted_uris'])} posted, {len(self._data['queue'])} queued")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to save storage: {e}")
            raise StorageError(f"Failed to save storage to {self.filepath}: {e}") from e
    
    def load_posted_articles(self) -> List[PostedArticle]:
        """Load history of posted articles."""
        history = self.data.get("posted_articles_history", [])
        
        posted_articles = []
        for record in history:
            try:
                # Reconstruct Article (simplified - no full article data in history)
                article = Article(
                    uri=record['uri'],
                    title=record['title'],
                    url=record['url'],
                    source=record.get('source', 'Unknown'),
                    body='',  # Not stored in history
                    published_at=None
                )
                
                # Parse posted timestamp
                posted_at = datetime.fromisoformat(record['posted_at'])
                
                # Reconstruct PostedArticle (without thread data)
                from src.domain import Thread, Tweet
                # Create placeholder thread
                placeholder_tweet = Tweet(record['url'])
                placeholder_thread = Thread(
                    tweets=(placeholder_tweet,),
                    article=article
                )
                
                posted = PostedArticle(
                    article=article,
                    thread=placeholder_thread,
                    posted_at=posted_at,
                    tweet_ids=tuple(record.get('tweet_ids', []))
                )
                
                posted_articles.append(posted)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse posted article: {e}")
                continue
        
        return posted_articles
    
    def save_posted_article(self, posted: PostedArticle) -> bool:
        """Save a newly posted article."""
        try:
            # Add to posted URIs
            if posted.article.uri not in self.data["posted_uris"]:
                self.data["posted_uris"].append(posted.article.uri)
            
            # Add to history
            history_record = posted.to_dict()
            self.data["posted_articles_history"].append(history_record)
            
            # Keep only last 100 in history
            if len(self.data["posted_articles_history"]) > 100:
                self.data["posted_articles_history"] = self.data["posted_articles_history"][-100:]
            
            return self._save_data()
            
        except Exception as e:
            logger.error(f"Failed to save posted article: {e}")
            return False
    
    def load_queue(self) -> List[Article]:
        """Load queued articles."""
        queue_data = self.data.get("queue", [])
        
        articles = []
        for item in queue_data:
            try:
                article = Article.from_dict(item)
                articles.append(article)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse queued article: {e}")
                continue
        
        return articles
    
    def save_queue(self, articles: List[Article]) -> bool:
        """Save updated article queue."""
        try:
            self.data["queue"] = [article.to_dict() for article in articles]
            return self._save_data()
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
            return False
    
    def clear_queue(self) -> bool:
        """Clear all queued articles."""
        try:
            self.data["queue"] = []
            return self._save_data()
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return False
