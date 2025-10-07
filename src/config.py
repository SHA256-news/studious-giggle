"""
Configuration management for the bot.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BotConfig:
    """Main bot configuration loaded from environment."""
    
    # API Keys
    twitter_api_key: str
    twitter_api_secret: str
    twitter_access_token: str
    twitter_access_token_secret: str
    eventregistry_api_key: str
    gemini_api_key: str
    
    # Bot Settings
    max_articles: int = 20
    article_lookback_days: int = 1
    
    # Storage
    storage_file: str = "posted_articles.json"
    
    # Search Keywords
    bitcoin_keywords: List[str] = field(default_factory=lambda: [
        "bitcoin mining", "Bitcoin mining", "BTC mining",
        "bitcoin miner", "Bitcoin miner", "mining bitcoin",
        "mining BTC", "hash rate", "mining difficulty",
        "ASIC miner", "mining pool", "mining farm"
    ])
    
    # Filtering Settings
    title_similarity_threshold: float = 0.8
    content_similarity_threshold: float = 0.7
    duplicate_detection_window_hours: int = 48
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """
        Load configuration from environment variables.
        
        Returns:
            BotConfig instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Required keys
        twitter_api_key = os.getenv("TWITTER_API_KEY", "")
        twitter_api_secret = os.getenv("TWITTER_API_SECRET", "")
        twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        eventregistry_api_key = os.getenv("EVENTREGISTRY_API_KEY", "")
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        
        return cls(
            twitter_api_key=twitter_api_key,
            twitter_api_secret=twitter_api_secret,
            twitter_access_token=twitter_access_token,
            twitter_access_token_secret=twitter_access_token_secret,
            eventregistry_api_key=eventregistry_api_key,
            gemini_api_key=gemini_api_key,
            max_articles=int(os.getenv("MAX_ARTICLES", "20")),
            article_lookback_days=int(os.getenv("ARTICLE_LOOKBACK_DAYS", "1")),
            storage_file=os.getenv("STORAGE_FILE", "posted_articles.json")
        )
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []
        
        # Check required API keys
        if not self.twitter_api_key:
            issues.append("TWITTER_API_KEY is required")
        if not self.twitter_api_secret:
            issues.append("TWITTER_API_SECRET is required")
        if not self.twitter_access_token:
            issues.append("TWITTER_ACCESS_TOKEN is required")
        if not self.twitter_access_token_secret:
            issues.append("TWITTER_ACCESS_TOKEN_SECRET is required")
        if not self.eventregistry_api_key:
            issues.append("EVENTREGISTRY_API_KEY is required")
        if not self.gemini_api_key:
            issues.append("GEMINI_API_KEY is required")
        
        # Validate numeric ranges
        if self.max_articles < 1:
            issues.append(f"max_articles must be positive: {self.max_articles}")
        if self.article_lookback_days < 1:
            issues.append(f"article_lookback_days must be positive: {self.article_lookback_days}")
        
        # Validate thresholds
        if not 0 <= self.title_similarity_threshold <= 1:
            issues.append(f"title_similarity_threshold must be 0-1: {self.title_similarity_threshold}")
        if not 0 <= self.content_similarity_threshold <= 1:
            issues.append(f"content_similarity_threshold must be 0-1: {self.content_similarity_threshold}")
        
        return issues
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0
    
    def __repr__(self) -> str:
        """Safe string representation (no API keys)."""
        return (
            f"BotConfig(twitter={'✓' if self.twitter_api_key else '✗'}, "
            f"eventregistry={'✓' if self.eventregistry_api_key else '✗'}, "
            f"gemini={'✓' if self.gemini_api_key else '✗'}, "
            f"max_articles={self.max_articles})"
        )
