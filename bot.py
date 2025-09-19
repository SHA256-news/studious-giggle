"""
Bitcoin Mining News Twitter Bot
-------------------------------
This bot fetches the latest Bitcoin mining news from EventRegistry (NewsAPI.ai)
and posts them to Twitter/X as single tweets with catchy headlines.
"""

import os
import json
import logging
import random
import time
from datetime import datetime, timedelta

import tweepy

try:
    from tweepy.errors import TooManyRequests as TweepyTooManyRequests  # type: ignore
except (ImportError, AttributeError):
    class TweepyTooManyRequests(Exception):
        """Fallback TooManyRequests when tweepy is fully mocked in tests."""

        def __init__(self, *args, **kwargs):
            # Extract known attributes before calling super()
            response = kwargs.pop('response', None)
            api_errors = kwargs.pop('api_errors', None)
            
            # Call super with only positional args (avoid kwargs issue)
            super().__init__(*args)
            
            # Store additional attributes for compatibility
            self.response = response
            self.api_errors = api_errors
            for key, value in kwargs.items():
                setattr(self, key, value)


class InvalidTweetResponse(Exception):
    """Raised when the Twitter client returns an unexpected response."""

from eventregistry import EventRegistry, QueryArticles, QueryItems, RequestArticlesInfo, ReturnInfo, ArticleInfoFlags
from crypto_filter import filter_bitcoin_only_articles
from runtime_logger import RuntimeLogger

