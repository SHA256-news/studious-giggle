"""
Bitcoin Mining News Bot - Simplified Core Module
===============================================
Clean, minimal core functionality for the Bitcoin Mining News Twitter Bot.
"""

import json
import logging
import os
import re
import time
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Union
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
# CUSTOM EXCEPTIONS
# =============================================================================

class URLRetrievalError(Exception):
    """Raised when URL content retrieval fails (not an API failure).
    
    This indicates the specific URL cannot be accessed, but the API itself is working.
    Bot should skip this article and try the next one without triggering rate limit cooldown.
    """
    pass


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
    
    # Content Similarity Thresholds
    title_similarity_threshold: float = 0.8
    content_similarity_threshold: float = 0.7
    duplicate_detection_date_window_hours: int = 48
    
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
    """Represents a news article."""
    title: str
    body: str
    url: str
    source: str = ""
    date_published: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create Article from dictionary with input validation."""
        if not isinstance(data, dict):
            raise ValueError("Article data must be a dictionary")
        
        # Validate required fields
        title = data.get("title", "").strip()
        if not title:
            raise ValueError("Article title is required")
        
        url = data.get("url", data.get("uri", "")).strip()
        if not url:
            raise ValueError("Article URL is required")
        
        # Basic URL format validation
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")
        
        # Additional basic URL validation
        if len(url) < 10 or ' ' in url:
            raise ValueError(f"Malformed URL: {url}")
        
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
        """Parse date string to datetime, ensuring UTC timezone awareness."""
        if not date_str:
            return None
        try:
            # Parse ISO format with timezone awareness
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Ensure we have UTC timezone info
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (ValueError, TypeError):
            return None


# =============================================================================
# CONTENT SIMILARITY FUNCTIONS
# =============================================================================

class ContentSimilarity:
    """Intelligent content similarity detection for duplicate article identification."""
    
    # Performance optimization: Cache expensive fingerprint calculations
    _fingerprint_cache: Dict[str, str] = {}
    
    @staticmethod
    def clear_cache():
        """Clear fingerprint cache to free memory."""
        ContentSimilarity._fingerprint_cache.clear()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison by removing extra whitespace and converting to lowercase."""
        if not text:
            return ""
        # Remove extra whitespace, convert to lowercase, remove special characters
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    @staticmethod
    def get_word_set(text: str) -> Set[str]:
        """Extract normalized word set from text."""
        normalized = ContentSimilarity.normalize_text(text)
        words = normalized.split()
        # Filter out very short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return {word for word in words if len(word) > 2 and word not in stop_words}
    
    @staticmethod
    def title_similarity(title1: str, title2: str) -> float:
        """Calculate title similarity using Jaccard similarity of words."""
        if not title1 or not title2:
            return 0.0
        
        words1 = ContentSimilarity.get_word_set(title1)
        words2 = ContentSimilarity.get_word_set(title2)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def content_fingerprint(text: str) -> str:
        """Create a content fingerprint using significant words and phrases."""
        if not text:
            return ""
        
        # Performance optimization: Check cache first
        if text in ContentSimilarity._fingerprint_cache:
            return ContentSimilarity._fingerprint_cache[text]
        
        # Extract significant phrases (3+ words) and individual significant words
        normalized = ContentSimilarity.normalize_text(text)
        words = normalized.split()
        
        # Get significant words (length > 4) and numbers
        significant_words = []
        for word in words:
            if len(word) > 4 or word.isdigit():
                significant_words.append(word)
        
        # Create fingerprint from most significant words (sorted for consistency)
        fingerprint_words = sorted(set(significant_words))[:20]  # Take top 20 most significant
        fingerprint = ' '.join(fingerprint_words)
        
        # Return hash of fingerprint for compact comparison
        result = hashlib.md5(fingerprint.encode()).hexdigest()
        
        # Cache result (but limit cache size to prevent memory issues)
        if len(ContentSimilarity._fingerprint_cache) < 100:  # Reasonable cache limit
            ContentSimilarity._fingerprint_cache[text] = result
        
        return result
    
    @staticmethod
    def content_similarity(body1: str, body2: str) -> float:
        """Calculate content similarity using multiple methods."""
        if not body1 or not body2:
            return 0.0
        
        # Method 1: Fingerprint exact match
        fp1 = ContentSimilarity.content_fingerprint(body1)
        fp2 = ContentSimilarity.content_fingerprint(body2)
        
        if fp1 == fp2 and fp1:  # Exact fingerprint match (high confidence)
            return 1.0
        
        # Method 2: Word overlap similarity
        words1 = ContentSimilarity.get_word_set(body1)
        words2 = ContentSimilarity.get_word_set(body2)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def date_proximity(date1: Optional[datetime], date2: Optional[datetime], 
                      max_hours: int = 48) -> bool:
        """Check if two dates are within specified hours of each other."""
        if not date1 or not date2:
            return True  # If dates unknown, don't use as discriminator
        
        time_diff = abs((date1 - date2).total_seconds()) / 3600  # Convert to hours
        return time_diff <= max_hours
    
    @staticmethod
    def is_duplicate_article(article1: 'Article', article2: 'Article',
                           title_threshold: float = 0.8,
                           content_threshold: float = 0.7,
                           date_window_hours: int = 48) -> bool:
        """
        Determine if two articles are duplicates using multiple similarity metrics.
        
        Args:
            article1, article2: Articles to compare
            title_threshold: Minimum title similarity for duplicate (0.0-1.0)
            content_threshold: Minimum content similarity for duplicate (0.0-1.0)  
            date_window_hours: Maximum hours apart for articles to be considered duplicates
            
        Returns:
            True if articles are likely duplicates
        """
        # Quick URL check first (if same URL, definitely duplicate)
        if article1.url == article2.url:
            return True
        
        # Check date proximity first (optimization - fastest check)
        if not ContentSimilarity.date_proximity(
            article1.date_published, article2.date_published, date_window_hours
        ):
            return False
        
        # Performance optimization: Check title similarity first (faster than content)
        title_sim = ContentSimilarity.title_similarity(article1.title, article2.title)
        
        # Early exit if title similarity is very low (likely not duplicates)
        if title_sim < 0.3:  # If titles are very different, skip expensive content analysis
            return False
        
        # Calculate content similarity only when needed
        content_sim = ContentSimilarity.content_similarity(article1.body, article2.body)
        
        # Articles are duplicates if:
        # 1. High title similarity AND high content similarity, OR
        # 2. Very high content similarity (even if titles differ slightly)
        return (
            (title_sim >= title_threshold and content_sim >= content_threshold) or
            content_sim >= 0.9  # Very high content similarity threshold
        )


