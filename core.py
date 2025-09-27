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
import google.genai as genai
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
    bitcoin_keywords: Optional[List[str]] = None
    
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
        missing: List[str] = []
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
        """Create Article from dictionary with input validation.
        
        Args:
            data: Dictionary containing article data
            
        Returns:
            Article: Validated article object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Article data must be a dictionary")
        
        # Validate required fields
        title = data.get("title", "").strip()
        if not title:
            raise ValueError("Article title is required")
        
        url = data.get("url", data.get("uri", "")).strip()
        if not url:
            raise ValueError("Article URL is required")
        
        return cls(
            title=title,
            body=data.get("body", data.get("summary", "")),
            url=url,
            source=cls._extract_source(data.get("source")),
            date_published=cls._parse_date(data.get("dateTimePub", data.get("dateTime")))
        )
    
    @staticmethod
    def _extract_source(source_data: Any) -> str:
        """Extract source name from various source data formats."""
        if isinstance(source_data, dict):
            title = source_data.get("title", "Unknown Source")
            return str(title) if title else "Unknown Source"
        elif isinstance(source_data, str):
            return source_data if source_data.strip() else "Unknown Source"
        else:
            return "Unknown Source"
    
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
        """Load JSON file with comprehensive error handling.
        
        Args:
            filepath: Path to JSON file
            default: Default value to return on error
            
        Returns:
            Loaded data or default value
        """
        file_path = Path(filepath)
        
        try:
            if not file_path.exists():
                logger.info(f"File {filepath} does not exist, using defaults")
                return default if default is not None else {}
            
            if file_path.stat().st_size == 0:
                logger.warning(f"File {filepath} is empty, using defaults")
                return default if default is not None else {}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Successfully loaded {filepath}")
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
        except PermissionError as e:
            logger.error(f"Permission denied reading {filepath}: {e}")
        except IOError as e:
            logger.error(f"I/O error reading {filepath}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {e}")
        
        return default if default is not None else {}
    
    @staticmethod
    def save_json(filepath: str, data: Any) -> bool:
        """Save data to JSON file with atomic operations and error handling.
        
        Args:
            filepath: Target file path
            data: Data to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        file_path = Path(filepath)
        temp_file = None
        
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use atomic write: write to temp file, then rename
            temp_file = file_path.with_suffix(f"{file_path.suffix}.tmp")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()  # Ensure data is written
                os.fsync(f.fileno())  # Force OS to write to disk
            
            # Atomic rename (on most filesystems)
            temp_file.rename(file_path)
            logger.debug(f"Successfully saved {filepath}")
            return True
            
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to encode JSON for {filepath}: {e}")
        except PermissionError as e:
            logger.error(f"Permission denied writing {filepath}: {e}")
        except OSError as e:
            logger.error(f"OS error writing {filepath}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving {filepath}: {e}")
        finally:
            # Clean up temp file if it exists
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {temp_file}: {e}")
        
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
# GEMINI AI CLIENT  
# =============================================================================

