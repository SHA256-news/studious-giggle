"""
Twitter adapter - posts threads to Twitter/X.
"""
import logging
from typing import List, Optional

import tweepy

from src.domain import Thread
from src.adapters.interfaces import SocialMediaPublisher, PublisherError

logger = logging.getLogger(__name__)


class TwitterAdapter(SocialMediaPublisher):
    """Adapter for Twitter/X API."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """
        Initialize Twitter client.
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
        """
        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError("All Twitter credentials must be provided")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self._client: Optional[tweepy.Client] = None
    
    @property
    def client(self) -> tweepy.Client:
        """Lazy-load Twitter client."""
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
        return self._client
    
    def is_authenticated(self) -> bool:
        """Check if Twitter client is authenticated."""
        try:
            # Try to get authenticated user info
            me = self.client.get_me()
            return me is not None
        except Exception as e:
            logger.error(f"Twitter authentication check failed: {e}")
            return False
    
    def post_thread(self, thread: Thread) -> Optional[List[str]]:
        """
        Post a thread to Twitter.
        
        Args:
            thread: Thread object containing tweets
            
        Returns:
            List of tweet IDs if successful, None otherwise
            
        Raises:
            PublisherError: If posting fails
        """
        try:
            tweet_texts = thread.to_list()
            tweet_ids: List[str] = []
            previous_id: Optional[str] = None
            
            logger.info(f"Posting thread with {len(tweet_texts)} tweets")
            
            for i, text in enumerate(tweet_texts):
                try:
                    # Post tweet as reply to previous tweet
                    response = self.client.create_tweet(
                        text=text,
                        in_reply_to_tweet_id=previous_id
                    )
                    
                    if response and response.data:
                        tweet_id = response.data['id']
                        tweet_ids.append(tweet_id)
                        previous_id = tweet_id
                        logger.info(f"Posted tweet {i + 1}/{len(tweet_texts)}: {tweet_id}")
                    else:
                        raise PublisherError(f"No response data for tweet {i + 1}")
                    
                except tweepy.errors.TweepyException as e:
                    logger.error(f"Failed to post tweet {i + 1}: {e}")
                    
                    # If first tweet fails, abort
                    if i == 0:
                        raise PublisherError(f"Failed to post first tweet: {e}") from e
                    
                    # If subsequent tweet fails, return partial success
                    logger.warning(f"Thread incomplete - posted {len(tweet_ids)}/{len(tweet_texts)} tweets")
                    return tweet_ids if tweet_ids else None
            
            logger.info(f"Successfully posted complete thread: {len(tweet_ids)} tweets")
            return tweet_ids
            
        except tweepy.errors.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            raise PublisherError(f"Failed to post thread: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error posting thread: {e}")
            raise PublisherError(f"Unexpected error: {e}") from e
