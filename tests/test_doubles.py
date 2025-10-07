"""
Test doubles (mocks/fakes) for adapter interfaces.
Makes testing easy without hitting real APIs.
"""
from datetime import datetime
from typing import List, Optional

from src.domain import Article, Thread, PostedArticle
from src.adapters.interfaces import (
    NewsProvider,
    AIProvider,
    SocialMediaPublisher,
    ArticleStorage
)


class FakeNewsProvider(NewsProvider):
    """Fake news provider for testing."""
    
    def __init__(self):
        self.articles_to_return: List[Article] = []
        self.fetch_called = False
    
    def fetch_articles(
        self,
        keywords: List[str],
        max_results: int = 20,
        since_date: Optional[datetime] = None
    ) -> List[Article]:
        self.fetch_called = True
        return self.articles_to_return[:max_results]


class FakeAIProvider(AIProvider):
    """Fake AI provider for testing."""
    
    def __init__(self, available: bool = True):
        self._available = available
        self.headline_to_return: Optional[str] = "Test Headline"
        self.summary_to_return: Optional[str] = "Test summary"
        self.generate_headline_called = False
        self.generate_summary_called = False
    
    def generate_headline(
        self,
        article: Article,
        max_length: int = 80
    ) -> Optional[str]:
        self.generate_headline_called = True
        return self.headline_to_return
    
    def generate_summary(
        self,
        article: Article,
        headline: str,
        max_length: int = 180
    ) -> Optional[str]:
        self.generate_summary_called = True
        return self.summary_to_return
    
    def is_available(self) -> bool:
        return self._available


class FakePublisher(SocialMediaPublisher):
    """Fake publisher for testing."""
    
    def __init__(self, authenticated: bool = True):
        self._authenticated = authenticated
        self.posted_threads: List[Thread] = []
        self.post_thread_called = False
    
    def post_thread(self, thread: Thread) -> Optional[List[str]]:
        self.post_thread_called = True
        self.posted_threads.append(thread)
        # Return fake tweet IDs
        return [f"tweet_{i}" for i in range(thread.tweet_count)]
    
    def is_authenticated(self) -> bool:
        return self._authenticated


class FakeStorage(ArticleStorage):
    """Fake storage for testing."""
    
    def __init__(self):
        self.posted_articles: List[PostedArticle] = []
        self.queue: List[Article] = []
        self.last_run_time: Optional[datetime] = None
        self.save_posted_article_called = False
        self.save_queue_called = False
    
    def load_posted_articles(self) -> List[PostedArticle]:
        return self.posted_articles.copy()
    
    def save_posted_article(self, posted: PostedArticle) -> bool:
        self.save_posted_article_called = True
        self.posted_articles.append(posted)
        return True
    
    def load_queue(self) -> List[Article]:
        return self.queue.copy()
    
    def save_queue(self, articles: List[Article]) -> bool:
        self.save_queue_called = True
        self.queue = articles.copy()
        return True
    
    def get_last_run_time(self) -> Optional[datetime]:
        return self.last_run_time
    
    def set_last_run_time(self, timestamp: datetime) -> bool:
        self.last_run_time = timestamp
        return True
    
    def clear_queue(self) -> bool:
        self.queue = []
        return True


def create_test_article(
    uri: str = "test-uri-123",
    title: str = "Test Bitcoin Mining Article",
    url: str = "https://example.com/article",
    source: str = "Test Source",
    body: str = "Bitcoin mining test content",
    published_at: Optional[datetime] = None
) -> Article:
    """Helper to create test articles."""
    if published_at is None:
        published_at = datetime.now()
    
    return Article(
        uri=uri,
        title=title,
        url=url,
        source=source,
        body=body,
        published_at=published_at
    )