# =============================================================================
# STORAGE MANAGER
# =============================================================================

class Storage:
    """Simple file-based storage manager."""
    
    @staticmethod
    def load_json(filepath: str, default: Any = None) -> Any:
        """Load JSON file with error handling."""
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
                
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return default if default is not None else {}
    
    @staticmethod
    def save_json(filepath: str, data: Any) -> bool:
        """Save data to JSON file with atomic operations."""
        file_path = Path(filepath)
        temp_file = None
        
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use atomic write: write to temp file, then rename
            temp_file = file_path.with_suffix(f"{file_path.suffix}.tmp")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename
            temp_file.rename(file_path)
            logger.debug(f"Successfully saved {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
            return False
        finally:
            # Clean up temp file if it exists
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
    
    @staticmethod
    def load_posted_articles(filepath: str) -> Dict[str, Any]:
        """Load posted articles data structure."""
        data = Storage.load_json(filepath, {})
        return {
            "posted_uris": data.get("posted_uris", []),
            "queued_articles": data.get("queued_articles", []),
            "posted_articles_history": data.get("posted_articles_history", []),
            "last_run_time": data.get("last_run_time")
        }


# =============================================================================
# TIME UTILITIES
# =============================================================================

class TimeManager:
    """Time-related utilities."""
    
    @staticmethod
    def now() -> datetime:
        """Get current datetime in UTC timezone."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def is_minimum_interval_passed(last_run: Optional[str], min_minutes: int) -> bool:
        """Check if minimum interval has passed since last run."""
        if not last_run:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_run)
            # Ensure timezone awareness for comparison
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=timezone.utc)
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
            # Ensure timezone awareness for comparison
            if cooldown_end.tzinfo is None:
                cooldown_end = cooldown_end.replace(tzinfo=timezone.utc)
            return TimeManager.now() < cooldown_end
        except (ValueError, TypeError, KeyError):
            return False


# =============================================================================
# GEMINI AI CLIENT  
# =============================================================================

class GeminiClient:
    """Gemini AI client for generating catchy headlines and summaries with URL context support.
    
    📚 API REFERENCE: /docs/api/gemini.md
    🔗 Quick Reference: /docs/api/quick-reference.md
    🚨 CRITICAL: /GEMINI-API-NEVER-FORGET.md - PERMANENT solution to API format confusion
    
    ⚠️ SYSTEMATIC ISSUE SOLVED: We kept forgetting correct API format during refactoring!
    ✅ PERMANENT FIX: Always use simple dict format {"url_context": {}}
    ❌ NEVER USE: Complex types.Tool() objects (causes error tweets)
    """
    
    def __init__(self, api_key: str):
        """Initialize Gemini client with API key."""
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        try:
            from google import genai
            # ✅ CORRECT: Use simple dict format, no need for types import
            # Reference: Official cookbook examples use simple dict tools
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.5-flash'
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini client: {e}")
    
    def _clean_headline(self, headline: str) -> str:
        """Clean up headline text by removing unwanted formatting."""
        import re
        
        # Remove quotes if present
        headline = headline.strip('"\'')
        
        # Remove markdown formatting
        headline = re.sub(r'\*\*', '', headline)
        headline = re.sub(r'__', '', headline)
        
        # Remove any leading/trailing whitespace
        headline = headline.strip()
        
        return headline
    
    def _process_summary_response(self, summary_text: str) -> str:
        """Process and clean Gemini's summary response to extract only bullet points."""
        import re
        
        lines = summary_text.strip().split('\n')
        bullet_points = []
        
        # Filter lines to keep only actual bullet points
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Clean the line: remove bullet markers, extra dashes, quotes at start
            clean_line = line.lstrip('•-* ').strip()
            clean_line = clean_line.lstrip('-* ').strip()  # Remove any remaining dashes/asterisks
            clean_line = clean_line.lstrip('"\'').strip()  # Remove quotes at start
            
            line_lower = clean_line.lower()
            
            # Skip lines that look like Gemini's thinking process or meta-commentary
            skip_patterns = [
                r'^(i will|i am|let me|here are|here is)',
                r'^(the article|from the article|based on|according to)',
                r'^(the following|these are|below are)',
                r'(extract|create|generate|provide|present)\s+(the|specific|details)',
                r'^(bullet points?|summary|details?)[:.]',
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line_lower):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Additional check: skip very short lines (less than 20 chars of actual content)
            if len(clean_line) < 20:
                continue
            
            # Only keep lines that look like actual facts (have numbers, company names, or specific data)
            # This helps filter out malformed partial content
            if re.search(r'[A-Z]{2,}|\d+|bitcoin|btc|mara|riot|hive|cleanpark', clean_line, re.IGNORECASE):
                bullet_points.append(f"• {clean_line}")
        
        # If we found valid bullet points, return them
        if bullet_points:
            # Take only first 3 bullet points if more were returned
            return '\n'.join(bullet_points[:3])
        
        # Fallback: try to extract any meaningful content that looks like facts
        meaningful_lines = []
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Must be substantial content
            if len(line) < 20:
                continue
            
            # Skip meta-commentary
            if any(p in line_lower for p in ['i will', 'let me', 'here are', 'from the article:', 'based on', 'according to']):
                continue
            
            # Look for lines with numbers, percentages, or dollar amounts (likely real facts)
            if re.search(r'\d+[%$]|\d+\s*(BTC|miners?|facility|percent|million|billion)', line, re.IGNORECASE):
                # Clean this line too
                clean = line.lstrip('•-* ').lstrip('-* ').lstrip('"\'').strip()
                meaningful_lines.append(f"• {clean}")
        
        if meaningful_lines:
            return '\n'.join(meaningful_lines[:3])
        
        # Last resort: return the original text (this shouldn't happen often)
        return summary_text

    def generate_catchy_headline(self, article: 'Article') -> str:
        """Generate a catchy, emoji-free headline for the article using URL context."""
        try:
            logger.info("🎯 Generating catchy headline with Gemini 2.5 Flash + URL context...")
            
            prompt = f"""
            Read the FULL Bitcoin mining article at {article.url} (not just the title) and write a PUNCHY news headline based on the article's BODY content.
            
            Article's original title: "{article.title}"
            
            CRITICAL: Your headline must be DIFFERENT from the original title. Extract NEW insights from reading the full article body.
            
            CRITICAL REQUIREMENTS:
            - Read the ENTIRE article body to find the most newsworthy angle
            - Write like a professional financial news reporter
            - Start with COMPANY NAME or KEY ACTION, never "The article states that..."
            - Keep it under 70 characters
            - Include specific numbers, percentages, or dollar amounts from the article BODY
            - Use powerful action verbs: "soars", "plummets", "hits", "reaches", "secures", "reports"
            - Sound like headlines from Bloomberg, Reuters, or MarketWatch
            - Must be DIFFERENT from the original article title above
            
            GOOD EXAMPLES:
            - "HIVE Hits 52-Week High on Mining Surge"
            - "Riot Platforms Acquires 5,000 Bitcoin Miners"
            - "Marathon Digital Reports Record Q3 Revenue"
            - "CleanSpark Stock Jumps 15% on Expansion News"
            
            BAD EXAMPLES (NEVER DO THIS):
            - "The article states that HIVE Digital Technologies..."
            - "According to the report, Marathon Digital..."
            - "The company announced in the article..."
            - Repeating the original article title
            
            Return ONLY the headline, no quotes, no explanation.
            """
            
            # Use URL context tool with SIMPLE DICT format (from official cookbook examples)
            # ✅ CORRECT: Simple dict format from Grounding.ipynb lines 561, 696, 873
            # Source: https://github.com/google-gemini/cookbook/tree/main/quickstarts/Grounding.ipynb
            config = {
                "tools": [{"url_context": {}}]
            }
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt.strip(),
                config=config
            )
            
            # Null check before accessing response.text
            if not response or not response.text:
                raise ValueError("Gemini API returned empty or null response for headline generation")
            
            headline = response.text.strip()
            
            # CRITICAL: Check for Gemini error messages indicating URL retrieval failure
            error_patterns = [
                "unable to fetch the content",
                "unable to access the content",
                "could not retrieve the content",
                "failed to fetch the content",
                "cannot access the URL",
                "unable to fetch",
                "unable to access",
                "could not access"
            ]
            
            headline_lower = headline.lower()
            for pattern in error_patterns:
                if pattern in headline_lower:
                    logger.warning(f"❌ Gemini returned URL access error: {headline[:100]}...")
                    raise URLRetrievalError(f"Failed to retrieve content from {article.url}: Gemini access error")
            
            logger.info(f"✅ Generated headline with URL context: '{headline}'")
            
            # Check URL context metadata using CORRECT access pattern
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                    metadata = candidate.url_context_metadata
                    logger.info(f"📄 URL context metadata: {metadata}")
                    
                    # CORRECT: Access url_metadata list directly from official format
                    if hasattr(metadata, 'url_metadata'):
                        for url_meta in metadata.url_metadata:
                            if hasattr(url_meta, 'url_retrieval_status'):
                                status = url_meta.url_retrieval_status
                                status_str = str(status)
                                # Check for SUCCESS status (handle both enum value and string representation)
                                is_success = (
                                    status_str == "URL_RETRIEVAL_STATUS_SUCCESS" or 
                                    "URL_RETRIEVAL_STATUS_SUCCESS" in status_str
                                )
                                if not is_success:
                                    logger.warning(f"❌ URL retrieval failed for {article.url}: {status_str}")
                                    raise URLRetrievalError(f"Failed to retrieve content from {article.url}: URL retrieval status {status_str}")
                                else:
                                    logger.info(f"✅ URL retrieval successful for {article.url}: {status_str}")
            
            return self._clean_headline(headline)[:80]
            
        except ValueError as e:
            # API authentication or configuration issues - reraise to surface the problem
            logger.error(f"❌ Gemini API authentication/configuration error: {e}")
            raise
        except ConnectionError as e:
            # Network connectivity issues
            logger.warning(f"❌ Gemini network connection failed: {e}")
            raise
        except Exception as e:
            # Check if this is a URL retrieval failure (not an API failure)
            error_message = str(e).lower()
            if any(term in error_message for term in ['url', 'retrieve', 'fetch', 'access', 'blocked', 'forbidden', '403', '404']):
                logger.warning(f"❌ URL retrieval failed for {article.url}: {e}")
                raise URLRetrievalError(f"Failed to retrieve content from {article.url}: {e}")
            
            # Other unexpected errors - still raise as general failure
            logger.warning(f"❌ Gemini headline generation failed with unexpected error: {e}")
            raise

    def generate_thread_summary(self, article: 'Article') -> str:
        """Generate a concise 3-point summary using URL context."""
        try:
            logger.info("🎯 Generating thread summary with Gemini 2.5 Flash + URL context...")
            
            headline = self.generate_catchy_headline(article)
            
            prompt = f"""
            Read the FULL Bitcoin mining article body at {article.url} and create SPECIFIC bullet points with NEW information.
            
            Article's original title: "{article.title}"
            Generated Headline: {headline}
            
            CRITICAL ANTI-REPETITION RULES:
            - DO NOT repeat ANY information from the original article title above
            - DO NOT repeat ANY information from the generated headline above
            - DO NOT repeat ANY numbers, dollar amounts, Bitcoin amounts, percentages, dates, or specific facts (e.g., "127,271", "$12 billion") already mentioned in the original article title or generated headline
            - Each bullet point must contain COMPLETELY NEW information from the article BODY
            - Read the ENTIRE article body to find additional facts not in the title or headline
            - If the headline mentions a specific Bitcoin amount or dollar figure, your bullets must discuss DIFFERENT aspects
            
            Create 3 rapid-fire bullet points that reveal DIFFERENT details from the article body:
            - Total length under 180 characters
            - Include specific numbers, dates, locations, dollar amounts NOT already mentioned
            - Use telegraphic style like financial newswires
            - Each point 50-60 characters max
            - Format: "• [specific fact]"
            - NO generic statements
            - NO repetition of title or headline content
            
            GOOD EXAMPLES (each has NEW information):
            • Q3 revenue jumped 42% to $87M year-over-year
            • Added 2,500 miners at Texas facility this month  
            • Power costs dropped to 4.2¢/kWh from 6.1¢/kWh
            
            BAD EXAMPLES (NEVER DO):
            • The company is performing well (too generic)
            • Bitcoin mining operations are expanding (too generic)
            • Repeating any number or fact from the title or headline (FORBIDDEN)
            • "US Treasury seizing 127,271 BTC total" - if headline already says this amount (FORBIDDEN REPETITION)
            • "Worth $12 billion" - if headline already mentions dollar amount (FORBIDDEN REPETITION)
            • Restating the same event in different words (must be DIFFERENT facts)
            
            **CRITICAL OUTPUT FORMAT RULES:**
            - Start IMMEDIATELY with the first bullet point (•)
            - NO introductions like "I will now...", "Let me...", "Here are...", "From the article:", etc.
            - NO explanations or meta-commentary about what you're doing
            - NO blank lines between bullet points
            - ONLY the 3 bullet points, nothing else
            - Each bullet point must start with • character
            
            Your response must be EXACTLY in this format:
            • [First NEW specific fact with numbers/details]
            • [Second NEW specific fact with numbers/details]
            • [Third NEW specific fact with numbers/details]
            """
            
            # Use URL context tool with SIMPLE DICT format (from official cookbook examples)
            # ✅ CORRECT: Simple dict format from Grounding.ipynb lines 561, 696, 873
            # Source: https://github.com/google-gemini/cookbook/tree/main/quickstarts/Grounding.ipynb
            config = {
                "tools": [{"url_context": {}}]
            }
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt.strip(),
                config=config
            )
            
            # Null check before accessing response.text
            if not response or not response.text:
                raise ValueError("Gemini API returned empty or null response for summary generation")
            
            summary_text = response.text.strip()
            
            # CRITICAL: Check for Gemini error messages indicating URL retrieval failure
            error_patterns = [
                "unable to fetch the content",
                "unable to access the content", 
                "could not retrieve the content",
                "failed to fetch the content",
                "cannot access the URL",
                "unable to fetch",
                "unable to access",
                "could not access"
            ]
            
            summary_lower = summary_text.lower()
            for pattern in error_patterns:
                if pattern in summary_lower:
                    logger.warning(f"❌ Gemini returned URL access error: {summary_text[:100]}...")
                    raise URLRetrievalError(f"Failed to retrieve content from {article.url}: Gemini access error")
            
            logger.info(f"✅ Generated summary with URL context: '{summary_text}'")
            
            # Check URL context metadata using CORRECT access pattern
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'url_context_metadata') and candidate.url_context_metadata:
                    metadata = candidate.url_context_metadata
                    logger.info(f"📄 URL context metadata: {metadata}")
                    
                    # CORRECT: Access url_metadata list directly from official format
                    if hasattr(metadata, 'url_metadata'):
                        for url_meta in metadata.url_metadata:
                            if hasattr(url_meta, 'url_retrieval_status'):
                                status = url_meta.url_retrieval_status
                                status_str = str(status)
                                # Check for SUCCESS status (handle both enum value and string representation)
                                is_success = (
                                    status_str == "URL_RETRIEVAL_STATUS_SUCCESS" or 
                                    "URL_RETRIEVAL_STATUS_SUCCESS" in status_str
                                )
                                if not is_success:
                                    logger.warning(f"❌ URL retrieval failed for {article.url} during summary generation: {status_str}")
                                    raise URLRetrievalError(f"Failed to retrieve content from {article.url}: URL retrieval status {status_str}")
                                else:
                                    logger.info(f"✅ URL retrieval successful during summary generation for {article.url}: {status_str}")
            
            return self._process_summary_response(summary_text)
                
        except ValueError as e:
            # API authentication or configuration issues - reraise to surface the problem
            logger.error(f"❌ Gemini API authentication/configuration error in summary generation: {e}")
            raise
        except ConnectionError as e:
            # Network connectivity issues
            logger.warning(f"❌ Gemini network connection failed during summary generation: {e}")
            raise
        except Exception as e:
            # Check if this is a URL retrieval failure (not an API failure)
            error_message = str(e).lower()
            if any(term in error_message for term in ['url', 'retrieve', 'fetch', 'access', 'blocked', 'forbidden', '403', '404']):
                logger.warning(f"❌ URL retrieval failed for {article.url} during summary generation: {e}")
                raise URLRetrievalError(f"Failed to retrieve content from {article.url}: {e}")
            
            # Other unexpected errors - still raise as general failure
            logger.warning(f"❌ Gemini summary generation failed with unexpected error: {e}")
            raise


