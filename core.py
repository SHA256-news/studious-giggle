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
logger = logging.getLogger('bitcoin_mining_bot')


# =============================================================================
# FULL CONTENT FETCHER
# =============================================================================

class FullContentFetcher:
    """Fetches complete article content from URLs using multiple methods."""
    
    def __init__(self):
        self._cache = {}  # Simple in-memory cache for article content
        
    def fetch_full_content(self, url: str) -> str:
        """
        Fetch full article content from URL with multiple fallback methods.
        
        Args:
            url: The article URL to scrape
            
        Returns:
            Full article content as string, or empty string if failed
        """
        if not url or not url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL provided: {url}")
            return ""
        
        # Check cache first
        if url in self._cache:
            logger.debug(f"Using cached content for: {url}")
            return self._cache[url]
        
        content = ""
        
        # Method 1: Try newspaper3k (best for news articles)
        content = self._try_newspaper3k(url)
        
        # Method 2: Try BeautifulSoup as fallback
        if not content:
            content = self._try_beautifulsoup(url)
        
        # Method 3: Try simple requests as last resort
        if not content:
            content = self._try_simple_requests(url)
        
        # Clean and validate content
        content = self._clean_content(content)
        
        # Cache the result (even empty strings to avoid retry)
        self._cache[url] = content
        
        if content:
            logger.info(f"✅ Fetched full content ({len(content)} chars) from: {url}")
        else:
            logger.warning(f"❌ Failed to fetch content from: {url}")
        
        return content
    
    def _try_newspaper3k(self, url: str) -> str:
        """Try to extract content using newspaper3k library."""
        try:
            from newspaper import Article as NewsArticle
            
            article = NewsArticle(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text.strip()) > 100:
                logger.debug(f"✅ newspaper3k extracted {len(article.text)} chars")
                return article.text.strip()
                
        except ImportError:
            logger.debug("newspaper3k not available")
        except Exception as e:
            logger.debug(f"newspaper3k failed: {e}")
        
        return ""
    
    def _try_beautifulsoup(self, url: str) -> str:
        """Try to extract content using BeautifulSoup."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                tag.decompose()
            
            # Try to find main content using common selectors
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.content', 'main', '.main-content', '.story-body', '.article-body'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    text = content_elem.get_text().strip()
                    if len(text) > 100:
                        logger.debug(f"✅ BeautifulSoup extracted {len(text)} chars with selector: {selector}")
                        return text
            
            # Fallback: get all paragraph text
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if len(text) > 100:
                logger.debug(f"✅ BeautifulSoup extracted {len(text)} chars from paragraphs")
                return text
                
        except ImportError:
            logger.debug("BeautifulSoup not available")
        except Exception as e:
            logger.debug(f"BeautifulSoup failed: {e}")
        
        return ""
    
    def _try_simple_requests(self, url: str) -> str:
        """Simple text extraction using requests only."""
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Very basic HTML tag removal
            text = re.sub(r'<[^>]+>', '', response.text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) > 200:
                logger.debug(f"✅ Simple requests extracted {len(text)} chars")
                return text
                
        except Exception as e:
            logger.debug(f"Simple requests failed: {e}")
        
        return ""
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize extracted content."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove common junk patterns
        junk_patterns = [
            r'Cookie Policy.*?(?=\.|$)',
            r'Privacy Policy.*?(?=\.|$)',
            r'Subscribe to.*?(?=\.|$)',
            r'Sign up for.*?(?=\.|$)',
            r'Advertisement.*?(?=\.|$)',
            r'Loading.*?(?=\.|$)',
            r'Share this.*?(?=\.|$)',
            r'Follow us.*?(?=\.|$)'
        ]
        
        for pattern in junk_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Normalize whitespace again after cleaning
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def clear_cache(self):
        """Clear the content cache."""
        self._cache.clear()
        logger.debug("Content cache cleared")


# =============================================================================
# CONFIGURATION
# =============================================================================

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
    bitcoin_keywords: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.bitcoin_keywords is None:
            self.bitcoin_keywords = [
                "bitcoin mining", "Bitcoin mining", "BTC mining", 
                "bitcoin miner", "Bitcoin miner", "mining bitcoin",
                "mining BTC", "hash rate", "mining difficulty",
                "ASIC miner", "mining pool", "mining farm"
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
    """Represents a news article with optional full content fetching."""
    title: str
    body: str
    url: str
    source: str = ""
    date_published: Optional[datetime] = None
    _full_content: Optional[str] = None  # Cached full article content
    _content_fetcher: Optional['FullContentFetcher'] = None  # Lazy-loaded fetcher
    
    def __init__(self, title: str, body: str, url: str, source: str = "", 
                 date_published: Optional[datetime] = None, content_fetcher: Optional['FullContentFetcher'] = None):
        self.title = title
        self.body = body
        self.url = url
        self.source = source
        self.date_published = date_published
        self._full_content = None
        self._content_fetcher = content_fetcher
    
    def get_full_content(self, force_refetch: bool = False) -> str:
        """
        Get the full article content from the URL.
        
        Args:
            force_refetch: Whether to refetch even if cached content exists
            
        Returns:
            Full article content, or falls back to EventRegistry body if fetching fails
        """
        # Return cached content if available and not forcing refetch
        if self._full_content and not force_refetch:
            return self._full_content
        
        # Initialize content fetcher if needed
        if not self._content_fetcher:
            self._content_fetcher = FullContentFetcher()
        
        # Try to fetch full content
        self._full_content = self._content_fetcher.fetch_full_content(self.url)
        
        # Fall back to EventRegistry body if fetching failed
        if not self._full_content:
            logger.debug(f"Using EventRegistry body as fallback for: {self.url}")
            self._full_content = self.body
        
        return self._full_content
    
    def get_best_content(self, max_length: Optional[int] = None) -> str:
        """
        Get the best available content (full content preferred, EventRegistry body as fallback).
        
        Args:
            max_length: Maximum length to return (truncates if longer)
            
        Returns:
            Best available article content
        """
        # Try full content first
        full_content = self.get_full_content()
        
        # Use full content if it's substantially longer than EventRegistry body
        if len(full_content) > len(self.body) * 1.5:
            content = full_content
            logger.debug(f"Using full content ({len(content)} chars) vs EventRegistry ({len(self.body)} chars)")
        else:
            content = self.body
            logger.debug(f"Using EventRegistry content ({len(content)} chars)")
        
        # Truncate if requested
        if max_length and len(content) > max_length:
            content = content[:max_length].rsplit(' ', 1)[0] + "..."  # Truncate at word boundary
        
        return content
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], content_fetcher: Optional['FullContentFetcher'] = None) -> 'Article':
        """Create Article from dictionary with input validation.
        
        Args:
            data: Dictionary containing article data
            content_fetcher: Optional content fetcher for full article content
            
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
            date_published=cls._parse_date(data.get("dateTimePub", data.get("dateTime"))),
            content_fetcher=content_fetcher
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
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Updated to support URL context
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")
    
    def generate_catchy_headline(self, article: 'Article') -> str:
        """Generate a catchy, emoji-free headline for the article using URL context."""
        try:
            logger.info("🎯 Generating catchy headline with Gemini URL context...")
            
            # Use Gemini's native URL context feature instead of manual scraping
            # Check if this is a chip/hardware article for enhanced prompts
            text = f"{article.title} {article.body}".lower()
            chip_terms = ["chip", "semiconductor", "processor", "hardware", "asic", "gpu", "cpu"]
            is_chip_article = any(term in text for term in chip_terms)
            
            chip_instruction = ""
            if is_chip_article:
                chip_instruction = "- CRITICAL: This appears to be about chips/hardware - explicitly connect it to Bitcoin mining applications\n            "
            
            prompt = f"""
            Create a compelling, newsworthy headline for this Bitcoin mining article.
            
            Original title: {article.title}
            Article URL: {article.url}
            
            Requirements:
            - NO emojis, hashtags, or special characters
            - 60-80 characters maximum  
            - Should capture the MAIN story/takeaway from the article
            - Include specific numbers, percentages, or key facts when available
            - Use action words like "surges", "drops", "reaches", "announces", "adopts"
            - Focus on the actual news impact, not generic statements
            - Remember: A separate 3-point summary will provide ADDITIONAL complementary details
            {chip_instruction}- Examples of good headlines (note: summary would add different details):
              "Bitcoin Mining Difficulty Surges 7.3% to New Record High"
              "Marathon Digital Announces 15,000 New ASIC Miners"  
              "Texas Bitcoin Miners Cut Power Usage During Heat Wave"
              "Nvidia Launches New Chip Targeting Bitcoin Mining Efficiency" (for chip news)
              "Intel Expands Bitcoin Mining Hardware Production" (for hardware news)
            - NO generic phrases like "key development" or "industry impact"
            
            Please read the full article content from the URL to identify the main news point.
            {"For chip/hardware articles, emphasize the Bitcoin mining application specifically." if is_chip_article else ""}
            Return only the headline text, nothing else.
            """
            
            # Configure with URL context tool
            tools = [{"url_context": {}}]
            
            try:
                import google.generativeai as genai
                # Use generate_content with tools parameter for URL context
                response = self.model.generate_content(
                    prompt.strip(),
                    tools=tools
                )
                
                headline = response.text.strip()
                logger.info(f"✅ Generated headline with URL context: '{headline}'")
                
                # Check if URL context was actually used
                if hasattr(response.candidates[0], 'url_context_metadata'):
                    url_metadata = response.candidates[0].url_context_metadata
                    logger.info(f"📄 URL context metadata: {url_metadata}")
                
                # Process and clean the headline
                return self._process_headline_response(headline)
                
            except Exception as e:
                logger.warning(f"URL context failed, falling back to standard approach: {e}")
                # Fallback to original approach without URL context
                response = self.model.generate_content(prompt.strip())
                headline = response.text.strip()
                logger.info(f"✅ Generated headline (fallback): '{headline}'")
                return self._process_headline_response(headline)
            
        except Exception as e:
            logger.warning(f"❌ Gemini headline generation failed: {e}")
            # Final fallback to cleaned original title
            return self._clean_headline(article.title)[:70]
    
    def generate_thread_summary(self, article: 'Article') -> str:
        """Generate a concise 3-point summary using URL context for full article access."""
        try:
            logger.info("🎯 Generating thread summary with Gemini URL context...")
            
            # First generate the headline to avoid repetition
            headline = self.generate_catchy_headline(article)
            logger.info(f"📰 Using headline for context: '{headline}'")
            
            # Check if this is a chip/hardware article for enhanced prompts
            text = f"{article.title} {article.body}".lower()
            chip_terms = ["chip", "semiconductor", "processor", "hardware", "asic", "gpu", "cpu"]
            is_chip_article = any(term in text for term in chip_terms)
            
            chip_instruction = ""
            chip_example = ""
            if is_chip_article:
                chip_instruction = "- CRITICAL: If this article is about chips, hardware, or semiconductors, explicitly highlight Bitcoin mining applications\n            "
                chip_example = """
              If headline: "Nvidia Launches New Chip for Enhanced Performance" (chip article)
              Then summary:
              "• Targets Bitcoin mining efficiency gains
              • Available Q2 2024 for mining farms
              • Expected 25% power reduction per hash"
              """
            
            prompt = f"""
            Create a specific 3-point summary for this Bitcoin mining article that COMPLEMENTS the headline.
            
            Title: {article.title}
            Article URL: {article.url}
            Generated Headline: {headline}
            
            CRITICAL: DO NOT REPEAT any information already mentioned in the headline above.
            
            Requirements:
            - TOTAL summary must be under 180 characters (to fit with headline in one tweet)
            - Include specific details like numbers, dates, company names, locations
            - Each point should be 50-60 characters maximum
            - Focus on NEW facts NOT mentioned in the headline
            {chip_instruction}- Good examples:{chip_example}
              If headline: "Marathon Digital Deploys 5,000 New S19 XP Miners"
              Then summary:
              "• Located in West Texas facility
              • Operations start Q2 2024
              • Expected ROI within 8 months"
              
              If headline: "Bitcoin Mining Difficulty Surges 7.3% to Record High"  
              Then summary:
              "• Block 815,000 adjustment complete
              • Hashrate reaches 472 EH/s
              • Next adjustment in 14 days"
              
            - BAD examples (repeating headline info):
              If headline mentions "5,000 miners" then DON'T repeat "5,000 miners" in summary
              If headline mentions company name, focus on OTHER details like location, timeline, financial impact
              
            - Format: Each point on its own line starting with "•"
            - NO generic phrases like "industry impact", "key development", "details in article"
            
            Please read the full article content from the URL and extract DIFFERENT facts than those in the headline.
            {"For chip/hardware articles, ensure Bitcoin mining relevance is clear in the summary." if is_chip_article else ""}
            Return only the formatted summary with each bullet point on its own line, nothing else.
            """
            
            # Configure with URL context tool
            tools = [{"url_context": {}}]
            
            try:
                # Use generate_content with tools parameter for URL context
                response = self.model.generate_content(
                    prompt.strip(),
                    tools=tools
                )
                
                summary_text = response.text.strip()
                logger.info(f"✅ Generated complementary summary: '{summary_text}'")
                
                # Check if URL context was actually used
                if hasattr(response.candidates[0], 'url_context_metadata'):
                    url_metadata = response.candidates[0].url_context_metadata
                    logger.info(f"📄 URL context metadata: {url_metadata}")
                
                # Process and validate the summary
                return self._process_summary_response(summary_text)
                
            except Exception as e:
                logger.warning(f"URL context failed, falling back to EventRegistry content: {e}")
                # Fallback to EventRegistry content approach with headline context
                fallback_prompt = f"""
                Create a specific 3-point summary that does NOT repeat information from this headline: "{headline}"
                
                Title: {article.title}
                Content: {article.body}
                
                Requirements:
                - TOTAL summary must be under 180 characters
                - Include specific details when available but NOT mentioned in headline
                - Format: Each point on its own line starting with "•"
                - NO repetition of headline information
                - NO generic phrases like "industry impact", "key development"
                - CRITICAL: If this is about chips/hardware, emphasize Bitcoin mining applications
                
                Return only the formatted summary with each point on its own line, nothing else.
                """
                
                response = self.model.generate_content(fallback_prompt.strip())
                summary_text = response.text.strip()
                logger.info(f"✅ Generated complementary summary (fallback): '{summary_text}'")
                return self._process_summary_response(summary_text)
                
        except Exception as e:
            logger.warning(f"❌ Gemini summary generation failed: {e}")
            # Final fallback to Bitcoin mining specific summary
            return "• Bitcoin mining sector update\n• Industry development details\n• See full article for specifics"
    
    def _process_headline_response(self, text: str) -> str:
        """Process and validate Gemini headline response."""
        import re
        
        # Remove common unwanted prefixes/suffixes
        text = text.replace("Here is a headline:", "").replace("Headline:", "")
        text = re.sub(r'^[\s\-\*]*', '', text)  # Remove leading spaces, dashes, asterisks
        text = text.strip()
        
        # Clean and truncate headline
        headline = self._clean_headline(text)
        return headline[:200] if len(headline) > 200 else headline
    
    def _process_summary_response(self, summary_text: str) -> str:
        """Process and clean the summary response from Gemini."""
        import re
        
        # Clean up any numbering that might have been added
        # Remove number prefixes like "1. ", "2. ", etc.
        summary_text = re.sub(r'^\d+\.\s*', '', summary_text, flags=re.MULTILINE)
        
        # If we have inline bullets, convert to line-break format
        if ' • ' in summary_text and '\n' not in summary_text:
            # Convert inline bullets to line breaks
            parts = [part.strip() for part in summary_text.split(' • ') if part.strip()]
            summary_text = '\n'.join([f'• {part}' if not part.startswith('•') else part for part in parts[:3]])
        elif '\n' in summary_text:
            # Already has line breaks, ensure proper bullet formatting
            lines = [line.strip() for line in summary_text.split('\n') if line.strip()]
            summary_text = '\n'.join([f'• {line}' if not line.startswith('•') else line for line in lines[:3]])
        else:
            # Single line without bullets, add bullet point
            summary_text = f'• {summary_text}'
        
        # Ensure it's not too long (accounting for line breaks)
        if len(summary_text) > 180:
            # Try to fit within limit by truncating last points
            lines = summary_text.split('\n')
            result_lines = []
            total_length = 0
            
            for line in lines:
                if total_length + len(line) + 1 <= 177:  # +1 for newline, leave room for "..."
                    result_lines.append(line)
                    total_length += len(line) + 1
                else:
                    break
            
            summary_text = '\n'.join(result_lines)
            if len(summary_text) > 180:
                summary_text = summary_text[:177] + "..."
                
        return summary_text
    
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
    def create_tweet_thread(article: Article, gemini_client: Optional[GeminiClient] = None) -> list[str]:
        """Create a complete tweet thread with catchy headline, summary, and URL."""
        thread = []
        
        logger.info(f"🧵 Creating tweet thread for: {article.title[:100]}...")
        logger.info(f"🤖 Gemini client available: {gemini_client is not None}")
        
        if gemini_client:
            try:
                logger.info("🎯 Using Gemini-powered thread generation...")
                # Generate Gemini-powered content
                headline = gemini_client.generate_catchy_headline(article)
                summary_text = gemini_client.generate_thread_summary(article)
                
                # Try to combine headline and summary in first tweet
                if summary_text:
                    combined_text = f"{headline}\n\n{summary_text}"
                    logger.info(f"📏 Combined text length: {len(combined_text)} chars")
                    
                    if len(combined_text) <= 280:
                        # Fits in one tweet - perfect!
                        logger.info("✅ Using combined format (headline + summary)")
                        thread.append(combined_text)
                    else:
                        # Too long - separate headline and summary
                        logger.info("📏 Text too long, using separate tweets")
                        thread.append(headline)
                        
                        # Check if summary fits in second tweet
                        if len(summary_text) <= 280:
                            thread.append(summary_text)
                        else:
                            # Summary too long, truncate with ellipsis
                            thread.append(summary_text[:277] + "...")
                else:
                    # No summary generated, just use headline
                    logger.info("⚠️ No summary generated, using headline only")
                    thread.append(headline)
                
                # Final tweet: URL only
                if article.url:
                    thread.append(article.url)
                
                logger.info(f"✅ Generated {len(thread)}-tweet thread with Gemini")
                return thread
                
            except Exception as e:
                logger.warning(f"❌ Gemini content generation failed: {e}")
                # Fall back to simple format if Gemini fails
        
        # Fallback: Simple format without Gemini
        logger.info("🔄 Using fallback simple tweet format")
        return TextProcessor._create_simple_tweet(article)
    
    @staticmethod
    def _create_simple_tweet(article: Article) -> list[str]:
        """Create simple thread (fallback when Gemini unavailable)."""
        thread = []
        
        # Clean title and add appropriate prefix based on article age
        title = TextProcessor._clean_title(article.title)
        
        # Select prefix based on article freshness (hour-based)
        if hasattr(article, 'is_fresh') and article.is_fresh:
            # Fresh articles (<1 hour) get urgent prefixes
            prefixes = ["BREAKING:", "JUST IN:"]
        elif hasattr(article, 'hours_old') and article.hours_old <= 6:
            # Recent articles (1-6 hours) get news prefixes
            prefixes = ["NEWS:", "UPDATE:"]
        else:
            # Older articles get report prefixes
            prefixes = ["REPORT:", "ANALYSIS:"]
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
            
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded (429): {e}")
            # Re-raise to be caught by calling code for rate limit handling
            raise
        except tweepy.Forbidden as e:
            logger.error(f"Twitter API forbidden (403): {e}")
            return None
        except tweepy.Unauthorized as e:
            logger.error(f"Twitter API unauthorized (401): {e}")
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
            
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded (429) during thread posting: {e}")
            # Re-raise to be caught by calling code for rate limit handling
            raise
        except tweepy.Forbidden as e:
            logger.error(f"Twitter API forbidden (403) during thread posting: {e}")
            return False
        except tweepy.Unauthorized as e:
            logger.error(f"Twitter API unauthorized (401) during thread posting: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            return False


class NewsAPI:
    """Enhanced EventRegistry/NewsAPI client with fresh content fetching."""
    
    def __init__(self, config: Config):
        self.config = config
        self._client = None
    
    def fetch_articles(self, max_articles: int = 20) -> List[Article]:
        """Fetch fresh Bitcoin mining articles using multiple EventRegistry endpoints."""
        try:
            # Lazy import and initialization
            if self._client is None:
                import eventregistry
                self._client = eventregistry.EventRegistry(
                    apiKey=self.config.eventregistry_api_key,
                    verboseOutput=False
                )
            
            # Strategy 1: Try to get very recent articles (last 60 minutes)
            recent_articles = self._fetch_minute_stream_articles(max_articles // 2)
            logger.info(f"Fetched {len(recent_articles)} recent articles (last 60 minutes)")
            
            # Strategy 2: Get additional articles from last 24 hours
            daily_articles = self._fetch_daily_articles(max_articles - len(recent_articles))
            logger.info(f"Fetched {len(daily_articles)} daily articles (last 24 hours)")
            
            # Combine and deduplicate
            all_articles = recent_articles + daily_articles
            unique_articles = self._deduplicate_articles(all_articles)
            
            # Convert to Article objects and filter for Bitcoin content
            content_fetcher = FullContentFetcher()  # Create content fetcher instance
            articles = [Article.from_dict(data, content_fetcher) for data in unique_articles[:max_articles]]
            filtered_articles = self._filter_bitcoin_articles(articles)
            
            # Add freshness information
            for article in filtered_articles:
                self._add_freshness_info(article)
            
            # Sort by freshness (most recent first)
            filtered_articles.sort(key=lambda a: getattr(a, 'hours_old', 999))
            
            logger.info(f"Final result: {len(filtered_articles)} fresh Bitcoin mining articles")
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Failed to fetch articles: {e}")
            return []
    
    def _fetch_minute_stream_articles(self, max_items: int = 10) -> List[dict]:
        """Fetch very recent articles using minuteStreamArticles endpoint."""
        try:
            import requests
            
            url = "https://eventregistry.org/api/v1/minuteStreamArticles"
            
            # Use the exact query structure from the provided example
            query_data = {
                "query": {
                    "$query": {
                        "keyword": "bitcoin mining",
                        "keywordLoc": "body"
                    }
                },
                "recentActivityArticlesUpdatesAfterMinsAgo": 60,
                "apiKey": self.config.eventregistry_api_key
            }
            
            response = requests.post(url, json=query_data, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', {}).get('results', [])
            return articles[:max_items]
            
        except Exception as e:
            logger.warning(f"Failed to fetch minute stream articles: {e}")
            return []
    
    def _fetch_daily_articles(self, max_items: int = 10) -> List[dict]:
        """Fetch recent articles using getArticles endpoint with date sorting."""
        try:
            import requests
            
            url = "https://eventregistry.org/api/v1/article/getArticles"
            
            # Use the exact query structure from the provided example  
            query_data = {
                "query": {
                    "$query": {
                        "keyword": "bitcoin mining",
                        "keywordLoc": "body"
                    },
                    "$filter": {
                        "forceMaxDataTimeWindow": "1"  # Last 1 day for freshness
                    }
                },
                "resultType": "articles",
                "articlesSortBy": "date",  # Sort by most recent first
                "includeConceptSynonyms": True,
                "includeConceptTrendingScore": True,
                "apiKey": self.config.eventregistry_api_key
            }
            
            response = requests.post(url, json=query_data, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', {}).get('results', [])
            return articles[:max_items]
            
        except Exception as e:
            logger.warning(f"Failed to fetch daily articles: {e}")
            return []
    
    def _deduplicate_articles(self, articles: List[dict]) -> List[dict]:
        """Remove duplicate articles based on URL."""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    def _add_freshness_info(self, article: 'Article') -> None:
        """Add precise freshness information to article for smart prefix selection."""
        article_date = article.date_published
        if article_date:
            try:
                if isinstance(article_date, str):
                    article_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
                
                hours_old = (datetime.now(article_date.tzinfo) - article_date).total_seconds() / 3600
                
                # Mark as fresh if less than 1 hour old (for JUST IN/BREAKING)
                article.is_fresh = hours_old <= 1.0
                article.hours_old = hours_old
                
            except (ValueError, TypeError, AttributeError):
                # If date parsing fails, mark as not fresh
                article.is_fresh = False
                article.hours_old = 999  # Very old
        else:
            article.is_fresh = False
            article.hours_old = 999

    def _filter_bitcoin_articles(self, articles: List[Article]) -> List[Article]:
        """Filter articles for Bitcoin mining relevance and add freshness information."""
        bitcoin_terms = ["bitcoin", "btc", "mining", "miner", "hash rate", "asic"]
        
        # Exclude articles about other cryptocurrencies
        crypto_exclusions = [
            "ethereum", "eth", "solana", "sol", "cardano", "ada", "polkadot", "dot",
            "chainlink", "link", "litecoin", "ltc", "ripple", "xrp", "dogecoin", "doge",
            "avalanche", "avax", "polygon", "matic", "cosmos", "atom", "tezos", "xtz",
            "binance coin", "bnb", "uniswap", "uni", "shiba", "shib", "pepe", "memecoin"
        ]
        
        filtered = []
        for article in articles:
            text = f"{article.title} {article.body}".lower()
            
            # Check for Bitcoin mining relevance
            if any(term in text for term in bitcoin_terms):
                # Exclude if it mentions other cryptocurrencies significantly
                other_crypto_mentions = sum(1 for term in crypto_exclusions if term in text)
                bitcoin_mentions = sum(1 for term in ["bitcoin", "btc"] if term in text)
                
                # Skip if other cryptos are mentioned more than Bitcoin or equally
                if other_crypto_mentions > 0 and other_crypto_mentions >= bitcoin_mentions:
                    logger.info(f"Filtered out multi-crypto article: {article.title[:50]}...")
                    continue
                
                # Mark if this is a chip/hardware article for enhanced processing
                chip_terms = ["chip", "semiconductor", "processor", "hardware", "asic", "gpu", "cpu"]
                article.is_chip_article = any(term in text for term in chip_terms)
                
                # Add article freshness information for smart prefix selection
                article_date = article.date_published
                if article_date:
                    try:
                        if isinstance(article_date, str):
                            article_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
                        
                        days_old = (datetime.now(article_date.tzinfo) - article_date).days
                        
                        # Skip articles older than 7 days completely
                        if days_old > 7:
                            continue
                            
                        # Mark freshness for prefix selection (fresh = 1 day old or less)
                        article.is_fresh = days_old <= 1
                        
                    except (ValueError, TypeError, AttributeError):
                        # If date parsing fails, mark as not fresh
                        article.is_fresh = False
                else:
                    article.is_fresh = False
                    
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
                    logger.info("Attempting to initialize Gemini client...")
                    self._gemini = GeminiClient(self.config.gemini_api_key)
                    logger.info("✅ Gemini client initialized successfully")
                except Exception as e:
                    logger.warning(f"❌ Failed to initialize Gemini client: {e}")
                    self._gemini = None
            else:
                logger.info("⚠️  No Gemini API key provided - using fallback mode")
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
                cooldown_data = self.storage.load_json(self.config.rate_limit_file, {})
                cooldown_end = cooldown_data.get('cooldown_end', 'unknown')
                logger.info(f"⏳ Rate limit cooldown active until: {cooldown_end}")
                logger.info("🚫 Skipping run due to active rate limit cooldown")
                return True
            
            # Check minimum interval
            if not self._can_run_now():
                last_run = self.posted_data.get("last_run_time")
                logger.info(f"⏱️ Last run: {last_run}")
                logger.info(f"🚫 Minimum interval ({self.config.min_interval_minutes} minutes) not yet reached. Skipping run.")
                return True
            
            # Fetch new articles first (prioritize fresh content)
            logger.info("Fetching new articles...")
            try:
                articles = self.news.fetch_articles(self.config.max_articles)
                
                # Log ALL fetched articles for daily briefing system
                self._log_all_articles(articles)
                
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
                
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded (429): {e}")
            logger.info("Setting rate limit cooldown to prevent further requests")
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
                
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded during article posting: {e}")
            # Re-raise to be handled by main run() method
            raise
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
        logger.warning(f"Failed to post tweet - setting rate limit cooldown for {self.config.cooldown_hours} hours")
        
        cooldown_data = TimeManager.create_cooldown_data(self.config.cooldown_hours)
        
        # Log cooldown details for debugging
        cooldown_end = cooldown_data.get('cooldown_end', 'unknown')
        logger.info(f"⏳ Rate limit cooldown active until: {cooldown_end}")
        logger.info(f"🚫 Bot will skip runs for the next {self.config.cooldown_hours} hours")
        
        if self.storage.save_json(self.config.rate_limit_file, cooldown_data):
            logger.info(f"✅ Cooldown data saved to {self.config.rate_limit_file}")
        else:
            logger.error(f"❌ Failed to save cooldown data to {self.config.rate_limit_file}")
    
    def _log_all_articles(self, articles: List[Article]) -> bool:
        """Log ALL fetched articles to articles_log.json for daily briefing system.
        
        This method maintains a comprehensive log of all articles fetched from EventRegistry,
        regardless of whether they are posted to Twitter. The daily briefing system uses
        this log to generate comprehensive reports.
        
        Args:
            articles: List of articles to log
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        if not articles:
            logger.debug("No articles to log")
            return True
            
        try:
            # Load existing articles log
            articles_log_file = "articles_log.json"
            existing_log = self.storage.load_json(articles_log_file, {
                "last_updated": None,
                "total_articles": 0,
                "daily_articles": []
            })
            
            # Get current date for daily grouping
            current_date = datetime.now().strftime("%Y-%m-%d")
            today = datetime.now().date()
            
            # Initialize today's entries if needed
            daily_articles = existing_log.get("daily_articles", [])
            today_entry = None
            
            # Find or create today's entry
            for entry in daily_articles:
                if entry.get("date") == current_date:
                    today_entry = entry
                    break
            
            if not today_entry:
                today_entry = {
                    "date": current_date,
                    "articles": [],
                    "fetch_count": 0
                }
                daily_articles.append(today_entry)
            
            # Track URLs to avoid duplicates within today
            existing_urls = {article.get("url") for article in today_entry["articles"]}
            
            # Add new articles to today's log
            new_articles_count = 0
            for article in articles:
                if article.url not in existing_urls:
                    article_data = {
                        "url": article.url,
                        "title": article.title,
                        "description": getattr(article, 'description', '') or '',
                        "source": getattr(article, 'source', '') or '',
                        "dateTimePub": getattr(article, 'dateTimePub', '') or '',
                        "fetched_at": datetime.now().isoformat(),
                        "posted_to_twitter": article.url in self.posted_data.get("posted_uris", []),
                        "queued_for_twitter": any(qa.get("url") == article.url for qa in self.posted_data.get("queued_articles", [])),
                        "lang": getattr(article, 'lang', '') or '',
                        "isDuplicate": getattr(article, 'isDuplicate', False),
                        "wgt": getattr(article, 'wgt', 0)
                    }
                    today_entry["articles"].append(article_data)
                    existing_urls.add(article.url)
                    new_articles_count += 1
            
            # Update metadata
            today_entry["fetch_count"] += 1
            existing_log["daily_articles"] = daily_articles
            existing_log["total_articles"] = sum(len(entry["articles"]) for entry in daily_articles)
            existing_log["last_updated"] = datetime.now().isoformat()
            
            # Clean old entries (keep only last 30 days)
            cutoff_date = today - timedelta(days=30)
            existing_log["daily_articles"] = [
                entry for entry in daily_articles 
                if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= cutoff_date
            ]
            
            # Save the updated log
            if self.storage.save_json(articles_log_file, existing_log):
                logger.info(f"📊 Logged {new_articles_count} new articles for daily briefing (total today: {len(today_entry['articles'])})")
                return True
            else:
                logger.error("Failed to save articles log")
                return False
                
        except Exception as e:
            logger.error(f"Failed to log articles for daily briefing: {e}")
            return False
    
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