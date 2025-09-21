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
        """Save the list of posted article URIs and queued articles (backward compatibility)"""
        FileManager.save_posted_articles(self.posted_articles)
    
    def _set_rate_limit_cooldown(self) -> None:
        """Set a simple cooldown period due to rate limiting (backward compatibility)"""
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
            # Save updated queue after successful posting
            FileManager.save_posted_articles(self.posted_articles)
        else:
            # Return article to queue if posting failed
            queued_articles.insert(0, article_to_post)
            logger.info("Returned failed article to queue")
            
        # Save updated queue state
        FileManager.save_posted_articles(self.posted_articles)
        return success

    def _post_article(self, article: Dict[str, Any]) -> bool:
        """Post a single article and update posted articles list"""
        if not self.tweet_poster:
            logger.error("Tweet poster not initialized")
            return False
        
        # Create a copy of the article to potentially enhance with Gemini-generated content
        enhanced_article = article.copy()
        
        # Generate enhanced tweet headline with Gemini AI if available and not skipped
        if not self.skip_gemini_analysis:
            gemini_client = self.api_manager.get_gemini_client()
            if gemini_client:
                try:
                    tweet_headline = gemini_client.generate_tweet_headline(article)
                    enhanced_article['gemini_headline'] = tweet_headline
                    logger.info(f"Using Gemini-generated tweet headline ({len(tweet_headline)} chars): {tweet_headline[:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to generate tweet headline with Gemini: {e}")
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

            logger.info("Starting Bitcoin Mining News Bot")

            # Check minimum interval since last run
            if not self._is_minimum_interval_respected():
                logger.info("Bot execution skipped: minimum 90-minute interval not yet reached")
                return

            # Check if we're in rate limit cooldown
            if self._is_rate_limit_cooldown_active():
                logger.info("Bot execution skipped: rate limit cooldown still active")
                return

            # Fetch articles
            articles = self.fetch_bitcoin_mining_articles()

            if not articles:
                logger.info("No new articles from EventRegistry - checking queue for pending articles")
                # Even if no new articles, check queue for pending articles
                self._process_queued_article()
                return

            logger.info(f"Found {len(articles)} total articles from EventRegistry")

            # Filter out already posted articles and extract new ones
            new_articles = []
            queued_uris = {article.get("uri") for article in self.posted_articles.get("queued_articles", [])}
            for article in articles:
                uri = article.get("uri")
                if not uri:
                    logger.warning("Skipping article with missing URI")
                    continue

                if uri not in self.posted_articles["posted_uris"] and uri not in queued_uris:
                    new_articles.append(article)
                else:
                    title = article.get("title", "Unknown title")[:50] + "..."
                    if uri in self.posted_articles["posted_uris"]:
                        logger.info(f"Skipping already posted article: {title}")
                    else:
                        logger.info(f"Skipping already queued article: {title}")

            if not new_articles:
                # Check if we have queued articles to post
                self._process_queued_article()
                return

            # Sort by publication date (newest first) 
            new_articles.sort(key=lambda x: x.get("dateTime", ""), reverse=True)

            # Post the most recent article and queue the rest
            articles_to_queue = new_articles[1:] if len(new_articles) > 1 else []
            article_to_post = new_articles[0]

            if articles_to_queue:
                logger.info(f"Found {len(new_articles)} new articles. Posting most recent, queueing {len(articles_to_queue)} older articles for later.")
                for i, article in enumerate(articles_to_queue, 1):
                    title = article.get("title", "Unknown title")[:50] + "..."
                    logger.info(f"  Queueing #{i}: {title}")
                
                # Add to queue
                self.posted_articles.setdefault("queued_articles", []).extend(articles_to_queue)
            else:
                logger.info(f"Found {len(new_articles)} new article to post.")

            # Post the most recent article
            success = self._post_article(article_to_post)
            
            # Save posted articles list
            FileManager.save_posted_articles(self.posted_articles)

            if success:
                queued_count = len(self.posted_articles.get("queued_articles", []))
                total_in_queue_msg = f", {queued_count} total in queue" if queued_count > 0 else ""
                if articles_to_queue:
                    logger.info(f"Successfully posted 1 article. Queued {len(articles_to_queue)} newer articles for later ({len(new_articles)} new articles available, {len(articles) - len(new_articles)} already posted{total_in_queue_msg})")
                else:
                    logger.info(f"Successfully posted 1 article ({len(new_articles)} new articles available, {len(articles) - len(new_articles)} already posted{total_in_queue_msg})")
            else:
                # Set rate limit cooldown since posting failed
                cooldown_data = TimeUtils.create_rate_limit_cooldown()
                FileManager.save_rate_limit_cooldown(cooldown_data)

        except Exception as e:
            if "Missing environment variable" in str(e):
                logger.error("==="*20)
                logger.error("CONFIGURATION ERROR: Missing required environment variables")
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
                logger.error("="*60)
                sys.exit(1)
            else:
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
    else:
        try:
            bot = BitcoinMiningNewsBot()
            bot.run()
        except ValueError as e:
            # If API initialization fails, check if we can process queued articles
            if "environment variables" in str(e).lower():
                logger.warning("API keys missing, checking for queued articles to process...")
                try:
                    from utils import FileManager
                    posted_articles = FileManager.load_posted_articles()
                    queued_count = len(posted_articles.get("queued_articles", []))
                    _show_api_key_error(queued_count)
                except Exception as load_error:
                    logger.error(f"Failed to check queued articles: {load_error}")
            else:
                logger.error(f"Bot initialization failed: {e}")
            raise


if __name__ == "__main__":
    main()