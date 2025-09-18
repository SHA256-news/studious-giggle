"""
Bitcoin Mining News Twitter Bot
-------------------------------
This bot fetches the latest Bitcoin mining news from EventRegistry (NewsAPI.ai)
and posts them to Twitter/X as threaded tweets.
"""

import os
import json
import logging
import random
import time
from datetime import datetime, timedelta

import tweepy
from eventregistry import EventRegistry, QueryArticles, QueryItems, RequestArticlesInfo, ReturnInfo, ArticleInfoFlags

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('bitcoin_mining_bot')


class BitcoinMiningNewsBot:
    def __init__(self, safe_mode=False):
        """
        Initialize the bot
        
        Args:
            safe_mode (bool): If True, skip API initialization for diagnostics
        """
        # Define cooldown file path
        self.rate_limit_cooldown_file = "rate_limit_cooldown.json"
        
        if safe_mode:
            logger.info("Running in safe mode - API clients not initialized")
            self.twitter_client = None
            self.er_client = None
            self.posted_articles = self._load_posted_articles()
            return
            
        # Load API credentials
        self.twitter_client = self._init_twitter_client()
        self.er_client = self._init_eventregistry_client()

        # Load history of posted articles
        self.posted_articles = self._load_posted_articles()
        logger.info(f"Loaded {len(self.posted_articles['posted_uris'])} previously posted articles")

    def _init_twitter_client(self):
        """Initialize Twitter API client with OAuth 1.0a"""
        try:
            # Check if all required environment variables are set
            required_vars = ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET"]
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            
            if missing_vars:
                logger.error(f"Missing required Twitter API environment variables: {missing_vars}")
                logger.error("Please set these variables in your GitHub repository secrets or environment")
                raise ValueError(f"Missing environment variables: {missing_vars}")
            
            client = tweepy.Client(
                consumer_key=os.environ.get("TWITTER_API_KEY"),
                consumer_secret=os.environ.get("TWITTER_API_SECRET"),
                access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
            )
            logger.info("Twitter client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise

    def _init_eventregistry_client(self):
        """Initialize EventRegistry API client"""
        try:
            api_key = os.environ.get("EVENTREGISTRY_API_KEY")
            if not api_key:
                logger.error("Missing required EVENTREGISTRY_API_KEY environment variable")
                logger.error("Please set this variable in your GitHub repository secrets or environment")
                raise ValueError("Missing environment variable: EVENTREGISTRY_API_KEY")
            
            er = EventRegistry(apiKey=api_key)
            logger.info("EventRegistry client initialized successfully")
            return er
        except Exception as e:
            logger.error(f"Failed to initialize EventRegistry client: {str(e)}")
            raise

    def _load_posted_articles(self):
        """Load the list of already posted article URIs"""
        try:
            with open("posted_articles.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing posted articles file found, creating new one")
            return {"posted_uris": []}

    def _save_posted_articles(self):
        """Save the list of posted article URIs"""
        with open("posted_articles.json", "w") as f:
            json.dump(self.posted_articles, f, indent=2)
        logger.info(f"Saved {len(self.posted_articles['posted_uris'])} posted article URIs")

    def _is_rate_limit_cooldown_active(self):
        """Check if we're still in rate limit cooldown period"""
        try:
            with open(self.rate_limit_cooldown_file, "r") as f:
                cooldown_data = json.load(f)
                cooldown_timestamp = datetime.fromisoformat(cooldown_data["cooldown_until"])
                
                if datetime.now() < cooldown_timestamp:
                    remaining_seconds = (cooldown_timestamp - datetime.now()).total_seconds()
                    remaining_minutes = int(remaining_seconds / 60)
                    logger.warning(f"Rate limit cooldown active. Skipping run. {remaining_minutes} minutes remaining.")
                    return True
                else:
                    # Cooldown period has passed, remove the file
                    os.remove(self.rate_limit_cooldown_file)
                    logger.info("Rate limit cooldown period ended. Proceeding with normal operation.")
                    return False
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            # No cooldown file or invalid format - proceed normally
            return False
    
    def _set_rate_limit_cooldown(self):
        """Set a 1-hour cooldown period due to rate limiting"""
        cooldown_until = datetime.now() + timedelta(hours=1)
        cooldown_data = {
            "cooldown_until": cooldown_until.isoformat(),
            "reason": "Twitter API rate limit exceeded",
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.rate_limit_cooldown_file, "w") as f:
            json.dump(cooldown_data, f, indent=2)
        
        logger.warning(f"Rate limit cooldown set. Bot will not run until: {cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning("This prevents the automation from running again for 1 hour as required.")

    def fetch_bitcoin_mining_articles(self, max_articles=10):
        """Fetch latest articles about Bitcoin mining"""
        try:
            logger.info("Fetching Bitcoin mining articles...")

            # Set time limit to recent articles (last 24 hours)
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=1)

            # Create a query for articles about Bitcoin mining
            q = QueryArticles(
                keywords=QueryItems.OR(["Bitcoin mining", "crypto mining", "cryptocurrency mining"]),
                conceptUri=QueryItems.OR([
                    self.er_client.getConceptUri("Bitcoin"),
                    self.er_client.getConceptUri("Mining"),
                    self.er_client.getConceptUri("Cryptocurrency")
                ]),
                dataType=["news"],
                lang="eng",
                dateStart=yesterday,
                dateEnd=current_date
            )

            # Request article information
            q.setRequestedResult(
                RequestArticlesInfo(
                    page=1,
                    count=max_articles,
                    sortBy="date",
                    sortByAsc=False,
                    returnInfo=ReturnInfo(
                        articleInfo=ArticleInfoFlags(
                            duplicateList=False,
                            concepts=True,
                            categories=True,
                            image=True,
                            title=True,
                            body=True,
                            sentiment=True
                        )
                    )
                )
            )

            # Execute the query
            result = self.er_client.execQuery(q)

            if "articles" in result and "results" in result["articles"]:
                articles = result["articles"]["results"]
                logger.info(f"Found {len(articles)} articles about Bitcoin mining")
                return articles
            else:
                logger.warning("No articles found or unexpected response format")
                logger.debug(f"EventRegistry response: {result}")
                return []

        except Exception as e:
            error_msg = str(e)
            if "User is not logged in" in error_msg:
                logger.error("EventRegistry authentication failed - check EVENTREGISTRY_API_KEY")
                logger.error("The API key may be missing, invalid, or expired")
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                logger.error("EventRegistry API quota/rate limit exceeded")
            else:
                logger.error(f"Error fetching articles: {error_msg}")
            return []

    def create_tweet_text(self, article):
        """Create catchy tweet text for the article"""
        try:
            # Choose a catchy prefix
            prefixes = ["BREAKING: ", "JUST IN: ", "ALERT: ", "NEWS: ", "UPDATE: "]
            prefix = random.choice(prefixes)

            # Create a summary (use article title if it's concise enough)
            title = article.get("title", "") or ""  # Handle None values
            title = title.strip() if title else ""

            # Clean up and shorten the title if needed
            if len(title) <= 240:  # Leave some room for the prefix
                summary = title
            else:
                # Take first sentence or truncate
                first_period = title.find(".")
                if first_period > 0 and first_period < 240:
                    summary = title[:first_period+1]
                else:
                    summary = title[:240] + "..."

            # Create the tweet text with the prefix
            tweet_text = f"{prefix}{summary}"

            # Truncate if too long for Twitter (280 character limit)
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."

            return tweet_text

        except Exception as e:
            logger.error(f"Error creating tweet text: {str(e)}")
            # Return a fallback tweet text with proper None handling
            fallback_title = article.get("title", "") or ""
            return "New Bitcoin mining article: " + fallback_title[:240]

    def post_to_twitter(self, article):
        """Post article as a thread on Twitter"""
        return self._post_with_retry(article, max_retries=3)
        
    def _post_with_retry(self, article, max_retries=3):
        """Post to Twitter with exponential backoff retry logic for rate limits"""
        for attempt in range(max_retries + 1):
            try:
                # Create the first tweet with a catchy summary
                tweet_text = self.create_tweet_text(article)
                logger.info(f"Posting tweet (attempt {attempt + 1}): {tweet_text[:50]}...")

                # Post the first tweet
                first_tweet = self.twitter_client.create_tweet(text=tweet_text)
                first_tweet_id = first_tweet.data["id"]
                logger.info(f"Posted first tweet with ID: {first_tweet_id}")

                # Create the second tweet with the article link
                article_url = article.get("url", "")
                if article_url:
                    try:
                        # Post as a reply to create a thread using the supported reply parameter
                        reply_parameters = {"in_reply_to_tweet_id": first_tweet_id}
                        second_tweet = self.twitter_client.create_tweet(
                            text=f"Read more: {article_url}",
                            reply=reply_parameters
                        )
                        second_tweet_id = second_tweet.data["id"]
                        logger.info(f"Posted second tweet (reply) with ID: {second_tweet_id}")
                    except Exception as e:
                        logger.error(f"Error posting second tweet: {str(e)}")
                        logger.info("First tweet was successful, continuing...")

                return first_tweet_id

            except tweepy.TooManyRequests as e:
                if attempt < max_retries:
                    # Calculate exponential backoff delay
                    delay = (2 ** attempt) * 60  # 1 min, 2 min, 4 min
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}. Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries + 1} attempts. Skipping this article.")
                    # Set cooldown to prevent automation from running again for 1 hour
                    self._set_rate_limit_cooldown()
                    return None
            except Exception as e:
                logger.error(f"Error posting to Twitter (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    # For other errors, shorter delay
                    delay = 30 * (attempt + 1)  # 30s, 60s, 90s
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Failed to post after {max_retries + 1} attempts")
                    return None
        
        return None

    def run(self):
        """Main function to run the bot"""
        try:
            logger.info("Starting Bitcoin Mining News Bot")

            # Check if we're in rate limit cooldown period
            if self._is_rate_limit_cooldown_active():
                return

            # Fetch recent Bitcoin mining articles
            articles = self.fetch_bitcoin_mining_articles()
            
            if not articles:
                logger.warning("No articles found from EventRegistry")
                logger.warning("This could be due to:")
                logger.warning("  1. Missing or invalid EVENTREGISTRY_API_KEY")
                logger.warning("  2. API quota exceeded")
                logger.warning("  3. No recent Bitcoin mining articles in the last 24 hours")
                logger.warning("  4. EventRegistry service temporarily unavailable")
                return

            logger.info(f"Found {len(articles)} total articles")

            # Track if we posted anything
            posted_count = 0
            rate_limited_count = 0
            already_posted_count = 0

            # Process each article
            for article in articles:
                article_uri = article.get("uri")

                # Skip if article URI is None or already posted
                if not article_uri:
                    logger.warning("Skipping article with missing URI")
                    continue

                if article_uri in self.posted_articles["posted_uris"]:
                    logger.info(f"Skipping already posted article: {article.get('title', 'Unknown')[:50]}...")
                    already_posted_count += 1
                    continue

                # Post to Twitter
                tweet_id = self.post_to_twitter(article)

                if tweet_id:
                    # Add to posted articles
                    self.posted_articles["posted_uris"].append(article_uri)
                    posted_count += 1

                    # Only post one article per run to avoid flooding
                    logger.info(f"Posted article: {article.get('title', 'Unknown')[:50]}...")
                    break
                else:
                    # Check if it was rate limited or another error
                    rate_limited_count += 1
                    logger.warning(f"Failed to post article (likely rate limited): {article.get('title', 'Unknown')[:50]}...")

            # Save the updated list of posted articles
            self._save_posted_articles()

            # Provide detailed summary
            total_new_articles = len(articles) - already_posted_count
            if posted_count == 0:
                if total_new_articles == 0:
                    logger.info("No new articles to post (all articles were already posted)")
                elif rate_limited_count > 0:
                    logger.warning(f"Found {total_new_articles} new articles but couldn't post any due to rate limiting or other errors")
                else:
                    logger.info("No new articles were successfully posted")
            else:
                logger.info(f"Successfully posted {posted_count} new articles ({total_new_articles} new articles available, {already_posted_count} already posted)")

        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # Check if running in diagnostic mode
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose":
        logger.info("Running diagnostics...")
        from diagnose_bot import main as diagnose_main
        diagnose_main()
    else:
        try:
            bot = BitcoinMiningNewsBot()
            bot.run()
        except ValueError as e:
            if "Missing environment variables" in str(e):
                logger.error("\n" + "="*60)
                logger.error("🚨 CONFIGURATION ERROR: Missing API Keys")
                logger.error("="*60)
                logger.error("The bot cannot run without the required API keys.")
                logger.error("\nTo fix this issue:")
                logger.error("1. Go to your GitHub repository settings")
                logger.error("2. Navigate to Settings > Secrets and variables > Actions")
                logger.error("3. Add the following repository secrets:")
                logger.error("   • TWITTER_API_KEY")
                logger.error("   • TWITTER_API_SECRET")
                logger.error("   • TWITTER_ACCESS_TOKEN")
                logger.error("   • TWITTER_ACCESS_TOKEN_SECRET")
                logger.error("   • EVENTREGISTRY_API_KEY")
                logger.error("\nFor detailed setup instructions, see the README.md file.")
                logger.error("="*60)
                sys.exit(1)
            else:
                raise
