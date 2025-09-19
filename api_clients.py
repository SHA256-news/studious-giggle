"""
API clients for Bitcoin Mining News Bot
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import tweepy
from eventregistry import EventRegistry, QueryArticles, QueryItems, RequestArticlesInfo, ReturnInfo, ArticleInfoFlags

from config import TwitterConfig, EventRegistryConfig, BotConstants
from crypto_filter import filter_bitcoin_only_articles

logger = logging.getLogger('bitcoin_mining_bot')


class TwitterClient:
    """Wrapper for Twitter API client"""
    
    def __init__(self, config: TwitterConfig):
        self.client = tweepy.Client(
            consumer_key=config.api_key,
            consumer_secret=config.api_secret,
            access_token=config.access_token,
            access_token_secret=config.access_token_secret
        )
        logger.info("Twitter client initialized successfully")
    
    def create_tweet(self, **kwargs) -> Any:
        """Create a tweet"""
        return self.client.create_tweet(**kwargs)
    
    def create_media(self, **kwargs) -> Any:
        """Upload media"""
        return self.client.create_media(**kwargs)


class EventRegistryClient:
    """Wrapper for EventRegistry API client"""
    
    def __init__(self, config: EventRegistryConfig):
        self.client = EventRegistry(apiKey=config.api_key)
        logger.info("EventRegistry client initialized successfully")
    
    def fetch_bitcoin_mining_articles(self, max_articles: int = BotConstants.DEFAULT_MAX_ARTICLES) -> List[Dict[str, Any]]:
        """Fetch latest articles about Bitcoin mining"""
        try:
            logger.info("Fetching Bitcoin mining articles...")

            # Set time limit to recent articles (last 24 hours)
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=BotConstants.ARTICLE_LOOKBACK_DAYS)

            # Create a query for articles about Bitcoin mining ONLY
            # Use specific Bitcoin-focused keywords to avoid general crypto content
            q = QueryArticles(
                keywords=QueryItems.OR(BotConstants.BITCOIN_KEYWORDS),
                conceptUri=QueryItems.AND([
                    self.client.getConceptUri("Bitcoin"),
                    self.client.getConceptUri("Mining")
                ]),
                dataType=["news"],
                lang=BotConstants.SUPPORTED_LANGUAGES[0],
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
            result = self.client.execQuery(q)

            if "articles" in result and "results" in result["articles"]:
                raw_articles = result["articles"]["results"]
                logger.info(f"Found {len(raw_articles)} initial articles about Bitcoin mining")
                
                # Filter out articles mentioning other cryptocurrencies
                filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(raw_articles)
                
                if excluded_count > 0:
                    logger.info(f"Filtered out {excluded_count} articles mentioning non-Bitcoin cryptocurrencies")
                    logger.debug(f"Excluded articles: {[detail['title'] for detail in excluded_details[:3]]}")
                
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


class APIClientManager:
    """Manages all API clients for the bot"""
    
    def __init__(self, safe_mode: bool = False):
        self.safe_mode = safe_mode
        self.twitter_client: Optional[TwitterClient] = None
        self.eventregistry_client: Optional[EventRegistryClient] = None
        
        if not safe_mode:
            self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize all API clients"""
        try:
            twitter_config = TwitterConfig.from_env()
            self.twitter_client = TwitterClient(twitter_config)
        except ValueError as e:
            logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise
        
        try:
            eventregistry_config = EventRegistryConfig.from_env()
            self.eventregistry_client = EventRegistryClient(eventregistry_config)
        except ValueError as e:
            logger.error(f"Failed to initialize EventRegistry client: {str(e)}")
            raise
    
    def get_twitter_client(self) -> TwitterClient:
        """Get Twitter client"""
        if not self.twitter_client:
            raise RuntimeError("Twitter client not initialized")
        return self.twitter_client
    
    def get_eventregistry_client(self) -> EventRegistryClient:
        """Get EventRegistry client"""
        if not self.eventregistry_client:
            raise RuntimeError("EventRegistry client not initialized")
        return self.eventregistry_client