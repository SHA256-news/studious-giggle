"""
Thread builder service - creates Twitter threads from articles.
"""
import logging
from typing import Optional

from src.domain import Article, Thread, Tweet
from src.adapters.interfaces import AIProvider

logger = logging.getLogger(__name__)


class ThreadBuilder:
    """
    Builds Twitter threads from articles using AI generation.
    Can work with or without AI provider (graceful degradation).
    """
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """
        Initialize thread builder.
        
        Args:
            ai_provider: Optional AI provider for enhanced content generation
        """
        self.ai_provider = ai_provider
    
    def build_thread(self, article: Article) -> Optional[Thread]:
        """
        Build a Twitter thread for the article.
        
        Args:
            article: Article to create thread for
            
        Returns:
            Thread object or None if building fails
        """
        # Try AI-enhanced thread first
        if self.ai_provider and self.ai_provider.is_available():
            thread = self._build_ai_thread(article)
            if thread:
                return thread
            logger.warning("AI thread generation failed, falling back to simple thread")
        
        # Fallback to simple thread
        return self._build_simple_thread(article)
    
    def _build_ai_thread(self, article: Article) -> Optional[Thread]:
        """Build AI-enhanced thread with headline and summary."""
        try:
            # Generate headline
            headline = self.ai_provider.generate_headline(article, max_length=80)
            if not headline:
                return None
            
            # Generate summary
            summary = self.ai_provider.generate_summary(article, headline, max_length=180)
            if not summary:
                # Use headline-only thread
                tweets = (
                    Tweet(headline),
                    Tweet(article.url)
                )
                return Thread(tweets=tweets, article=article)
            
            # Check if headline + summary fits in one tweet
            combined = f"{headline}\n\n{summary}"
            if len(combined) <= 280:
                # Single tweet with both + URL tweet
                tweets = (
                    Tweet(combined),
                    Tweet(article.url)
                )
            else:
                # Separate tweets
                tweets = (
                    Tweet(headline),
                    Tweet(summary),
                    Tweet(article.url)
                )
            
            thread = Thread(tweets=tweets, article=article)
            logger.info(f"Built AI thread: {thread.tweet_count} tweets, {thread.total_chars} chars")
            return thread
            
        except Exception as e:
            logger.error(f"Failed to build AI thread: {e}")
            return None
    
    def _build_simple_thread(self, article: Article) -> Thread:
        """Build simple thread with just title and URL."""
        # Clean title
        title = self._clean_title(article.title)
        
        # Create basic thread
        tweets = (
            Tweet(title),
            Tweet(article.url)
        )
        
        thread = Thread(tweets=tweets, article=article)
        logger.info(f"Built simple thread: {thread.tweet_count} tweets")
        return thread
    
    def _clean_title(self, title: str) -> str:
        """Clean article title for tweet."""
        # Remove common problematic patterns
        title = title.replace('\n', ' ')
        title = title.replace('\r', ' ')
        title = title.strip()
        
        # Truncate if too long
        if len(title) > 270:
            title = title[:267] + "..."
        
        return title
