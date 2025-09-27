"""
Bitcoin Mining News Bot - Core Module
====================================
Elegant, consolidated core functionality for the Bitcoin Mining News Twitter Bot.
This module contains all essential components in a clean, organized structure.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# External dependencies
import tweepy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('bitcoin_mining_bot')


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Centralized configuration for the Bitcoin Mining News Bot."""
    
    # API Configuration
    twitter_api_key: str = ""
    twitter_api_secret: str = ""  
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""
    eventregistry_api_key: str = ""
    gemini_api_key: str = ""
    
    # Bot Constants
    max_articles: int = 20
    min_interval_minutes: int = 90
    max_retries: int = 1
    retry_delay_minutes: int = 5
    article_lookback_days: int = 1
    cooldown_hours: int = 2
    
    # Files
    posted_articles_file: str = "posted_articles.json"
    rate_limit_file: str = "rate_limit_cooldown.json"
    
    # Keywords
    bitcoin_keywords: List[str] = None
    
    def __post_init__(self):
        if self.bitcoin_keywords is None:
            self.bitcoin_keywords = [
                "Bitcoin mining", "BTC mining", "bitcoin miner", "mining pool",
                "mining farm", "hash rate", "mining difficulty", "ASIC miner"
            ]
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            twitter_api_key=os.getenv("TWITTER_API_KEY", ""),
            twitter_api_secret=os.getenv("TWITTER_API_SECRET", ""),
            twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN", ""),
            twitter_access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
            eventregistry_api_key=os.getenv("EVENTREGISTRY_API_KEY", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", "")
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of missing required fields."""
        missing = []
        required_fields = [
            ("twitter_api_key", self.twitter_api_key),
            ("twitter_api_secret", self.twitter_api_secret),
            ("twitter_access_token", self.twitter_access_token),
            ("twitter_access_token_secret", self.twitter_access_token_secret),
            ("eventregistry_api_key", self.eventregistry_api_key)
        ]
        
        for field_name, value in required_fields:
            if not value:
                missing.append(field_name.upper())
        
        return missing


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Article:
    """Represents a news article."""
    title: str
    body: str
    url: str
    source: str = ""
    date_published: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create Article from dictionary."""
        return cls(
            title=data.get("title", ""),
            body=data.get("body", data.get("summary", "")),
            url=data.get("url", data.get("uri", "")),
            source=data.get("source", {}).get("title", "") if isinstance(data.get("source"), dict) else str(data.get("source", "")),
            date_published=cls._parse_date(data.get("dateTimePub", data.get("dateTime")))
        )
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except (ValueError, TypeError):
            return None


# =============================================================================
# STORAGE MANAGER
# =============================================================================

class Storage:
    """Elegant file-based storage manager."""
    
    @staticmethod
    def load_json(filepath: str, default: Any = None) -> Any:
        """Load JSON file with error handling."""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error loading {filepath}: {e}")
        
        return default if default is not None else {}
    
    @staticmethod
    def save_json(filepath: str, data: Any) -> bool:
        """Save data to JSON file with error handling."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, TypeError) as e:
            logger.error(f"Error saving {filepath}: {e}")
            return False
    
    @staticmethod
    def load_posted_articles(filepath: str) -> Dict[str, Any]:
        """Load posted articles data structure."""
        data = Storage.load_json(filepath, {})
        return {
            "posted_uris": data.get("posted_uris", []),
            "queued_articles": data.get("queued_articles", []),
            "last_run_time": data.get("last_run_time")
        }


# =============================================================================
# TIME UTILITIES
# =============================================================================

class TimeManager:
    """Time-related utilities."""
    
    @staticmethod
    def now() -> datetime:
        """Get current datetime."""
        return datetime.now()
    
    @staticmethod
    def is_minimum_interval_passed(last_run: Optional[str], min_minutes: int) -> bool:
        """Check if minimum interval has passed since last run."""
        if not last_run:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_run)
            return (TimeManager.now() - last_time) >= timedelta(minutes=min_minutes)
        except (ValueError, TypeError):
            return True
    
    @staticmethod
    def create_cooldown_data(hours: int) -> Dict[str, Any]:
        """Create rate limit cooldown data."""
        return {
            "cooldown_start": TimeManager.now().isoformat(),
            "cooldown_hours": hours,
            "cooldown_end": (TimeManager.now() + timedelta(hours=hours)).isoformat()
        }
    
    @staticmethod
    def is_cooldown_active(cooldown_data: Dict[str, Any]) -> bool:
        """Check if cooldown is still active."""
        if not cooldown_data.get("cooldown_end"):
            return False
        
        try:
            cooldown_end = datetime.fromisoformat(cooldown_data["cooldown_end"])
            return TimeManager.now() < cooldown_end
        except (ValueError, TypeError, KeyError):
            return False


# =============================================================================
# TEXT PROCESSING
# =============================================================================

class TextProcessor:
    """Advanced text processing for tweet creation."""
    
    PREFIXES = ["🚨 BREAKING:", "📢 JUST IN:", "⚡ NEWS:", "🔥 HOT:"]
    
    @staticmethod
    def create_tweet_text(article: Article) -> str:
        """Create engaging tweet text from article."""
        import random
        
        # Clean and prepare title
        title = TextProcessor._clean_title(article.title)
        
        # Add engaging prefix
        prefix = random.choice(TextProcessor.PREFIXES)
        
        # Create tweet with URL if available
        if article.url:
            max_length = 240  # Leave room for URL
            tweet_text = f"{prefix} {title}"
            
            if len(tweet_text) > max_length:
                # Truncate title to fit
                available = max_length - len(prefix) - 4  # 4 for " " and "..."
                title = title[:available] + "..."
                tweet_text = f"{prefix} {title}"
            
            return f"{tweet_text}\n\n{article.url}"
        else:
            # Text-only tweet
            tweet_text = f"{prefix} {title}"
            if len(tweet_text) > 280:
                available = 276  # 4 for "..."
                title = title[:available - len(prefix) - 1] + "..."
                tweet_text = f"{prefix} {title}"
            
            return tweet_text
    
    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean and optimize title for Twitter."""
        # Remove common prefixes
        prefixes_to_remove = [
            r"^BREAKING:\s*", r"^Breaking:\s*", r"^JUST IN:\s*",
            r"^News:\s*", r"^Bitcoin:\s*", r"^BTC:\s*"
        ]
        
        for prefix in prefixes_to_remove:
            title = re.sub(prefix, "", title, flags=re.IGNORECASE)
        
        # Clean up whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title


# =============================================================================
# API CLIENTS
# =============================================================================

class TwitterAPI:
    """Simplified Twitter API client."""
    
    def __init__(self, config: Config):
        self.client = tweepy.Client(
            consumer_key=config.twitter_api_key,
            consumer_secret=config.twitter_api_secret,
            access_token=config.twitter_access_token,
            access_token_secret=config.twitter_access_token_secret,
            wait_on_rate_limit=False
        )
    
    def post_tweet(self, text: str) -> Optional[str]:
        """Post a tweet and return tweet ID."""
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id'] if response.data else None
            logger.info(f"Tweet posted successfully: {tweet_id}")
            return tweet_id
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None


class NewsAPI:
    """Simplified EventRegistry/NewsAPI client."""
    
    def __init__(self, config: Config):
        self.config = config
        self._client = None
    
    def fetch_articles(self, max_articles: int = 20) -> List[Article]:
        """Fetch Bitcoin mining articles."""
        try:
            # Lazy import and initialization
            if self._client is None:
                import eventregistry
                self._client = eventregistry.EventRegistry(
                    apiKey=self.config.eventregistry_api_key,
                    verboseOutput=False
                )
            
            # Create query for Bitcoin mining articles
            from eventregistry import QueryArticles, QueryItems, RequestArticlesInfo
            
            yesterday = datetime.now() - timedelta(days=self.config.article_lookback_days)
            
            query = QueryArticles(
                keywords=QueryItems.OR(self.config.bitcoin_keywords),
                dateStart=yesterday.date(),
                dateEnd=datetime.now().date(),
                lang="eng"
            )
            
            query.setRequestedResult(RequestArticlesInfo(
                count=max_articles,
                sortBy="date",
                sortByAsc=False
            ))
            
            result = self._client.execQuery(query)
            articles_data = result.get("articles", {}).get("results", [])
            
            # Convert to Article objects and filter for Bitcoin content
            articles = [Article.from_dict(data) for data in articles_data]
            return self._filter_bitcoin_articles(articles)
            
        except Exception as e:
            logger.error(f"Failed to fetch articles: {e}")
            return []
    
    def _filter_bitcoin_articles(self, articles: List[Article]) -> List[Article]:
        """Filter articles to ensure they're actually about Bitcoin."""
        bitcoin_terms = ["bitcoin", "btc", "mining", "miner", "hash rate", "asic"]
        
        filtered = []
        for article in articles:
            text = f"{article.title} {article.body}".lower()
            if any(term in text for term in bitcoin_terms):
                filtered.append(article)
        
        logger.info(f"Filtered {len(articles)} articles to {len(filtered)} Bitcoin-focused articles")
        return filtered


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class BitcoinMiningBot:
    """
    Elegant, consolidated Bitcoin Mining News Bot.
    
    This class handles the complete workflow:
    1. Fetch articles from EventRegistry
    2. Filter and queue new articles
    3. Post tweets to Twitter
    4. Manage rate limits and storage
    """
    
    def __init__(self, config: Optional[Config] = None, safe_mode: bool = False):
        """Initialize the bot with configuration."""
        self.config = config or Config.from_env()
        self.safe_mode = safe_mode
        
        # Initialize storage
        self.storage = Storage()
        self.posted_data = self.storage.load_posted_articles(self.config.posted_articles_file)
        
        # Initialize API clients (lazy)
        self._twitter = None
        self._news = None
        
        if not safe_mode:
            logger.info(f"Bot initialized. {len(self.posted_data['posted_uris'])} articles already posted.")
    
    @property
    def twitter(self) -> TwitterAPI:
        """Lazy-initialized Twitter API client."""
        if self._twitter is None:
            self._twitter = TwitterAPI(self.config)
        return self._twitter
    
    @property
    def news(self) -> NewsAPI:
        """Lazy-initialized News API client."""
        if self._news is None:
            self._news = NewsAPI(self.config)
        return self._news
    
    def run(self) -> bool:
        """
        Main execution method.
        Returns True if successful, False otherwise.
        """
        try:
            start_time = time.time()
            logger.info("🤖 Starting Bitcoin Mining News Bot")
            
            # Validate configuration
            if self.safe_mode:
                return self._run_diagnostics()
            
            missing_config = self.config.validate()
            if missing_config:
                logger.error(f"Missing required configuration: {', '.join(missing_config)}")
                return False
            
            # Check rate limiting
            if self._is_rate_limited():
                logger.info("Rate limit cooldown active. Skipping run.")
                return True
            
            # Check minimum interval
            if not self._can_run_now():
                return True
            
            # Fetch new articles
            logger.info("Fetching articles...")
            articles = self.news.fetch_articles(self.config.max_articles)
            
            if not articles:
                logger.info("No new articles found")
                return True
            
            # Find new articles to post
            new_articles = self._filter_new_articles(articles)
            
            if not new_articles:
                logger.info("All articles have already been posted")
                return True
            
            # Post the most recent article
            article_to_post = new_articles[0]
            success = self._post_article(article_to_post)
            
            if success:
                # Queue remaining articles for future posts
                if len(new_articles) > 1:
                    self._queue_articles(new_articles[1:])
                
                # Update last run time
                self.posted_data["last_run_time"] = datetime.now().isoformat()
                self._save_data()
                
                execution_time = time.time() - start_time
                logger.info(f"✅ Bot completed successfully in {execution_time:.2f}s")
                return True
            else:
                self._handle_posting_failure()
                return False
                
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            return False
    
    def _run_diagnostics(self) -> bool:
        """Run diagnostic checks."""
        logger.info("🔍 Running diagnostics...")
        
        missing_config = self.config.validate()
        if missing_config:
            logger.error("❌ Missing required environment variables:")
            for var in missing_config:
                logger.error(f"   - {var}")
            logger.info("💡 Set these as GitHub repository secrets")
            return False
        
        logger.info("✅ All required environment variables are configured")
        logger.info("✅ Posted articles file is accessible")
        logger.info("🎉 Diagnostics completed successfully")
        return True
    
    def _is_rate_limited(self) -> bool:
        """Check if bot is currently rate limited."""
        cooldown_data = self.storage.load_json(self.config.rate_limit_file, {})
        return TimeManager.is_cooldown_active(cooldown_data)
    
    def _can_run_now(self) -> bool:
        """Check if minimum interval has passed since last run."""
        last_run = self.posted_data.get("last_run_time")
        return TimeManager.is_minimum_interval_passed(last_run, self.config.min_interval_minutes)
    
    def _filter_new_articles(self, articles: List[Article]) -> List[Article]:
        """Filter out articles that have already been posted."""
        posted_urls = set(self.posted_data["posted_uris"])
        new_articles = [article for article in articles if article.url not in posted_urls]
        
        logger.info(f"Found {len(new_articles)} new articles out of {len(articles)} total")
        return new_articles
    
    def _post_article(self, article: Article) -> bool:
        """Post an article to Twitter."""
        tweet_text = TextProcessor.create_tweet_text(article)
        logger.info(f"Posting: {article.title[:50]}...")
        
        tweet_id = self.twitter.post_tweet(tweet_text)
        
        if tweet_id:
            # Record successful post
            self.posted_data["posted_uris"].append(article.url)
            return True
        else:
            return False
    
    def _queue_articles(self, articles: List[Article]) -> None:
        """Add articles to the queue for future posting."""
        for article in articles:
            article_data = {
                "title": article.title,
                "body": article.body,
                "url": article.url,
                "source": {"title": article.source},
                "dateTimePub": article.date_published.isoformat() if article.date_published else None
            }
            self.posted_data["queued_articles"].append(article_data)
        
        logger.info(f"Queued {len(articles)} articles for future posting")
    
    def _handle_posting_failure(self) -> None:
        """Handle failure to post tweet (likely rate limiting)."""
        logger.warning("Failed to post tweet - setting rate limit cooldown")
        cooldown_data = TimeManager.create_cooldown_data(self.config.cooldown_hours)
        self.storage.save_json(self.config.rate_limit_file, cooldown_data)
    
    def _save_data(self) -> None:
        """Save posted articles data."""
        self.storage.save_json(self.config.posted_articles_file, self.posted_data)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Main CLI entry point."""
    import sys
    
    # Parse command line arguments
    safe_mode = '--diagnose' in sys.argv
    
    # Create and run bot
    bot = BitcoinMiningBot(safe_mode=safe_mode)
    success = bot.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()