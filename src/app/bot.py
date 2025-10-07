"""
Main bot application - orchestrates the Bitcoin mining news bot pipeline.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from src.domain import Article, PostedArticle
from src.adapters.interfaces import (
    NewsProvider,
    AIProvider,
    SocialMediaPublisher,
    ArticleStorage
)
from src.services import BitcoinMiningFilter, DuplicateDetector, ThreadBuilder

logger = logging.getLogger(__name__)


class BitcoinMiningNewsBot:
    """
    Main bot application with clean dependency injection.
    All dependencies are provided through constructor - no singletons or hard-wired state.
    """
    
    def __init__(
        self,
        news_provider: NewsProvider,
        storage: ArticleStorage,
        publisher: SocialMediaPublisher,
        ai_provider: Optional[AIProvider] = None,
        min_interval_minutes: int = 90
    ):
        """
        Initialize bot with dependencies.
        
        Args:
            news_provider: Provider for fetching news articles
            storage: Storage for article data and bot state
            publisher: Publisher for posting to social media
            ai_provider: Optional AI provider for enhanced content
            min_interval_minutes: Minimum minutes between runs
        """
        self.news_provider = news_provider
        self.storage = storage
        self.publisher = publisher
        self.ai_provider = ai_provider
        self.min_interval_minutes = min_interval_minutes
        
        # Initialize services
        self.mining_filter = BitcoinMiningFilter()
        self.duplicate_detector = DuplicateDetector()
        self.thread_builder = ThreadBuilder(ai_provider=ai_provider)
    
    def run(self, keywords: List[str], max_articles: int = 20) -> bool:
        """
        Run the bot pipeline: fetch, filter, generate, and post.
        
        Args:
            keywords: Keywords to search for
            max_articles: Maximum articles to fetch
            
        Returns:
            True if run was successful, False otherwise
        """
        try:
            # Check if enough time has passed since last run
            if not self._can_run_now():
                logger.info("Minimum interval not yet passed, skipping run")
                return False
            
            # Fetch articles
            logger.info(f"Fetching articles with keywords: {keywords}")
            articles = self.news_provider.fetch_articles(
                keywords=keywords,
                max_results=max_articles,
                since_date=datetime.now() - timedelta(days=1)
            )
            
            if not articles:
                logger.info("No articles fetched")
                return False
            
            logger.info(f"Fetched {len(articles)} articles")
            
            # Filter articles
            relevant_articles = self._filter_articles(articles)
            
            if not relevant_articles:
                logger.info("No relevant articles after filtering")
                return False
            
            logger.info(f"{len(relevant_articles)} relevant articles after filtering")
            
            # Load queue and add new articles
            queue = self.storage.load_queue()
            queue.extend(relevant_articles)
            logger.info(f"Queue has {len(queue)} articles")
            
            # Try to post from queue
            posted = False
            if queue:
                article = queue[0]
                if self._post_article(article):
                    queue.pop(0)
                    posted = True
            
            # Save updated queue
            self.storage.save_queue(queue)
            
            # Update last run time
            self.storage.set_last_run_time(datetime.now())
            
            return posted
            
        except Exception as e:
            logger.error(f"Bot run failed: {e}", exc_info=True)
            return False
    
    def _filter_articles(self, articles: List[Article]) -> List[Article]:
        """
        Filter articles for relevance and duplicates.
        
        Args:
            articles: Articles to filter
            
        Returns:
            Filtered list of relevant, non-duplicate articles
        """
        # Load previously posted articles for duplicate detection
        posted = self.storage.load_posted_articles()
        posted_articles = [p.article for p in posted]
        self.duplicate_detector.add_articles(posted_articles)
        
        filtered: List[Article] = []
        
        for article in articles:
            # Check mining relevance
            if not self.mining_filter.is_relevant(article):
                continue
            
            # Check for duplicates
            if self.duplicate_detector.is_duplicate(article):
                logger.info(f"Skipping duplicate: {article.title}")
                continue
            
            filtered.append(article)
        
        return filtered
    
    def _post_article(self, article: Article) -> bool:
        """
        Post an article to social media.
        
        Args:
            article: Article to post
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            logger.info(f"Posting article: {article.title}")
            
            # Build thread
            thread = self.thread_builder.build_thread(article)
            if not thread:
                logger.error("Failed to build thread")
                return False
            
            # Post thread
            tweet_ids = self.publisher.post_thread(thread)
            if not tweet_ids:
                logger.error("Failed to post thread")
                return False
            
            logger.info(f"Successfully posted thread with {len(tweet_ids)} tweets")
            
            # Save posted article
            posted = PostedArticle(
                article=article,
                thread=thread,
                posted_at=datetime.now(),
                tweet_ids=tuple(tweet_ids)
            )
            
            self.storage.save_posted_article(posted)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to post article: {e}", exc_info=True)
            return False
    
    def _can_run_now(self) -> bool:
        """Check if minimum interval has passed since last run."""
        last_run = self.storage.get_last_run_time()
        if not last_run:
            return True
        
        elapsed = datetime.now() - last_run
        elapsed_minutes = elapsed.total_seconds() / 60
        
        if elapsed_minutes < self.min_interval_minutes:
            logger.info(
                f"Only {elapsed_minutes:.1f} minutes since last run "
                f"(minimum: {self.min_interval_minutes})"
            )
            return False
        
        return True
    
    def diagnose(self) -> dict:
        """
        Run diagnostics and return status information.
        
        Returns:
            Dictionary with diagnostic information
        """
        diagnostics = {
            "news_provider": "available",
            "storage": "available",
            "publisher_authenticated": False,
            "ai_provider": "not available",
            "queue_size": 0,
            "posted_count": 0,
            "last_run": None
        }
        
        try:
            # Check publisher
            diagnostics["publisher_authenticated"] = self.publisher.is_authenticated()
        except Exception as e:
            diagnostics["publisher_authenticated"] = f"error: {e}"
        
        try:
            # Check AI provider
            if self.ai_provider and self.ai_provider.is_available():
                diagnostics["ai_provider"] = "available"
        except Exception as e:
            diagnostics["ai_provider"] = f"error: {e}"
        
        try:
            # Check storage
            queue = self.storage.load_queue()
            diagnostics["queue_size"] = len(queue)
            
            posted = self.storage.load_posted_articles()
            diagnostics["posted_count"] = len(posted)
            
            last_run = self.storage.get_last_run_time()
            if last_run:
                diagnostics["last_run"] = last_run.isoformat()
        except Exception as e:
            diagnostics["storage"] = f"error: {e}"
        
        return diagnostics