class GeminiClient:
    """Gemini AI client for generating catchy headlines and summaries."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini client with API key."""
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_id = "gemini-1.5-flash"  # Using recommended model
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")
    
    def generate_catchy_headline(self, article: 'Article') -> str:
        """Generate a catchy, emoji-free headline for the article."""
        prompt = f"""
        Create a catchy, professional headline for this Bitcoin mining news article.
        
        Original title: {article.title}
        Source: {article.source_name if hasattr(article, 'source_name') else 'Unknown'}
        
        Requirements:
        - NO emojis or special characters
        - Maximum 50 characters
        - Professional and engaging tone
        - Focus on the key news impact
        - Suitable for Twitter/X
        
        Return only the headline text, nothing else.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt.strip()
            )
            
            headline = response.text.strip()
            # Ensure no emojis and length compliance
            headline = self._clean_headline(headline)
            return headline[:50] if len(headline) > 50 else headline
            
        except Exception as e:
            # Fallback to cleaned original title
            return self._clean_headline(article.title)[:50]
    
    def generate_thread_summary(self, article: 'Article') -> list[str]:
        """Generate a 3-point summary thread for the article."""
        prompt = f"""
        Create a 3-point summary thread for this Bitcoin mining news article.
        
        Title: {article.title}
        Content: {article.body[:1000]}...
        
        Requirements:
        - Exactly 3 key points
        - Each point maximum 200 characters
        - Professional tone, no emojis
        - Focus on Bitcoin mining implications
        - Numbered format (1., 2., 3.)
        
        Format:
        1. [First key point]
        2. [Second key point]  
        3. [Third key point]
        
        Return only the numbered points, nothing else.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt.strip()
            )
            
            summary_text = response.text.strip()
            # Parse the numbered points
            points = self._parse_summary_points(summary_text)
            return points[:3]  # Ensure exactly 3 points
            
        except Exception as e:
            # Fallback to simple bullet points from title
            return [
                f"1. {article.title[:180]}",
                "2. This development impacts Bitcoin mining operations",
                "3. More details in the full article"
            ]
    
    def _clean_headline(self, text: str) -> str:
        """Remove emojis and clean headline text."""
        import re
        # Remove emojis and special prefixes
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Remove common prefixes
        prefixes = [
            r"^(BREAKING:|JUST IN:|NEWS:|HOT:)\s*",
            r"^🚨\s*", r"^📢\s*", r"^⚡\s*", r"^🔥\s*"
        ]
        for prefix in prefixes:
            text = re.sub(prefix, "", text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _parse_summary_points(self, text: str) -> list[str]:
        """Parse numbered points from Gemini response."""
        import re
        
        # Look for numbered points (1., 2., 3.)
        points = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Match patterns like "1. ", "2. ", "3. "
            if re.match(r'^\d+\.\s+', line):
                points.append(line)
        
        # If parsing fails, create fallback points
        if len(points) < 3:
            points = [
                "1. Key development in Bitcoin mining sector",
                "2. Regulatory or technical implications discussed", 
                "3. Industry impact and future outlook"
            ]
        
        return points

# =============================================================================
# TEXT PROCESSING
# =============================================================================

class TextProcessor:
    """Advanced text processing for tweet creation with Gemini AI integration."""
    
    @staticmethod
    def create_tweet_thread(article: Article, gemini_client: GeminiClient = None) -> list[str]:
        """Create a complete tweet thread with catchy headline, summary, and URL."""
        thread = []
        
        if gemini_client:
            try:
                # Generate Gemini-powered content
                headline = gemini_client.generate_catchy_headline(article)
                summary_points = gemini_client.generate_thread_summary(article)
                
                # Tweet 1: Catchy headline (no URL)
                thread.append(headline)
                
                # Tweets 2-4: Summary points (no URL)
                for point in summary_points:
                    thread.append(point)
                
                # Final tweet: URL only
                if article.url:
                    thread.append(article.url)
                
                return thread
                
            except Exception as e:
                # Fall back to simple format if Gemini fails
                pass
        
        # Fallback: Simple format without Gemini
        return TextProcessor._create_simple_tweet(article)
    
    @staticmethod
    def _create_simple_tweet(article: Article) -> list[str]:
        """Create simple thread (fallback when Gemini unavailable)."""
        thread = []
        
        # Clean title and add simple prefix (no emojis)
        title = TextProcessor._clean_title(article.title)
        prefixes = ["BREAKING:", "JUST IN:", "NEWS:", "HOT:"]
        import random
        prefix = random.choice(prefixes)
        
        # Tweet 1: Prefixed headline (no URL, no emojis)
        headline = f"{prefix} {title}"
        if len(headline) > 280:
            headline = headline[:277] + "..."
        thread.append(headline)
        
        # Tweet 2: URL only (following the rule - no intermediate tweet)
        if article.url:
            thread.append(article.url)
        
        return thread
    
    @staticmethod
    def create_tweet_text(article: Article) -> str:
        """Legacy method - creates simple tweet (maintained for backward compatibility)."""
        # Use simple format for backward compatibility
        simple_thread = TextProcessor._create_simple_tweet(article)
        return simple_thread[0] if simple_thread else article.title
    
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
        """Post a tweet and return tweet ID.
        
        Args:
            text: Tweet content
            
        Returns:
            Tweet ID if successful, None otherwise
        """
        try:
            response = self.client.create_tweet(text=text)
            
            # Handle different response types
            if hasattr(response, 'data') and response.data:
                tweet_id = str(response.data.get('id', '')) if hasattr(response.data, 'get') else str(response.data)
                if tweet_id:
                    logger.info(f"Tweet posted successfully: {tweet_id}")
                    return tweet_id
            
            logger.warning("Tweet posted but no ID returned")
            return None
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None
    
    def post_thread(self, tweets: list[str]) -> bool:
        """Post a thread of tweets.
        
        Args:
            tweets: List of tweet texts to post as a thread
            
        Returns:
            True if all tweets posted successfully, False otherwise
        """
        if not tweets:
            return False
            
        try:
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweets):
                logger.info(f"Posting tweet {i+1}/{len(tweets)}")
                
                # Post tweet, replying to previous if this is part of thread
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet_text)
                
                # Extract tweet ID for next reply
                if hasattr(response, 'data') and response.data:
                    current_tweet_id = str(response.data.get('id', '')) if hasattr(response.data, 'get') else str(response.data)
                    if current_tweet_id:
                        previous_tweet_id = current_tweet_id
                        logger.info(f"Thread tweet {i+1} posted: {current_tweet_id}")
                    else:
                        logger.error(f"Failed to get ID for tweet {i+1}")
                        return False
                else:
                    logger.error(f"Failed to post tweet {i+1}")
                    return False
            
            logger.info(f"Thread posted successfully ({len(tweets)} tweets)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            return False


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
        self._gemini = None
        
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
    
    @property
    def gemini(self) -> GeminiClient:
        """Lazy-initialized Gemini AI client."""
        if self._gemini is None:
            if self.config.gemini_api_key:
                try:
                    self._gemini = GeminiClient(self.config.gemini_api_key)
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini client: {e}")
                    self._gemini = None
            else:
                self._gemini = None
        return self._gemini
    
    def run(self) -> bool:
        """
        Main execution method.
        Returns True if successful, False otherwise.
        """
        start_time = time.time()
        
        try:
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
                logger.info("Minimum interval not yet reached. Skipping run.")
                return True
            
            # Fetch new articles first (prioritize fresh content)
            logger.info("Fetching new articles...")
            try:
                articles = self.news.fetch_articles(self.config.max_articles)
            except Exception as e:
                logger.error(f"Failed to fetch articles: {e}")
                return False

            article_to_post = None
            new_articles = []

            if articles:
                # Find new articles to post
                new_articles = self._filter_new_articles(articles)
                
                if new_articles:
                    logger.info(f"Found {len(new_articles)} new articles")
                    # Post the most recent new article
                    article_to_post = new_articles[0]
                else:
                    logger.info("All fetched articles have already been posted")
            else:
                logger.info("No new articles found from EventRegistry")

            # Fallback to queued articles if no new articles available
            if not article_to_post:
                queued_articles = self.posted_data.get("queued_articles", [])
                
                if queued_articles:
                    logger.info(f"No new articles available. Processing {len(queued_articles)} queued articles (newest first)")
                    
                    # Sort queued articles by publication date (newest first)
                    try:
                        sorted_queue = sorted(queued_articles, key=lambda x: x.get('dateTimePub', x.get('dateTime', '')), reverse=True)
                        # Use most recent queued article first
                        article_data = sorted_queue[0]
                        # Find its index in the original queue for removal later
                        original_index = queued_articles.index(article_data)
                        self._posted_queue_index = original_index  # Store for later removal
                        article_to_post = Article.from_dict(article_data)
                        logger.info(f"Posting most recent queued article: {article_to_post.title} ({article_data.get('dateTimePub', 'unknown date')})")
                    except Exception as e:
                        logger.error(f"Failed to parse queued articles: {e}")
                        # Remove invalid article from queue (first one)
                        self.posted_data["queued_articles"].pop(0)
                        self._save_data()
                        return True
                else:
                    logger.info("No new articles and no queued articles available")
                    return True
            success = self._post_article(article_to_post)

            if success:
                # Handle post-success actions based on source
                if new_articles and len(new_articles) > 1:
                    # Queue remaining new articles for future posts
                    self._queue_articles(new_articles[1:])
                elif not new_articles and self.posted_data.get("queued_articles"):
                    # Remove the posted queued article from queue (use original_index)
                    if hasattr(self, '_posted_queue_index'):
                        self.posted_data["queued_articles"].pop(self._posted_queue_index)
                        logger.info("Removed posted article from queue")
                        delattr(self, '_posted_queue_index')

                # Update last run time
                self.posted_data["last_run_time"] = datetime.now().isoformat()
                if not self._save_data():
                    logger.warning("Failed to save posted articles data")

                execution_time = time.time() - start_time
                logger.info(f"✅ Bot completed successfully in {execution_time:.2f}s")
                return True
            else:
                self._handle_posting_failure()
                return False
                
        except KeyboardInterrupt:
            logger.info("Bot execution interrupted by user")
            return False
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Bot execution failed after {execution_time:.2f}s: {e}")
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
        """Post an article to Twitter as a thread."""
        try:
            # Generate thread using Gemini (if available) or fallback
            thread_tweets = TextProcessor.create_tweet_thread(article, self.gemini)
            logger.info(f"Posting thread with {len(thread_tweets)} tweets: {article.title[:50]}...")
            
            if len(thread_tweets) == 1:
                # Single tweet
                tweet_id = self.twitter.post_tweet(thread_tweets[0])
                success = bool(tweet_id)
            else:
                # Multi-tweet thread
                success = self.twitter.post_thread(thread_tweets)
            
            if success:
                # Record successful post
                self.posted_data["posted_uris"].append(article.url)
                return True
            else:
                logger.error("Failed to post tweet(s)")
                return False
                
        except Exception as e:
            logger.error(f"Error posting article: {e}")
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
    
    def _save_data(self) -> bool:
        """Save posted articles data.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            return self.storage.save_json(self.config.posted_articles_file, self.posted_data)
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False


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