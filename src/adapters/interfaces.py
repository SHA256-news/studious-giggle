"""
Abstract interfaces for external service adapters.
Defines contracts that implementations must follow - enables testing and substitution.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from datetime import datetime

from src.domain import Article, Thread, PostedArticle


class NewsProvider(ABC):
    """Interface for fetching news articles from external sources."""
    
    @abstractmethod
    def fetch_articles(
        self,
        keywords: List[str],
        max_results: int = 20,
        since_date: Optional[datetime] = None
    ) -> List[Article]:
        """
        Fetch articles matching keywords.
        
        Args:
            keywords: List of search keywords
            max_results: Maximum number of articles to return
            since_date: Only return articles published after this date
            
        Returns:
            List of Article objects
            
        Raises:
            NewsProviderError: If the API call fails
        """
        pass


class AIProvider(ABC):
    """Interface for AI-powered content generation."""
    
    @abstractmethod
    def generate_headline(
        self,
        article: Article,
        max_length: int = 80
    ) -> Optional[str]:
        """
        Generate a catchy headline for the article.
        
        Args:
            article: Article to generate headline for
            max_length: Maximum character length
            
        Returns:
            Generated headline or None if generation fails
        """
        pass
    
    @abstractmethod
    def generate_summary(
        self,
        article: Article,
        headline: str,
        max_length: int = 180
    ) -> Optional[str]:
        """
        Generate a summary that complements the headline.
        
        Args:
            article: Article to summarize
            headline: Previously generated headline (to avoid duplication)
            max_length: Maximum character length
            
        Returns:
            Generated summary or None if generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is currently available."""
        pass


class SocialMediaPublisher(ABC):
    """Interface for posting content to social media platforms."""
    
    @abstractmethod
    def post_thread(self, thread: Thread) -> Optional[List[str]]:
        """
        Post a thread to the platform.
        
        Args:
            thread: Thread object containing tweets
            
        Returns:
            List of post IDs if successful, None otherwise
            
        Raises:
            PublisherError: If posting fails
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if publisher is properly authenticated."""
        pass


class ArticleStorage(ABC):
    """Interface for persistent article storage."""
    
    @abstractmethod
    def load_posted_articles(self) -> List[PostedArticle]:
        """Load history of posted articles."""
        pass
    
    @abstractmethod
    def save_posted_article(self, posted: PostedArticle) -> bool:
        """Save a newly posted article."""
        pass
    
    @abstractmethod
    def load_queue(self) -> List[Article]:
        """Load queued articles awaiting posting."""
        pass
    
    @abstractmethod
    def save_queue(self, articles: List[Article]) -> bool:
        """Save updated article queue."""
        pass
    
    @abstractmethod
    def get_last_run_time(self) -> Optional[datetime]:
        """Get timestamp of last bot execution."""
        pass
    
    @abstractmethod
    def set_last_run_time(self, timestamp: datetime) -> bool:
        """Record bot execution timestamp."""
        pass
    
    @abstractmethod
    def clear_queue(self) -> bool:
        """Clear all queued articles."""
        pass


# Custom exceptions for adapters
class NewsProviderError(Exception):
    """Raised when news fetching fails."""
    pass


class AIProviderError(Exception):
    """Raised when AI generation fails."""
    pass


class PublisherError(Exception):
    """Raised when social media posting fails."""
    pass


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass
