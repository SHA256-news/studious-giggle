"""
Domain entities for Bitcoin Mining News Bot.
Pure Python with no external dependencies - represents core business concepts.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ArticleStatus(Enum):
    """Status of an article in the bot pipeline."""
    NEW = "new"
    QUEUED = "queued"
    POSTED = "posted"
    FILTERED = "filtered"
    DUPLICATE = "duplicate"
    ERROR = "error"


@dataclass(frozen=True)
class Article:
    """Immutable article entity representing a news article."""
    
    uri: str
    title: str
    url: str
    source: str
    body: str
    published_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate article data on creation."""
        if not self.uri:
            raise ValueError("Article URI cannot be empty")
        if not self.title:
            raise ValueError("Article title cannot be empty")
        if not self.url:
            raise ValueError("Article URL cannot be empty")
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError(f"Article URL must start with http:// or https://: {self.url}")
    
    @property
    def age_hours(self) -> Optional[float]:
        """Calculate article age in hours."""
        if not self.published_at:
            return None
        delta = datetime.now(self.published_at.tzinfo) - self.published_at
        return delta.total_seconds() / 3600
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'uri': self.uri,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'body': self.body,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """Create article from dictionary."""
        pub_at = None
        if data.get('published_at'):
            try:
                pub_at = datetime.fromisoformat(data['published_at'])
            except (ValueError, TypeError):
                pass
        
        return cls(
            uri=data['uri'],
            title=data['title'],
            url=data['url'],
            source=data['source'],
            body=data.get('body', ''),
            published_at=pub_at
        )


@dataclass(frozen=True)
class Tweet:
    """Immutable tweet entity representing a single tweet."""
    
    text: str
    char_count: int = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, 'char_count', len(self.text))
        if self.char_count > 280:
            raise ValueError(f"Tweet exceeds 280 characters: {self.char_count}")
        if self.char_count == 0:
            raise ValueError("Tweet cannot be empty")


@dataclass(frozen=True)
class Thread:
    """Immutable thread entity representing a Twitter thread."""
    
    tweets: tuple[Tweet, ...]
    article: Article
    
    def __post_init__(self):
        """Validate thread structure."""
        if not self.tweets:
            raise ValueError("Thread must contain at least one tweet")
        if len(self.tweets) > 10:
            raise ValueError(f"Thread too long: {len(self.tweets)} tweets")
    
    @property
    def total_chars(self) -> int:
        """Calculate total character count."""
        return sum(tweet.char_count for tweet in self.tweets)
    
    @property
    def tweet_count(self) -> int:
        """Get number of tweets in thread."""
        return len(self.tweets)
    
    def to_list(self) -> List[str]:
        """Convert to list of tweet texts."""
        return [tweet.text for tweet in self.tweets]


@dataclass(frozen=True)
class PostedArticle:
    """Record of a successfully posted article."""
    
    article: Article
    thread: Thread
    posted_at: datetime
    tweet_ids: tuple[str, ...]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'uri': self.article.uri,
            'title': self.article.title,
            'url': self.article.url,
            'source': self.article.source,
            'posted_at': self.posted_at.isoformat(),
            'tweet_count': self.thread.tweet_count,
            'tweet_ids': list(self.tweet_ids)
        }
