"""
Bitcoin Mining News Twitter Bot
-------------------------------
This bot fetches the latest Bitcoin mining news from EventRegistry (NewsAPI.ai)
and posts them to Twitter/X as single tweets with catchy headlines.
"""

import logging
import sys
from typing import Dict, List, Optional, Any

# Configure logging before any modules attempt to use the shared logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('bitcoin_mining_bot')

# Import new modular components
from config import BotConstants
from utils import FileManager, TimeUtils
from api_clients import APIClientManager
from tweet_poster import TweetPoster


class BitcoinMiningNewsBot:
    def __init__(self, safe_mode: bool = False, skip_gemini_analysis: bool = False):
        """
        Initialize the bot
        
        Args:
            safe_mode (bool): If True, skip API initialization for diagnostics
            skip_gemini_analysis (bool): If True, skip Gemini AI headline generation during posting
        """
        self.safe_mode = safe_mode
        self.skip_gemini_analysis = skip_gemini_analysis
        
        # File compatibility attributes expected by the legacy tests
        self.rate_limit_cooldown_file = BotConstants.RATE_LIMIT_COOLDOWN_FILE

        # Initialize API clients
        self.api_manager = APIClientManager(safe_mode=safe_mode)

        # Load history of posted articles
        self.posted_articles = FileManager.load_posted_articles()
        if not safe_mode:
            logger.info(f"Loaded {len(self.posted_articles['posted_uris'])} previously posted articles")
        
        # Initialize tweet poster if not in safe mode
        self.tweet_poster: Optional[TweetPoster] = None
        self.image_selector = None

        if not safe_mode:
            twitter_client = self.api_manager.get_twitter_client()
            self.tweet_poster = TweetPoster(twitter_client)
            # Expose the image selector directly for backward compatibility
            if hasattr(self.tweet_poster, "image_selector"):
                self.image_selector = self.tweet_poster.image_selector

    # Backward compatibility methods for tests
    def fetch_bitcoin_mining_articles(self, max_articles: int = BotConstants.DEFAULT_MAX_ARTICLES) -> List[Dict[str, Any]]:
        """Fetch latest articles about Bitcoin mining (backward compatibility)"""
        if self.safe_mode:
            return []
        eventregistry_client = self.api_manager.get_eventregistry_client()
        return eventregistry_client.fetch_bitcoin_mining_articles(max_articles)
    
    def create_tweet_text(self, article: Dict[str, Any]) -> str:
        """Create catchy tweet text for the article (backward compatibility)"""
        from utils import TextUtils
        return TextUtils.create_tweet_text(article)
    
    def post_to_twitter(self, article: Dict[str, Any]) -> Optional[str]:
        """Post article as a single tweet on Twitter (backward compatibility)"""
        if not self.tweet_poster:
            return None
        return self.tweet_poster.post_to_twitter(article)
    
    def _save_posted_articles(self) -> None:
        """Save the list of posted article URIs and queued articles (backward compatibility)
        
        Note: This method exists solely for backward compatibility with existing tests.
        The main bot logic uses FileManager.save_posted_articles() directly.
        This wrapper is preserved to avoid breaking existing test infrastructure.
        """
        FileManager.save_posted_articles(self.posted_articles)
    
    def _set_rate_limit_cooldown(self) -> None:
        """Set a simple cooldown period due to rate limiting (backward compatibility)
        
        Note: This method exists solely for backward compatibility with existing tests.
        The main bot logic uses TimeUtils.create_rate_limit_cooldown() and 
        FileManager.save_rate_limit_cooldown() directly. This wrapper is preserved 
        to avoid breaking existing test infrastructure.
        """
        cooldown_data = TimeUtils.create_rate_limit_cooldown()
        FileManager.save_rate_limit_cooldown(cooldown_data)

    def _is_rate_limit_cooldown_active(self) -> bool:
        """Check if we're still in rate limit cooldown period (backward compatibility)"""
        cooldown_data = FileManager.load_rate_limit_cooldown()
        return TimeUtils.is_rate_limit_cooldown_active(cooldown_data)

    def _is_minimum_interval_respected(self) -> bool:
        """Compatibility wrapper around the minimum interval check"""
        last_run_time = self.posted_articles.get("last_run_time")
        return TimeUtils.is_minimum_interval_respected(last_run_time)

    def _post_with_retry(self, article: Dict[str, Any], max_retries: int = BotConstants.MAX_RETRIES) -> Optional[str]:
        """Expose TweetPoster's retry helper for backwards compatibility"""
        if not self.tweet_poster:
            logger.error("Tweet poster not initialized")
            return None
        return self.tweet_poster._post_with_retry(article, max_retries=max_retries)
    
    @property
    def twitter_client(self):
        """Get Twitter client for backward compatibility with tests"""
        if self.tweet_poster and hasattr(self.tweet_poster, 'twitter_client'):
            return self.tweet_poster.twitter_client.client
        return None

    def _is_queue_stale(self, max_age_hours: int = 48) -> bool:
        """Check if queued articles are too old to be worth posting"""
        from datetime import datetime, timedelta
        
        queued_articles = self.posted_articles.get("queued_articles", [])
        if not queued_articles:
            return False
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        stale_count = 0
        articles_with_dates = 0
        
        for article in queued_articles:
            # Check publication date
            date_time_str = article.get("dateTimePub") or article.get("dateTime", "")
            if date_time_str:
                try:
                    # Parse ISO format date
                    article_date = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
                    articles_with_dates += 1
                    if article_date.replace(tzinfo=None) < cutoff_time:
                        stale_count += 1
                except ValueError:
                    # If we can't parse the date, don't count it as stale
                    pass
        
        # Only consider staleness if we have date information for most articles
        if articles_with_dates == 0:
            # No date information available, don't consider stale
            return False
        
        # If more than half the articles with dates are stale, consider the whole queue stale
        staleness_ratio = stale_count / articles_with_dates
        is_stale = staleness_ratio > 0.5
        
        if is_stale:
            logger.info(f"Queue is stale: {stale_count}/{articles_with_dates} dated articles older than {max_age_hours}h")
        
        return is_stale
    
    def _clean_stale_articles(self, max_age_hours: int = 48):
        """Remove stale articles from the queue"""
        from datetime import datetime, timedelta
        
        queued_articles = self.posted_articles.get("queued_articles", [])
        if not queued_articles:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        original_count = len(queued_articles)
        
        # Filter out stale articles
        fresh_articles = []
        for article in queued_articles:
            date_time_str = article.get("dateTimePub") or article.get("dateTime", "")
            if date_time_str:
                try:
                    article_date = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
                    if article_date.replace(tzinfo=None) >= cutoff_time:
                        fresh_articles.append(article)
                    # If the article is stale, don't add it (remove it)
                except ValueError:
                    # If we can't parse the date, keep the article (assume fresh)
                    fresh_articles.append(article)
            else:
                # If no date info, keep the article (we don't know how old it is)
                fresh_articles.append(article)
        
        self.posted_articles["queued_articles"] = fresh_articles
        cleaned_count = original_count - len(fresh_articles)
        
        if cleaned_count > 0:
            logger.info(f"Cleaned {cleaned_count} stale articles from queue (older than {max_age_hours}h)")
            # Don't update last_run_time for cleaning operations
            FileManager.save_posted_articles(self.posted_articles)

    def _process_queued_article(self) -> bool:
        """Process the next queued article (FIFO) if available"""
        queued_articles = self.posted_articles.get("queued_articles", [])
        if not queued_articles:
            logger.info("No queued articles to process")
            return False
            
        logger.info(f"Processing oldest of {len(queued_articles)} queued articles...")
        # Take the oldest queued article (FIFO)
        article_to_post = queued_articles.pop(0)
        
        # Try to post it
        success = self._post_article(article_to_post)
        if success:
            logger.info("Successfully posted 1 queued article")
            # Save updated queue after successful posting and update last_run_time
            FileManager.save_posted_articles(self.posted_articles, update_last_run_time=True)
        else:
            # Return article to queue if posting failed
            queued_articles.insert(0, article_to_post)
            logger.info("Returned failed article to queue")
            
        # Save updated queue state (without updating last_run_time for failures)
        if not success:
            FileManager.save_posted_articles(self.posted_articles)
        return success

    def _post_article(self, article: Dict[str, Any]) -> bool:
        """Post a single article and update posted articles list"""
        if not self.tweet_poster:
            logger.error("Tweet poster not initialized")
            return False
        
        # Create a copy of the article to potentially enhance with Gemini-generated content
        enhanced_article = article.copy()
        
        # Generate enhanced tweet content with Gemini AI if available and not skipped
        if not self.skip_gemini_analysis:
            gemini_client = self.api_manager.get_gemini_client()
            if gemini_client:
                try:
                    # Generate headline
                    tweet_headline = gemini_client.generate_tweet_headline(article)
                    enhanced_article['gemini_headline'] = tweet_headline
                    logger.info(f"Generated Gemini headline ({len(tweet_headline)} chars): {tweet_headline[:50]}...")
                    
                    # Generate 3-point summary
                    tweet_summary = gemini_client.generate_tweet_summary(article)
                    enhanced_article['gemini_summary'] = tweet_summary
                    logger.info(f"Generated Gemini summary ({len(tweet_summary)} chars): {tweet_summary[:50]}...")
                    
                    # Combine headline and summary for final tweet content
                    combined_content = f"{tweet_headline}\n\n{tweet_summary}"
                    if len(combined_content) <= 280:
                        enhanced_article['gemini_headline'] = combined_content
                        logger.info(f"Using combined Gemini content ({len(combined_content)} chars)")
                    else:
                        # If combined content is too long, use headline only
                        logger.warning(f"Combined content too long ({len(combined_content)} chars), using headline only")
                        
                except Exception as e:
                    logger.warning(f"Failed to generate tweet content with Gemini: {e}")
                    logger.info("Falling back to original article title for tweet")
        
        tweet_id = self.tweet_poster.post_to_twitter(enhanced_article)
        
        if tweet_id:
            # Add to posted articles
            uri = article.get("uri")
            if uri:
                self.posted_articles["posted_uris"].append(uri)
            
            title = enhanced_article.get("gemini_headline", article.get("title", "Unknown title"))[:50] + "..."
            logger.info(f"Posted article: {title}")
            return True
        
        return False

    def run(self):
        """Main method to run the bot"""
        import time
        start_time = time.time()
        
        try:
            if self.safe_mode:
                logger.error("Cannot run bot in safe mode")
                return

            # Initialize runtime logs
            try:
                from utils import RuntimeLogger
                RuntimeLogger.initialize_runtime_logs()
            except ImportError:
                pass  # Runtime logging not available

            logger.info("🤖 Starting Bitcoin Mining News Bot")
            logger.info(f"📊 Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Check minimum interval since last run
            if not self._is_minimum_interval_respected():
                logger.info("⏰ Bot execution skipped: minimum 90-minute interval not yet reached")
                logger.info(f"⏱️  Execution time: {time.time() - start_time:.2f} seconds")
                logger.info("✅ Status: SUCCESS (Interval Protection Active)")
                return

            # Check if we're in rate limit cooldown
            if self._is_rate_limit_cooldown_active():
                logger.info("🛑 Bot execution skipped: rate limit cooldown still active")
                logger.info(f"⏱️  Execution time: {time.time() - start_time:.2f} seconds")
                logger.info("✅ Status: SUCCESS (Rate Limit Cooldown Active)")
                return

            # Clean any stale articles from the queue before processing
            self._clean_stale_articles()

            # Fetch articles
            logger.info("🔍 Fetching articles from EventRegistry...")
            fetch_start = time.time()
            articles = self.fetch_bitcoin_mining_articles()
            fetch_time = time.time() - fetch_start
            logger.info(f"📊 Article fetch completed in {fetch_time:.2f} seconds")

            if not articles:
                logger.info("📭 No new articles from EventRegistry - checking queue for pending articles")
                # Even if no new articles, check queue for pending articles
                self._process_queued_article()
                execution_time = time.time() - start_time
                logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
                logger.info("✅ Status: SUCCESS (Processed Queue)")
                return

            logger.info(f"📄 Found {len(articles)} total articles from EventRegistry")

            # Filter out already posted articles and extract new ones
            new_articles = []
            queued_uris = {article.get("uri") for article in self.posted_articles.get("queued_articles", [])}
            for article in articles:
                uri = article.get("uri")
                if not uri:
                    logger.warning("⚠️  Skipping article with missing URI")
                    continue

                if uri not in self.posted_articles["posted_uris"] and uri not in queued_uris:
                    new_articles.append(article)
                else:
                    title = article.get("title", "Unknown title")[:50] + "..."
                    if uri in self.posted_articles["posted_uris"]:
                        logger.info(f"🔄 Skipping already posted article: {title}")
                    else:
                        logger.info(f"📋 Skipping already queued article: {title}")

            # Prioritize fresh content over stale queued articles
            if not new_articles:
                # No new articles available, check if queue has fresh content
                if self._is_queue_stale():
                    logger.info("📭 No new articles and queue is stale - waiting for fresh content")
                    execution_time = time.time() - start_time
                    logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
                    logger.info("✅ Status: SUCCESS (Waiting for Fresh Content)")
                    return
                else:
                    # Queue has fresh content, process it
                    self._process_queued_article()
                    execution_time = time.time() - start_time
                    logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
                    logger.info("✅ Status: SUCCESS (Processed Queued Article)")
                    return
            else:
                # We have new articles - always prioritize these over queued content
                if self.posted_articles.get("queued_articles"):
                    queue_count = len(self.posted_articles["queued_articles"])
                    logger.info(f"🆕 Found {len(new_articles)} fresh articles - prioritizing over {queue_count} queued articles")

            # Sort by publication date (newest first) 
            new_articles.sort(key=lambda x: x.get("dateTime", ""), reverse=True)

            # Post the most recent article and queue the rest
            articles_to_queue = new_articles[1:] if len(new_articles) > 1 else []
            article_to_post = new_articles[0]

            if articles_to_queue:
                logger.info(f"📝 Found {len(new_articles)} new articles. Posting most recent, queueing {len(articles_to_queue)} older articles for later.")
                for i, article in enumerate(articles_to_queue, 1):
                    title = article.get("title", "Unknown title")[:50] + "..."
                    logger.info(f"  📋 Queueing #{i}: {title}")
                
                # Add to queue
                self.posted_articles.setdefault("queued_articles", []).extend(articles_to_queue)
            else:
                logger.info(f"📝 Found {len(new_articles)} new article to post.")

            # Post the most recent article
            posting_start = time.time()
            success = self._post_article(article_to_post)
            posting_time = time.time() - posting_start
            logger.info(f"📊 Tweet posting completed in {posting_time:.2f} seconds")
            
            # Save posted articles list (without updating last_run_time yet)
            FileManager.save_posted_articles(self.posted_articles)

            execution_time = time.time() - start_time
            if success:
                queued_count = len(self.posted_articles.get("queued_articles", []))
                total_in_queue_msg = f", {queued_count} total in queue" if queued_count > 0 else ""
                if articles_to_queue:
                    logger.info(f"🎉 Successfully posted 1 article. Queued {len(articles_to_queue)} newer articles for later ({len(new_articles)} new articles available, {len(articles) - len(new_articles)} already posted{total_in_queue_msg})")
                else:
                    logger.info(f"🎉 Successfully posted 1 article ({len(new_articles)} new articles available, {len(articles) - len(new_articles)} already posted{total_in_queue_msg})")
                
                # Update last_run_time only after successful posting
                FileManager.save_posted_articles(self.posted_articles, update_last_run_time=True)
                logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
                logger.info("✅ Status: SUCCESS (Tweet Posted)")
            else:
                # Set rate limit cooldown since posting failed
                cooldown_data = TimeUtils.create_rate_limit_cooldown()
                FileManager.save_rate_limit_cooldown(cooldown_data)
                logger.info(f"⏱️  Total execution time: {execution_time:.2f} seconds")
                logger.info("⚠️  Status: SUCCESS (Rate Limited - Cooldown Active)")

        except Exception as e:
            execution_time = time.time() - start_time
            if "Missing environment variable" in str(e):
                logger.error("🚨 CONFIGURATION ERROR: Missing required environment variables")
                logger.error("This error occurs when the bot cannot find the required API keys.")
                logger.error("")
                logger.error("To fix this issue:")
                logger.error("1. Go to your GitHub repository settings")
                logger.error("2. Navigate to Settings > Secrets and variables > Actions")
                logger.error("3. Add the following repository secrets:")
                logger.error("   • TWITTER_API_KEY")
                logger.error("   • TWITTER_API_SECRET")
                logger.error("   • TWITTER_ACCESS_TOKEN")
                logger.error("   • TWITTER_ACCESS_TOKEN_SECRET")
                logger.error("   • EVENTREGISTRY_API_KEY")
                logger.error("")
                logger.error("For detailed setup instructions, see the README.md file.")
                logger.error(f"⏱️  Execution time: {execution_time:.2f} seconds")
                logger.error("❌ Status: FAILED (Missing Configuration)")
                raise
            else:
                logger.error(f"🚨 Unexpected error during bot execution: {str(e)}")
                logger.error(f"⏱️  Execution time: {execution_time:.2f} seconds")
                logger.error("❌ Status: FAILED (Unexpected Error)")
                raise


def _show_api_key_error(queued_count: int) -> None:
    """Show detailed error message for missing API keys"""
    logger.error("="*80)
    logger.error("🔍 DIAGNOSIS: GitHub Action 'Success' but No Tweets Posted")
    logger.error("="*80)
    logger.error("")
    logger.error("✅ WHAT WORKED:")
    logger.error("   - Dependencies installed successfully")
    logger.error("   - Bot code executed without errors")
    logger.error("   - Python imports and initialization completed")
    logger.error("   - Error handling worked correctly")
    logger.error("")
    logger.error("❌ WHAT FAILED:")
    logger.error("   - Missing required API credentials")
    logger.error("   - Unable to connect to Twitter API")
    logger.error("   - Unable to connect to EventRegistry API")
    logger.error("   - Cannot post tweets without valid authentication")
    logger.error("")
    if queued_count > 0:
        logger.error(f"📋 ARTICLES WAITING: {queued_count} articles are queued for posting")
        logger.error("   These articles will be posted automatically once API keys are configured.")
        logger.error("")
    logger.error("🔧 SOLUTION: Configure GitHub Repository Secrets")
    logger.error("   1. Go to your repository Settings > Secrets and variables > Actions")
    logger.error("   2. Add these repository secrets:")
    for var in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", 
               "TWITTER_ACCESS_TOKEN_SECRET", "EVENTREGISTRY_API_KEY"]:
        logger.error(f"      - {var}")
    logger.error("")
    logger.error("💡 WHY GITHUB ACTIONS SHOW 'SUCCESS':")
    logger.error("   - The workflow completes all steps without exceptions")
    logger.error("   - Dependencies install successfully")
    logger.error("   - The bot gracefully handles missing credentials")
    logger.error("   - No Python errors or crashes occur")
    logger.error("   - 'Success' means the code ran, not that tweets were posted")
    logger.error("")
    logger.error("📖 For API key setup guides:")
    logger.error("   - Twitter: https://developer.twitter.com/")
    logger.error("   - EventRegistry: https://newsapi.ai/dashboard")
    logger.error("")
    logger.error("🔍 Run diagnostics: python bot.py --diagnose")
    logger.error("="*80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bitcoin Mining News Twitter Bot")
    parser.add_argument("--diagnose", action="store_true", help="Run diagnostics only")
    args = parser.parse_args()
    
    if args.diagnose:
        logger.info("Running diagnostics...")
        bot = BitcoinMiningNewsBot(safe_mode=True)
        # Import and run diagnostics
        from diagnose_bot import main as diagnose_main
        diagnose_main()
        return
    
    try:
        bot = BitcoinMiningNewsBot()
        bot.run()
        logger.info("🎉 Bot execution completed successfully")
    except ValueError as e:
        # If API initialization fails, provide helpful information but don't crash
        if "environment variables" in str(e).lower():
            logger.warning("API keys missing, checking for queued articles to process...")
            try:
                from utils import FileManager
                posted_articles = FileManager.load_posted_articles()
                queued_count = len(posted_articles.get("queued_articles", []))
                _show_api_key_error(queued_count)
                
                # Exit gracefully for GitHub Actions
                logger.info("🔧 GitHub Actions Status: SUCCESS (Configuration Required)")
                logger.info("   The bot detected missing API keys and provided setup instructions.")
                logger.info("   This is expected behavior when API keys are not configured.")
                sys.exit(0)  # Exit with success code to avoid triggering GitHub Actions failures
            except Exception as load_error:
                logger.error(f"Failed to check queued articles: {load_error}")
                sys.exit(1)
        else:
            logger.error(f"🚨 Bot initialization failed: {e}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"🚨 Unexpected error during bot execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()