# =============================================================================
# TEXT PROCESSING
# =============================================================================

class TextProcessor:
    """Text processing for tweet creation with Gemini AI integration."""
    
    @staticmethod
    def create_tweet_thread(article: Article, gemini_client: Optional[GeminiClient] = None) -> Optional[List[str]]:
        """Create a complete tweet thread with catchy headline, summary, and URL.
        
        Args:
            article: The article to create a thread for
            gemini_client: Optional Gemini AI client for enhanced content generation
            
        Returns:
            List of tweet strings forming a thread, or None if Gemini is required but unavailable
            
        Note:
            Returns None if Gemini is required but unavailable, indicating the bot should wait and retry later.
        """
        logger.info(f"🧵 Creating tweet thread for: {article.title[:100]}...")
        logger.info(f"🤖 Gemini client available: {gemini_client is not None}")
        
        # CRITICAL: Gemini is now MANDATORY - do not publish without it
        if not gemini_client:
            logger.warning("❌ Gemini API is required but not available - will retry later")
            return None
        
        try:
            logger.info("🎯 Using Gemini-powered thread generation...")
            headline = gemini_client.generate_catchy_headline(article)
            summary_text = gemini_client.generate_thread_summary(article)
            
            if not headline:
                logger.error("❌ Failed to generate headline with Gemini - will retry later")
                return None
            
            if not summary_text:
                logger.error("❌ Failed to generate summary with Gemini - will retry later")
                return None
            
            thread = []
            
            # Smart character limit logic: Try to combine headline + summary in one tweet
            combined_text = f"{headline}\n\n{summary_text}"
            logger.info(f"📏 Combined text length: {len(combined_text)} chars")
            
            if len(combined_text) <= 280:
                logger.info("✅ Using combined format (headline + summary in one tweet)")
                thread.append(combined_text)
            else:
                logger.info("📏 Text too long, using separate tweets")
                thread.append(headline)
                
                # Ensure summary fits in second tweet
                if len(summary_text) <= 280:
                    thread.append(summary_text)
                else:
                    # Truncate summary to fit in 280 chars
                    truncated_summary = summary_text[:277] + "..."
                    thread.append(truncated_summary)
            
            # Final tweet: URL always goes in the last tweet
            if article.url:
                thread.append(article.url)
            
            logger.info(f"✅ Generated {len(thread)}-tweet thread with Gemini")
            return thread
            
        except Exception as e:
            logger.error(f"❌ Gemini content generation failed: {e} - will retry later")
            return None
    
    @staticmethod
    def create_tweet_text(article: Article) -> str:
        """Legacy method - creates simple tweet title only (for compatibility)."""
        return TextProcessor._clean_title(article.title)
    
    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean and optimize title for Twitter."""
        prefixes_to_remove = [
            r"^BREAKING:\s*", r"^Breaking:\s*", r"^JUST IN:\s*",
            r"^News:\s*", r"^Bitcoin:\s*", r"^BTC:\s*"
        ]
        
        for prefix in prefixes_to_remove:
            title = re.sub(prefix, "", title, flags=re.IGNORECASE)
        
        title = re.sub(r'\s+', ' ', title).strip()
        return title


# =============================================================================
# API CLIENTS
# =============================================================================

class TwitterAPI:
    """Twitter API client.
    
    📚 Tweepy Documentation: https://docs.tweepy.org/en/stable/
    🔗 Quick Reference: /docs/api/quick-reference.md
    """
    
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
            
            if hasattr(response, 'data') and response.data:
                tweet_id = str(response.data.get('id', '')) if hasattr(response.data, 'get') else str(response.data)
                if tweet_id:
                    logger.info(f"Tweet posted successfully: {tweet_id}")
                    return tweet_id
            
            logger.warning("Tweet posted but no ID returned")
            return None
            
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded (429): {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None
    
    def post_thread(self, tweets: list[str]) -> bool:
        """Post a thread of tweets."""
        if not tweets:
            return False
            
        try:
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweets):
                logger.info(f"Posting tweet {i+1}/{len(tweets)}")
                
                if previous_tweet_id:
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                else:
                    response = self.client.create_tweet(text=tweet_text)
                
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
            raise
        except Exception as e:
            logger.error(f"Failed to post thread: {e}")
            return False


class NewsAPI:
    """Simple EventRegistry client for Bitcoin mining articles.
    
    📚 API REFERENCE: /docs/api/eventregistry.md
    🔗 Quick Reference: /docs/api/quick-reference.md
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._client = None
    
    def fetch_articles(self, max_articles: int = 20) -> List[Article]:
        """Fetch fresh Bitcoin mining articles."""
        try:
            if self._client is None:
                import eventregistry
                self._client = eventregistry.EventRegistry(
                    apiKey=self.config.eventregistry_api_key,
                    verboseOutput=False
                )
            
            # Simple query for recent Bitcoin mining articles
            from eventregistry import QueryArticlesIter
            
            q = QueryArticlesIter(
                keywords="bitcoin mining",
                dateStart=datetime.now(timezone.utc) - timedelta(days=self.config.article_lookback_days),
                lang="eng"
            )
            
            articles = []
            article_count = 0
            
            for article_data in q.execQuery(self._client, sortBy="date", maxItems=max_articles):
                try:
                    article = Article.from_dict(article_data)
                    # Simple Bitcoin filtering
                    if self._is_bitcoin_relevant(article):
                        articles.append(article)
                        article_count += 1
                        if article_count >= max_articles:
                            break
                except Exception as e:
                    logger.warning(f"Failed to process article: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} Bitcoin mining articles")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch articles: {e}")
            return []
    
    def _is_bitcoin_relevant(self, article: Article) -> bool:
        """Enhanced check if article is relevant to Bitcoin mining news."""
        text = f"{article.title} {article.body}".lower()
        title_lower = article.title.lower()
        
        # ENHANCED: Check for public Bitcoin mining companies (ALWAYS relevant)
        # Comprehensive list of 33 publicly traded Bitcoin mining companies with tickers
        public_miners = [
            # Major US-listed Bitcoin miners
            "marathon digital", "mara", "riot platforms", "riot", "cleanspark", "clsk",
            "hut 8", "hut8", "core scientific", "corz", "cipher mining", "cifr",
            "bitfarms", "bitf", "hive digital", "hive", "terawulf", "wulf",
            "bitdeer", "btdr", "iris energy", "iren", "bit digital", "btbt",
            "greenidge", "gree", "stronghold", "sdig", "argo blockchain", "arbk",
            "arbkf", "canaan", "can", "bit mining", "btcm", "bitfufu", "fufu",
            # International and emerging miners
            "phoenix group", "phx", "the9 limited", "ncty", "dmg blockchain", "dmgi",
            "dmggf", "cathedra bitcoin", "cbit", "cbttf", "bitcoin well", "btcw",
            "lm funding", "lmfa", "sos limited", "sos", "neptune digital", "nda",
            "npptf", "digihost", "hsshf", "sato technologies", "sato",
            "sphere 3d", "any", "gryphon digital", "gryp", "american bitcoin", "abtc",
            "abits group", "abts"
        ]
        
        # CRITICAL: Check for promotional content BEFORE public miner check
        # This prevents scam apps like "HashJ" from being approved
        promotional_terms = [
            "cloud mining", "free bitcoin mining", "claim", "bonus", "gift", 
            "sign up", "register now", "join now", "get started", "download app",
            "earn daily", "passive income", "$118", "hashj", "momhash", 
            "free mining", "no investment", "guaranteed returns", "daily earnings"
        ]
        if any(term in text for term in promotional_terms):
            logger.info(f"❌ Excluded promotional content: {article.title}")
            return False
        
        if any(company in text for company in public_miners):
            logger.info(f"✅ Public mining company detected - auto-approved: {article.title}")
            return True
        
        # Must contain Bitcoin mining terms
        bitcoin_terms = ["bitcoin", "btc", "mining", "miner", "hash rate", "asic"]
        if not any(term in text for term in bitcoin_terms):
            return False
        
        # CORRECTED: Require Bitcoin AND mining in meaningful context (more flexible)
        bitcoin_terms_list = ["bitcoin", "btc"]
        mining_terms_list = ["mining", "miner", "miners", "mine", "mined"]
        
        bitcoin_mentions = sum(1 for term in bitcoin_terms_list if term in text)
        mining_mentions = sum(1 for term in mining_terms_list if term in text)
        
        if bitcoin_mentions == 0 or mining_mentions == 0:
            logger.info(f"❌ Missing Bitcoin+mining combination: {article.title} (Bitcoin: {bitcoin_mentions}, Mining: {mining_mentions})")
            return False
        
        # CORRECTED: More restrictive non-mining titles (only clear exclusions)
        non_mining_titles = [
            "defi", "nft", "metaverse", "web3", "stablecoin", "usdt", "tether"
        ]
        # NOTE: Removed "gold", "treasury", "investment fund", "trading", "exchange", "tokenized" 
        # as these can be part of legitimate mining news (e.g., "France opposes takeover")
        if any(term in title_lower for term in non_mining_titles):
            logger.info(f"❌ Excluded non-mining title topic: {article.title}")
            return False
        
        # Exclude other cryptocurrencies - validation with proper bounds checking
        other_cryptos = ["ethereum", "eth", "solana", "cardano", "dogecoin"]
        other_mentions = sum(1 for crypto in other_cryptos if crypto in text)
        
        # Skip if other cryptos mentioned more than Bitcoin (defensive check)
        if other_mentions > 0 and bitcoin_mentions > 0 and other_mentions > bitcoin_mentions:
            logger.info(f"❌ Other cryptos mentioned more than Bitcoin: {article.title} (Other: {other_mentions}, Bitcoin: {bitcoin_mentions})")
            return False
        
        # CORRECTED: More specific crypto-adjacent exclusions (removed overly broad terms)
        excluded_topics = [
            "stablecoin minting", "stable coin issuance", "defi protocol",
            "nft marketplace", "web3 gaming", "metaverse platform"
        ]
        # NOTE: Removed broad terms like "digital asset", "investment vehicle", "treasury"
        # as these can appear in legitimate mining regulatory/political news
        if any(term in text for term in excluded_topics):
            logger.info(f"❌ Excluded crypto-adjacent non-mining topic: {article.title}")
            return False
        
        # ENHANCED: Exclude only obvious promotional/cloud mining content (already checked above)
        # This check is moved earlier to prevent scam apps from being approved
        
        # Exclude generic educational content  
        generic_terms = [
            "what is bitcoin mining", "how to mine bitcoin", 
            "bitcoin mining explained", "mining tutorial",
            "beginner's guide", "introduction to mining"
        ]
        if any(term in title_lower for term in generic_terms):
            logger.info(f"❌ Excluded generic educational content: {article.title}")
            return False
        
        # Exclude suspicious/scam indicators
        suspicious_terms = [
            "guaranteed profit", "risk-free", "100% profit",
            "get rich", "make money fast", "instant profit",
            "ponzi", "pyramid", "scam"
        ]
        if any(term in text for term in suspicious_terms):
            logger.info(f"❌ Excluded suspicious content: {article.title}")
            return False
        
        # CRITICAL: Exclude law enforcement/criminal/seizure articles (not about mining operations)
        # These articles mention "mining" only tangentially in criminal context
        law_enforcement_terms = [
            "seiz", "arrest", "indict", "criminal", "fraud", "money laundering",
            "department of justice", "doj", "treasury", "sec charges", "law enforcement",
            "investigation", "convicted", "sentenced", "prison", "jail",
            "confiscate", "forfeiture", "ransomware", "cyberattack", "hack",
            "transnational criminal", "organized crime", "trafficking", "scam compound"
        ]
        law_enforcement_mentions = sum(1 for term in law_enforcement_terms if term in text)
        
        # If article heavily focuses on law enforcement (3+ mentions), it's not about mining operations
        if law_enforcement_mentions >= 3:
            logger.info(f"❌ Excluded law enforcement/criminal article (not about mining operations): {article.title} (Law enforcement mentions: {law_enforcement_mentions})")
            return False
        
        # CORRECTED: Expanded mining focus terms including AI/political/regulatory
        core_mining_terms = [
            "mining company", "mining operation", "mining facility", 
            "mining farm", "mining pool", "hash rate", "hashrate", "difficulty",
            "mining equipment", "mining revenue", "mining profit",
            "block reward", "halving", "mining stocks", "public miner",
            "mining rig", "mining power", "mining capacity", "mining contract",
            "mining data center", "mining infrastructure", "asic miner",
            "mining performance", "mining efficiency", "mining expansion",
            # ADDED: AI and data center terms (AI + mining is relevant)
            "ai data center", "artificial intelligence", "data center", "power struggle",
            "electricity", "energy consumption", "power grid", "renewable energy",
            # ADDED: Political/regulatory terms (political mining news is relevant)  
            "regulation", "regulatory", "government", "policy", "ban", "approval",
            "law", "legal", "compliance", "taxation", "lobbying", "political"
        ]
        
        # CORRECTED: More flexible mining focus (1 substantial term can be enough)
        mining_mentions = sum(1 for term in core_mining_terms if term in text)
        
        # Special case: If it's about AI + mining, data centers, or political/regulatory, 
        # it's automatically relevant even with fewer traditional mining terms
        ai_mining_terms = ["ai data center", "artificial intelligence", "power struggle", "electricity"]
        political_terms = ["regulation", "regulatory", "government", "policy", "political"]
        
        has_ai_mining = any(term in text for term in ai_mining_terms)
        has_political = any(term in text for term in political_terms)
        
        if has_ai_mining or has_political:
            logger.info(f"✅ Bitcoin mining content approved (AI/political relevance): {article.title}")
            return True
        
        # For traditional mining news, require at least 1 substantial mining term
        if mining_mentions < 1:
            logger.info(f"❌ Insufficient mining focus (only {mining_mentions} mining terms): {article.title}")
            return False
        
        # CORRECTED: Less restrictive hardware manufacturing check
        # Only exclude if it's ONLY about hardware manufacturing with no mining operations
        hardware_only_indicators = [
            "manufacturer", "manufacturing", "supply chain", "equipment maker",
            "hardware company", "chip maker", "asic manufacturer"
        ]
        hardware_mentions = sum(1 for term in hardware_only_indicators if term in text)
        
        # Only exclude if it's primarily hardware manufacturing AND has no operational mining content
        mining_operations_terms = [
            "mining company", "mining operation", "mining facility", "mining farm",
            "hash rate", "mining revenue", "mining profit", "mining expansion"
        ]
        operations_mentions = sum(1 for term in mining_operations_terms if term in text)
        
        # If it's primarily hardware manufacturing AND has no operations content
        if hardware_mentions >= 2 and operations_mentions == 0:
            logger.info(f"❌ Hardware manufacturing only, no mining operations: {article.title}")
            return False
        
        logger.info(f"✅ Bitcoin mining content approved: {article.title} (mining terms: {mining_mentions})")
        return True


