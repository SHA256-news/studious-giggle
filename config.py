"""
Configuration management for Bitcoin Mining News Bot
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TwitterConfig:
    """Twitter API configuration"""
    api_key: str
    api_secret: str 
    access_token: str
    access_token_secret: str
    
    @classmethod
    def from_env(cls) -> 'TwitterConfig':
        """Load Twitter config from environment variables"""
        missing_vars = []
        
        api_key = os.environ.get("TWITTER_API_KEY")
        api_secret = os.environ.get("TWITTER_API_SECRET")
        access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        
        if not api_key:
            missing_vars.append("TWITTER_API_KEY")
        if not api_secret:
            missing_vars.append("TWITTER_API_SECRET")
        if not access_token:
            missing_vars.append("TWITTER_ACCESS_TOKEN")
        if not access_token_secret:
            missing_vars.append("TWITTER_ACCESS_TOKEN_SECRET")
            
        if missing_vars:
            raise ValueError(f"Missing Twitter environment variables: {missing_vars}")
            
        return cls(
            api_key=api_key,
            api_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )


@dataclass
class EventRegistryConfig:
    """EventRegistry API configuration"""
    api_key: str
    
    @classmethod
    def from_env(cls) -> 'EventRegistryConfig':
        """Load EventRegistry config from environment variables"""
        api_key = os.environ.get("EVENTREGISTRY_API_KEY")
        if not api_key:
            raise ValueError("Missing environment variable: EVENTREGISTRY_API_KEY")
        return cls(api_key=api_key)


@dataclass
class GeminiConfig:
    """Gemini AI API configuration"""
    api_key: str
    
    @classmethod
    def from_env(cls) -> 'GeminiConfig':
        """Load Gemini config from environment variables"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing environment variable: GEMINI_API_KEY")
        return cls(api_key=api_key)


class BotConstants:
    """Bot configuration constants"""
    
    # File paths
    POSTED_ARTICLES_FILE = "posted_articles.json"
    RATE_LIMIT_COOLDOWN_FILE = "rate_limit_cooldown.json"
    
    # Tweet settings
    TWEET_MAX_LENGTH = 280
    TWEET_TRUNCATE_LENGTH = 277
    TITLE_MAX_LENGTH = 240
    TWEET_PREFIXES = ["⚡ ", "💰 ", "📈 ", "🏭 ", "🎯 "]
    TWEET_CALL_TO_ACTION = "Read more:"
    
    # Rate limiting
    MINIMUM_INTERVAL_MINUTES = 90
    RATE_LIMIT_INITIAL_HOURS = 2
    RATE_LIMIT_SUBSEQUENT_HOURS = 4
    DAILY_REQUEST_LIMIT = 17
    RETRY_DELAY_SECONDS = 300  # 5 minutes
    MAX_RETRIES = 1
    
    # Article fetching
    DEFAULT_MAX_ARTICLES = 10
    ARTICLE_LOOKBACK_DAYS = 1
    
    # Bitcoin-specific keywords for EventRegistry
    BITCOIN_KEYWORDS = [
        "Bitcoin mining", 
        "BTC mining", 
        "Bitcoin miner", 
        "Bitcoin miners",
        "Bitcoin hashrate",
        "Bitcoin difficulty"
    ]
    
    # Supported languages
    SUPPORTED_LANGUAGES = ["eng"]
    
    # Image support
    IMAGES_DIRECTORY = "images"