# Import image functionality
try:
    from image_selector import ImageSelector
    IMAGE_SUPPORT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Image support not available: {e}")
    ImageSelector = None
    IMAGE_SUPPORT_AVAILABLE = False

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
        
        # Initialize runtime logger
        self.runtime_logger = RuntimeLogger()
        
        if safe_mode:
            logger.info("Running in safe mode - API clients not initialized")
            self.twitter_client = None
            self.er_client = None
            self.image_selector = None
            self.posted_articles = self._load_posted_articles()
            return
            
        # Load API credentials
        self.twitter_client = self._init_twitter_client()
        self.er_client = self._init_eventregistry_client()

        # Load history of posted articles
        self.posted_articles = self._load_posted_articles()
        logger.info(f"Loaded {len(self.posted_articles['posted_uris'])} previously posted articles")
        
        # Initialize image selector if available
        if IMAGE_SUPPORT_AVAILABLE:
            try:
                self.image_selector = ImageSelector()
                logger.info("Image support enabled - images will be attached to tweets")
            except Exception as e:
                logger.warning(f"Failed to initialize image selector: {e}")
                self.image_selector = None
        else:
            self.image_selector = None
            logger.info("Image support disabled - tweets will be text-only")

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
        """Load the list of already posted article URIs and queued articles"""
        try:
            with open("posted_articles.json", "r") as f:
                data = json.load(f)
                # Auto-upgrade old format to include queued_articles
                if "queued_articles" not in data:
                    data["queued_articles"] = []
                    logger.info("Auto-upgrading posted_articles.json to include queued_articles")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing posted articles file found, creating new one")
            return {"posted_uris": [], "queued_articles": []}

    def _save_posted_articles(self):
        """Save the list of posted article URIs and queued articles"""
        with open("posted_articles.json", "w") as f:
            json.dump(self.posted_articles, f, indent=2)
        queued_count = len(self.posted_articles.get("queued_articles", []))
        posted_count = len(self.posted_articles["posted_uris"])
        logger.info(f"Saved {posted_count} posted article URIs and {queued_count} queued articles")

    def _is_rate_limit_cooldown_active(self):
        """Check if we're still in rate limit cooldown period"""
        try:
            with open(self.rate_limit_cooldown_file, "r") as f:
                cooldown_data = json.load(f)
                cooldown_timestamp = datetime.fromisoformat(cooldown_data["cooldown_until"])
                
                if datetime.now() < cooldown_timestamp:
                    remaining_seconds = (cooldown_timestamp - datetime.now()).total_seconds()
                    remaining_hours = int(remaining_seconds / 3600)
                    remaining_minutes = int((remaining_seconds % 3600) / 60)
                    
                    duration_hours = cooldown_data.get("duration_hours", "unknown")
                    progressive_count = cooldown_data.get("progressive_count", 1)
                    
                    if remaining_hours > 0:
                        logger.warning(f"Rate limit cooldown active ({duration_hours}h period, attempt #{progressive_count}). Skipping run. {remaining_hours}h {remaining_minutes}m remaining.")
                    else:
                        logger.warning(f"Rate limit cooldown active ({duration_hours}h period, attempt #{progressive_count}). Skipping run. {remaining_minutes} minutes remaining.")
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
        """Set a progressive cooldown period due to rate limiting"""
        # Check if there's an existing cooldown to implement progressive delays
        existing_cooldown = self._get_existing_cooldown_data()
        
        if existing_cooldown:
            # Progressive cooldown: 2h -> 4h -> 8h -> 24h
            previous_duration = self._get_cooldown_duration_hours(existing_cooldown)
            if previous_duration >= 24:
                cooldown_hours = 24  # Max 24 hours
            elif previous_duration >= 8:
                cooldown_hours = 24
            elif previous_duration >= 4:
                cooldown_hours = 8
            elif previous_duration >= 2:
                cooldown_hours = 4
            else:
                cooldown_hours = 4  # Start with 4 hours for daily rate limits
        else:
            # First rate limit hit - use 2 hours for daily rate limits
            cooldown_hours = 2
        
        cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)
        cooldown_data = {
            "cooldown_until": cooldown_until.isoformat(),
            "reason": "Twitter API daily rate limit exceeded (17 requests/24h)",
            "created_at": datetime.now().isoformat(),
            "duration_hours": cooldown_hours,
            "progressive_count": (existing_cooldown.get("progressive_count", 0) if existing_cooldown else 0) + 1
        }
        
        with open(self.rate_limit_cooldown_file, "w") as f:
            json.dump(cooldown_data, f, indent=2)
        
        logger.warning(f"Rate limit cooldown set for {cooldown_hours} hours. Bot will not run until: {cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning(f"This prevents automation from running due to Twitter's 17 requests per 24 hours limit.")
    
    def _get_existing_cooldown_data(self):
        """Get existing cooldown data if present"""
        try:
            with open(self.rate_limit_cooldown_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _get_cooldown_duration_hours(self, cooldown_data):
        """Extract cooldown duration from existing data"""
        if "duration_hours" in cooldown_data:
            return cooldown_data["duration_hours"]
        
        # Fallback: calculate from timestamps
        try:
            created = datetime.fromisoformat(cooldown_data["created_at"])
            cooldown_until = datetime.fromisoformat(cooldown_data["cooldown_until"])
            duration = cooldown_until - created
            return duration.total_seconds() / 3600
        except (KeyError, ValueError):
            return 1  # Default fallback

    def fetch_bitcoin_mining_articles(self, max_articles=10):
        """Fetch latest articles about Bitcoin mining"""
        try:
            logger.info("Fetching Bitcoin mining articles...")

            # Set time limit to recent articles (last 24 hours)
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=1)

            # Create a query for articles about Bitcoin mining ONLY
            # Use specific Bitcoin-focused keywords to avoid general crypto content
            q = QueryArticles(
                keywords=QueryItems.OR([
                    "Bitcoin mining", 
                    "BTC mining", 
                    "Bitcoin miner", 
                    "Bitcoin miners",
                    "Bitcoin hashrate",
                    "Bitcoin difficulty"
                ]),
                conceptUri=QueryItems.AND([
                    self.er_client.getConceptUri("Bitcoin"),
                    self.er_client.getConceptUri("Mining")
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
                raw_articles = result["articles"]["results"]
                logger.info(f"Found {len(raw_articles)} initial articles about Bitcoin mining")
                
                # Filter out articles mentioning other cryptocurrencies
                filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(raw_articles)
                
                if excluded_count > 0:
                    logger.info(f"Filtered out {excluded_count} articles mentioning non-Bitcoin cryptocurrencies")
                    logger.debug(f"Excluded articles: {[detail['title'] for detail in excluded_details[:3]]}")
                    # Log filtered articles to runtime logs
                    self.runtime_logger.log_crypto_filtered_articles(excluded_details)
                
                logger.info(f"Final count: {len(filtered_articles)} Bitcoin-only mining articles")
                return filtered_articles
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
        """Post article as a single tweet on Twitter"""
        return self._post_with_retry(article, max_retries=1)  # Reduced retries for daily rate limits
        
    def _post_with_retry(self, article, max_retries=1):
        """Post to Twitter with conservative retry logic for daily rate limits"""
        for attempt in range(max_retries + 1):
            try:
                # Create the first tweet with a catchy summary
                tweet_text = self.create_tweet_text(article)
                logger.info(f"Posting tweet (attempt {attempt + 1}): {tweet_text[:50]}...")

                # Select and upload images if image support is available
                media_ids = []
                if self.image_selector:
                    try:
                        images = self._select_and_upload_images(article)
                        media_ids = images
                    except Exception as e:
                        logger.warning(f"Failed to upload images, posting text-only tweet: {e}")

                # Post the tweet with images (if available)
                tweet_params = {"text": tweet_text}
                if media_ids:
                    tweet_params["media_ids"] = media_ids
                    logger.info(f"Posting tweet with {len(media_ids)} images")
                
                tweet = self.twitter_client.create_tweet(**tweet_params)

                # Some mocked Twitter clients return a TooManyRequests sentinel
                # object instead of raising the exception. Detect these cases and
                # convert them into a proper Tweepy exception so the retry logic
                # can respond consistently.
                if self._looks_like_rate_limit_response(tweet):
                    raise TweepyTooManyRequests(
                        response=getattr(tweet, "response", None),
                        api_errors=getattr(tweet, "api_errors", None) or []
                    )

                tweet_id = self._extract_tweet_id(tweet)
                if not tweet_id:
                    raise InvalidTweetResponse("missing tweet ID in response")
                logger.info(f"Posted tweet with ID: {tweet_id}")

                return tweet_id

            except InvalidTweetResponse as invalid_response:
                logger.error(f"Twitter client returned an invalid response: {invalid_response}")
                if attempt < max_retries:
                    logger.info("Retrying immediately due to invalid response...")
                    continue
                logger.error(f"Failed to post after {max_retries + 1} attempts")
                return None
            except Exception as e:
                # Check if this is a rate limit error (either tweepy.TooManyRequests or similar)
                is_rate_limit_error = (
                    "TooManyRequests" in str(type(e)) or 
                    "429" in str(e) or 
                    (hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 429) or
                    isinstance(e, TweepyTooManyRequests) or
                    # Handle mock exceptions that might contain TooManyRequests in their string representation
                    ("TooManyRequests" in str(e))
                )
                
                if is_rate_limit_error:
                    if attempt < max_retries:
                        # For daily rate limits, use longer delays (5 minutes)
                        delay = 300  # 5 minutes - conservative for daily limits
                        logger.warning(f"Rate limit hit on attempt {attempt + 1}. Waiting {delay} seconds before retry...")
                        logger.warning("Daily rate limit is 17 requests per 24 hours - being conservative with retries")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries + 1} attempts. Skipping this article.")
                        logger.error("Daily rate limit reached (17 requests per 24 hours). Setting extended cooldown.")
                        # Set progressive cooldown to prevent automation from hitting limits repeatedly
                        self._set_rate_limit_cooldown()
                        return None
                logger.error(f"Error posting to Twitter (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries:
                    # For other errors, shorter delay
                    delay = 60  # 1 minute for non-rate-limit errors
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Failed to post after {max_retries + 1} attempts")
                    return None
        
        return None

    def _select_and_upload_images(self, article):
        """Select and upload images for an article"""
        headline = article.get("title", "")
        if not headline:
            return []
        
        # Select appropriate images
        image_paths = self.image_selector.select_images_for_headline(headline)
        
        # Validate images for Twitter
        valid_images = self.image_selector.validate_images_for_twitter(image_paths)
        
        if not valid_images:
            logger.info("No valid images found for article")
            return []
        
        # Upload images to Twitter
        media_ids = []
        for image_path in valid_images[:4]:  # Twitter allows max 4 images
            try:
                media = self.twitter_client.create_media(media=image_path)
                if hasattr(media, 'media_id'):
                    media_ids.append(media.media_id)
                    logger.info(f"Uploaded image: {image_path}")
                else:
                    logger.warning(f"Failed to get media ID for: {image_path}")
            except Exception as e:
                logger.error(f"Failed to upload image {image_path}: {e}")
        
        return media_ids

    def _looks_like_rate_limit_response(self, response):
        """Detect mocked rate limit responses that aren't raised as exceptions"""
        if isinstance(response, TweepyTooManyRequests):
            return True

        response_type = type(response)
        if "TooManyRequests" in getattr(response_type, "__name__", ""):
            return True

        try:
            if "TooManyRequests" in repr(response):
                return True
        except Exception:
            pass

        return False

    def _extract_tweet_id(self, response):
        """Safely extract a tweet ID from a Twitter API response object"""
        try:
            tweet_id = response.data["id"]
            if tweet_id is None:
                return None
            return str(tweet_id)
        except (AttributeError, KeyError, TypeError):
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
                # Check if we have queued articles to post
                if not self.posted_articles.get("queued_articles"):
                    logger.warning("No articles found from EventRegistry and no queued articles available")
                    logger.warning("This could be due to:")
                    logger.warning("  1. Missing or invalid EVENTREGISTRY_API_KEY")
                    logger.warning("  2. API quota exceeded")
                    logger.warning("  3. No recent Bitcoin mining articles in the last 24 hours")
                    logger.warning("  4. EventRegistry service temporarily unavailable")
                    return
                else:
                    logger.info("No new articles found from EventRegistry, but queued articles available")
                    articles = []  # Ensure articles is an empty list for processing

            logger.info(f"Found {len(articles)} total articles")

            # Track if we posted anything
            posted_count = 0
            rate_limited_count = 0
            already_posted_count = 0

            # Filter out already posted articles
            new_articles = []
            for article in articles:
                article_uri = article.get("uri")

                # Skip if article URI is None
                if not article_uri:
                    logger.warning("Skipping article with missing URI")
                    continue

                if article_uri in self.posted_articles["posted_uris"]:
                    logger.info(f"Skipping already posted article: {article.get('title', 'Unknown')[:50]}...")
                    # Log duplicate articles to runtime logs
                    self.runtime_logger.log_duplicate_article(article)
                    already_posted_count += 1
                    continue
                
                new_articles.append(article)

            # Determine what article to post
            article_to_post = None
            
            if new_articles:
                # Process multiple new articles: post most recent, queue the rest
                article_to_post = new_articles[0]  # Most recent
                queued_count = len(new_articles) - 1
                
                if queued_count > 0:
                    logger.info(f"Found {len(new_articles)} new articles. Posting most recent, queueing {queued_count} older articles for later.")
                    # Queue older articles instead of discarding them
                    existing_queue_uris = {article.get("uri") for article in self.posted_articles["queued_articles"] if article.get("uri")}
                    for i, article_to_queue in enumerate(new_articles[1:], 1):
                        article_uri = article_to_queue.get("uri")
                        if article_uri and article_uri not in existing_queue_uris:
                            logger.info(f"  Queueing #{i}: {article_to_queue.get('title', 'Unknown')[:50]}...")
                            self.posted_articles["queued_articles"].append(article_to_queue)
                            existing_queue_uris.add(article_uri)
                        else:
                            logger.info(f"  Skipping duplicate in queue #{i}: {article_to_queue.get('title', 'Unknown')[:50]}...")
                else:
                    logger.info(f"Found 1 new article to post.")
                    
            elif self.posted_articles.get("queued_articles"):
                # No new articles, but we have queued ones - use oldest queued
                article_to_post = self.posted_articles["queued_articles"].pop(0)
                remaining_queued = len(self.posted_articles["queued_articles"])
                logger.info(f"No new articles found. Posting from queue: {article_to_post.get('title', 'Unknown')[:50]}... ({remaining_queued} articles remain in queue)")

            # Post the selected article
            if article_to_post:
                tweet_id = self.post_to_twitter(article_to_post)

                if tweet_id:
                    # Add to posted articles
                    self.posted_articles["posted_uris"].append(article_to_post.get("uri"))
                    posted_count += 1
                    logger.info(f"Posted article: {article_to_post.get('title', 'Unknown')[:50]}...")
                else:
                    # If posting failed, put article back in queue if it was from queue
                    if not new_articles and article_to_post:
                        # This was from queue, put it back at the front
                        self.posted_articles["queued_articles"].insert(0, article_to_post)
                        logger.info(f"Returned failed article to front of queue")
                        # Log as rate limited (most likely cause of failure)
                        self.runtime_logger.log_rate_limited_article(article_to_post)
                    else:
                        # This was a new article that failed to post
                        self.runtime_logger.log_failed_post(article_to_post, "Failed to post - likely rate limited")
                    rate_limited_count += 1
                    logger.warning(f"Failed to post article (likely rate limited): {article_to_post.get('title', 'Unknown')[:50]}...")

            # Save the updated list of posted articles
            self._save_posted_articles()

            # Provide detailed summary
            total_new_articles = len(articles) - already_posted_count
            queued_articles_count = len(self.posted_articles.get("queued_articles", []))
            
            if posted_count == 0:
                if total_new_articles == 0 and queued_articles_count == 0:
                    logger.info("No new articles to post (all articles were already posted and no queued articles available)")
                elif total_new_articles == 0 and queued_articles_count > 0:
                    logger.info(f"No new articles found but {queued_articles_count} articles remain in queue for future posting")
                elif rate_limited_count > 0:
                    logger.warning(f"Found {total_new_articles} new articles but couldn't post any due to rate limiting or other errors")
                    logger.warning("🔍 WHY NO TWEETS: Bot hit Twitter's 17 requests/24h limit and entered cooldown")
                    logger.warning("   This is normal behavior to avoid violating Twitter's terms of service")
                    logger.warning("   The bot will automatically resume posting when the cooldown period expires")
                    if queued_articles_count > 0:
                        logger.info(f"   {queued_articles_count} articles are queued and will be posted after cooldown")
                else:
                    logger.info("No articles were successfully posted")
            else:
                queued_count = len(new_articles) - 1 if new_articles else 0
                if queued_count > 0:
                    logger.info(f"Successfully posted 1 article. Queued {queued_count} newer articles for later ({total_new_articles} new articles available, {already_posted_count} already posted, {queued_articles_count} total in queue)")
                elif not new_articles:  # Posted from queue
                    logger.info(f"Successfully posted 1 article from queue ({queued_articles_count} articles remain in queue)")
                else:
                    logger.info(f"Successfully posted 1 article ({total_new_articles} new articles available, {already_posted_count} already posted)")
            
            # Finalize runtime logs
            blocked_count = self.runtime_logger.finalize_logs()
            if blocked_count > 0:
                logger.info(f"Runtime logs generated with {blocked_count} blocked items. Check artifacts for details.")

        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            # Still finalize logs even if there was an error
            try:
                self.runtime_logger.finalize_logs()
            except Exception as log_error:
                logger.error(f"Failed to finalize runtime logs: {log_error}")


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