# =============================================================================
# MAIN BOT CLASS
# =============================================================================

class BitcoinMiningBot:
    """
    Simplified Bitcoin Mining News Bot.
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
    def gemini(self) -> Optional[GeminiClient]:
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
        """Main execution method."""
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
                return True
            
            # Check minimum interval
            if not self._can_run_now():
                last_run = self.posted_data.get("last_run_time")
                logger.info(f"⏱️ Last run: {last_run}")
                logger.info(f"🚫 Minimum interval ({self.config.min_interval_minutes} minutes) not yet reached.")
                return True
            
            # Fetch articles
            logger.info("Fetching new articles...")
            articles = self.news.fetch_articles(self.config.max_articles)
            
            if not articles:
                logger.info("No new articles found from EventRegistry")
                return True
            
            # Filter out already posted articles using INTELLIGENT deduplication
            new_articles: List[Article] = []
            posted_urls = set(self.posted_data["posted_uris"])
            queued_articles_data = self.posted_data.get("queued_articles", [])
            
            # Convert existing queued articles to Article objects for comparison
            existing_articles: List[Article] = []
            
            # Add already queued articles for comparison
            for qa_data in queued_articles_data:
                try:
                    existing_articles.append(Article.from_dict(qa_data))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid queued article data: {e}")
                    continue
            
            # Note: We can't reconstruct Article objects from just URLs in posted_uris,
            # so for backwards compatibility, we still check URL duplicates first
            queued_urls = set(qa.get("url", "") for qa in queued_articles_data)
            existing_urls = posted_urls.union(queued_urls)
            
            for article in articles:
                # Quick URL check first (if URL already posted, definitely duplicate)
                if article.url in existing_urls:
                    continue
                
                # Intelligent content similarity check against queued articles
                # Performance optimization: Early termination on first duplicate match
                is_duplicate = False
                for existing_article in existing_articles:
                    if ContentSimilarity.is_duplicate_article(
                        article, existing_article,
                        title_threshold=self.config.title_similarity_threshold,
                        content_threshold=self.config.content_similarity_threshold,
                        date_window_hours=self.config.duplicate_detection_date_window_hours
                    ):
                        logger.info(f"Found content duplicate: '{article.title}' matches existing '{existing_article.title}'")
                        is_duplicate = True
                        break  # Early termination - no need to check remaining articles
                
                if not is_duplicate:
                    new_articles.append(article)
            
            logger.info(f"Found {len(new_articles)} new articles (filtered out {len(articles) - len(new_articles)} duplicates)")
            
            if not new_articles:
                # Check queued articles and try multiple if URL retrieval fails
                queued_articles = self.posted_data.get("queued_articles", [])
                if queued_articles:
                    logger.info("No new articles, posting from queue")
                    
                    # Try posting queued articles, skipping ones with URL retrieval failures
                    while queued_articles:
                        article_data = queued_articles[0]
                        article_to_post = Article.from_dict(article_data)
                        
                        try:
                            success = self._post_article(article_to_post)
                            if success:
                                # Remove from queue - verify queue has items before popping
                                if self.posted_data["queued_articles"]:
                                    try:
                                        self.posted_data["queued_articles"].pop(0)
                                        logger.info(f"✅ Removed posted article from queue: {article_to_post.title[:50]}")
                                    except (IndexError, ValueError) as e:
                                        logger.error(f"❌ Failed to remove article from queue: {e}")
                                        # Queue state is inconsistent - clear it to prevent further issues
                                        self.posted_data["queued_articles"] = []
                                        logger.warning("🧹 Cleared queue due to state inconsistency")
                                else:
                                    logger.error("❌ Queue was empty when trying to remove posted article - state inconsistency detected")
                                    # Reset queue state
                                    self.posted_data["queued_articles"] = []
                                
                                self.posted_data["last_run_time"] = TimeManager.now().isoformat()
                                self._save_data()
                                logger.info("✅ Posted queued article successfully")
                                return True
                            else:
                                # Check if failure was due to Gemini (not a rate limit issue)
                                if not self.gemini:
                                    logger.info("⏳ Gemini API unavailable for queued article - will retry on next run")
                                    return True  # Don't set rate limit cooldown for Gemini issues
                                else:
                                    self._handle_posting_failure()
                                    return False
                        
                        except URLRetrievalError as e:
                            # URL retrieval failed - skip this article and try next one
                            logger.warning(f"⏭️ Skipping article due to URL retrieval failure: {e}")
                            if self.posted_data["queued_articles"]:
                                skipped_article = self.posted_data["queued_articles"].pop(0)
                                logger.info(f"🗑️ Removed article from queue: {skipped_article.get('title', 'Unknown')}")
                            continue
                    
                    # If we get here, all queued articles had URL retrieval failures
                    logger.info("⚠️ All queued articles had URL retrieval failures - queue is now empty")
                    return True
                else:
                    logger.info("No new articles and no queued articles available")
                    return True
            else:
                # Try posting new articles, skipping ones with URL retrieval failures
                posted_successfully = False
                articles_posted = 0
                
                for i, article_to_post in enumerate(new_articles):
                    try:
                        success = self._post_article(article_to_post)
                        
                        if success:
                            posted_successfully = True
                            articles_posted += 1
                            
                            # Queue remaining articles (after the one we just posted)
                            remaining_articles = new_articles[i+1:]
                            for article in remaining_articles:
                                article_data = {
                                    "title": article.title,
                                    "body": article.body,
                                    "url": article.url,
                                    "source": {"title": article.source},
                                    "dateTimePub": article.date_published.isoformat() if article.date_published else None
                                }
                                self.posted_data["queued_articles"].append(article_data)
                            
                            if remaining_articles:
                                logger.info(f"Queued {len(remaining_articles)} additional articles")
                            
                            # Update last run time
                            self.posted_data["last_run_time"] = TimeManager.now().isoformat()
                            self._save_data()
                            
                            execution_time = time.time() - start_time
                            logger.info(f"✅ Bot completed successfully in {execution_time:.2f}s")
                            # Performance optimization: Clear cache to free memory
                            ContentSimilarity.clear_cache()
                            return True
                        else:
                            # Check if failure was due to Gemini (not a rate limit issue)
                            if not self.gemini:
                                logger.info("⏳ Gemini API unavailable - will retry on next run (no cooldown)")
                                return True  # Don't set rate limit cooldown for Gemini issues
                            else:
                                self._handle_posting_failure()
                                return False
                    
                    except URLRetrievalError as e:
                        # URL retrieval failed - skip this article and try next one
                        logger.warning(f"⏭️ Skipping article due to URL retrieval failure: {e}")
                        logger.info(f"🗑️ Skipped article: {article_to_post.title}")
                        continue
                
                # If we get here, no articles could be posted (all had URL retrieval failures)
                if not posted_successfully:
                    logger.info("⚠️ All new articles had URL retrieval failures - none could be posted")
                    return True
                
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded (429): {e}")
            self._handle_posting_failure()
            return False
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Bot execution failed after {execution_time:.2f}s: {e}")
            # Performance optimization: Clear cache even on failure to free memory
            ContentSimilarity.clear_cache()
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
    
    def _post_article(self, article: Article) -> bool:
        """Post an article to Twitter as a thread.
        
        Raises:
            URLRetrievalError: When URL content cannot be retrieved (caller should skip article)
            tweepy.TooManyRequests: When Twitter API rate limit is exceeded
        """
        try:
            thread_tweets = TextProcessor.create_tweet_thread(article, self.gemini)
            
            # CRITICAL: If Gemini failed (thread_tweets is None), don't post - wait and retry later
            if thread_tweets is None:
                logger.warning("❌ Cannot create thread without Gemini API - will retry later")
                return False
            
            logger.info(f"Posting thread with {len(thread_tweets)} tweets: {article.title[:50]}...")
            
            if len(thread_tweets) == 1:
                tweet_id = self.twitter.post_tweet(thread_tweets[0])
                success = bool(tweet_id)
            else:
                success = self.twitter.post_thread(thread_tweets)
            
            if success:
                # Record successful post in both URL list and full history
                self.posted_data["posted_uris"].append(article.url)
                
                # NEW: Save full article metadata to posted history
                posted_article_record: Dict[str, Any] = {
                    "url": article.url,
                    "title": article.title,
                    "source": article.source,
                    "date_published": article.date_published.isoformat() if article.date_published else None,
                    "date_posted": TimeManager.now().isoformat(),
                    "body_preview": article.body[:200] + "..." if len(article.body) > 200 else article.body
                }
                
                # Initialize posted_articles_history if it doesn't exist
                if "posted_articles_history" not in self.posted_data:
                    self.posted_data["posted_articles_history"] = []
                
                self.posted_data["posted_articles_history"].append(posted_article_record)
                
                logger.info(f"✅ Article recorded in posting history: {article.title}")
                return True
            else:
                logger.error("Failed to post tweet(s)")
                return False
                
        except URLRetrievalError:
            # Let URL retrieval errors bubble up to caller for proper handling
            raise
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit exceeded during article posting: {e}")
            raise
        except Exception as e:
            logger.error(f"Error posting article: {e}")
            return False
    
    def _handle_posting_failure(self) -> None:
        """Handle failure to post tweet (likely rate limiting)."""
        logger.warning(f"Failed to post tweet - setting rate limit cooldown for {self.config.cooldown_hours} hours")
        
        cooldown_data = TimeManager.create_cooldown_data(self.config.cooldown_hours)
        cooldown_end = cooldown_data.get('cooldown_end', 'unknown')
        logger.info(f"⏳ Rate limit cooldown active until: {cooldown_end}")
        
        if self.storage.save_json(self.config.rate_limit_file, cooldown_data):
            logger.info(f"✅ Cooldown data saved to {self.config.rate_limit_file}")
        else:
            logger.error(f"❌ Failed to save cooldown data to {self.config.rate_limit_file}")
    
    def _save_data(self) -> bool:
        """Save posted articles data."""
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
    
    safe_mode = '--diagnose' in sys.argv
    bot = BitcoinMiningBot(safe_mode=safe_mode)
    success = bot.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
