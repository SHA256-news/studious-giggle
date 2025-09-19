"""
Bitcoin Mining News Twitter Bot
-------------------------------
This bot fetches the latest Bitcoin mining news from EventRegistry (NewsAPI.ai)
and posts them to Twitter/X as single tweets with catchy headlines.
"""

import logging
import sys
from typing import List, Dict, Any, Optional

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
    def __init__(self, safe_mode: bool = False):
        """
        Initialize the bot
        
        Args:
            safe_mode (bool): If True, skip API initialization for diagnostics
        """
        self.safe_mode = safe_mode
        
        # Initialize API clients
        self.api_manager = APIClientManager(safe_mode=safe_mode)
        
        # Load history of posted articles
        self.posted_articles = FileManager.load_posted_articles()
        if not safe_mode:
            logger.info(f"Loaded {len(self.posted_articles['posted_uris'])} previously posted articles")
        
        # Initialize tweet poster if not in safe mode
        self.tweet_poster: Optional[TweetPoster] = None
        if not safe_mode:
            twitter_client = self.api_manager.get_twitter_client()
            self.tweet_poster = TweetPoster(twitter_client)

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

    def _post_article(self, article: Dict[str, Any]) -> bool:
        """Post a single article and update posted articles list"""
        if not self.tweet_poster:
            logger.error("Tweet poster not initialized")
            return False
            
        tweet_id = self.tweet_poster.post_to_twitter(article)
        
        if tweet_id:
            # Add to posted articles
            uri = article.get("uri")
            if uri:
                self.posted_articles["posted_uris"].append(uri)
            
            title = article.get("title", "Unknown title")[:50] + "..."
            logger.info(f"Posted article: {title}")
            return True
        
        return False

    def run(self):
        """Main method to run the bot"""
        try:
            if self.safe_mode:
                logger.error("Cannot run bot in safe mode")
                return

            logger.info("Starting Bitcoin Mining News Bot")

            # Check minimum interval since last run
            if not TimeUtils.is_minimum_interval_respected(self.posted_articles.get("last_run_time")):
                return

            # Check if we're in rate limit cooldown
            cooldown_data = FileManager.load_rate_limit_cooldown()
            if TimeUtils.is_rate_limit_cooldown_active(cooldown_data):
                return

            # Fetch articles
            eventregistry_client = self.api_manager.get_eventregistry_client()
            articles = eventregistry_client.fetch_bitcoin_mining_articles()

            if not articles:
                logger.warning("No articles found from EventRegistry")
                return

            logger.info(f"Found {len(articles)} total articles")

            # Filter out already posted articles and extract new ones
            new_articles = []
            for article in articles:
                uri = article.get("uri")
                if not uri:
                    logger.warning("Skipping article with missing URI")
                    continue

                if uri not in self.posted_articles["posted_uris"]:
                    new_articles.append(article)
                else:
                    title = article.get("title", "Unknown title")[:50] + "..."
                    logger.info(f"Skipping already posted article: {title}")

            if not new_articles:
                # Check if we have queued articles to post
                queued_articles = self.posted_articles.get("queued_articles", [])
                if queued_articles:
                    logger.info(f"No new articles found. Processing {len(queued_articles)} queued articles...")
                    # Take the oldest queued article (FIFO)
                    article_to_post = queued_articles.pop(0)
                    # Save updated queue
                    FileManager.save_posted_articles(self.posted_articles)
                    # Try to post it
                    success = self._post_article(article_to_post)
                    if success:
                        logger.info("Successfully posted 1 queued article")
                    else:
                        # Return article to queue if posting failed
                        queued_articles.insert(0, article_to_post)
                        FileManager.save_posted_articles(self.posted_articles)
                        logger.info("Returned failed article to queue")
                else:
                    logger.info("No new articles to post (all articles were already posted)")
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
        bot = BitcoinMiningNewsBot()
        bot.run()


if __name__ == "__main__":
    main()