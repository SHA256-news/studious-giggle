"""
Tweet posting logic for Bitcoin Mining News Bot
"""

import logging
import time
from typing import Dict, Any, Optional, List

try:
    from tweepy.errors import TooManyRequests as TweepyTooManyRequests
except (ImportError, AttributeError):
    class TweepyTooManyRequests(Exception):
        """Fallback TooManyRequests when tweepy is fully mocked in tests."""
        def __init__(self, *args, **kwargs):
            response = kwargs.pop('response', None)
            api_errors = kwargs.pop('api_errors', None)
            super().__init__(*args)
            self.response = response
            self.api_errors = api_errors
            for key, value in kwargs.items():
                setattr(self, key, value)


class InvalidTweetResponse(Exception):
    """Raised when the Twitter client returns an unexpected response."""


from config import BotConstants
from utils import TextUtils
from api_clients import TwitterClient

# Import image functionality
try:
    from image_selector import ImageSelector
    IMAGE_SUPPORT_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger('bitcoin_mining_bot')
    logger.warning(f"Image support not available: {e}")
    ImageSelector = None
    IMAGE_SUPPORT_AVAILABLE = False

logger = logging.getLogger('bitcoin_mining_bot')


class TweetPoster:
    """Handles posting tweets to Twitter"""
    
    def __init__(self, twitter_client: TwitterClient):
        self.twitter_client = twitter_client
        self.image_selector = None
        
        # Initialize image selector if available
        if IMAGE_SUPPORT_AVAILABLE:
            try:
                self.image_selector = ImageSelector()
                logger.info("Image support enabled - images will be attached to tweets")
            except Exception as e:
                logger.warning(f"Failed to initialize image selector: {e}")
                self.image_selector = None
        else:
            logger.info("Image support disabled - tweets will be text-only")
    
    def post_to_twitter(self, article: Dict[str, Any]) -> Optional[str]:
        """Post article as a single tweet on Twitter"""
        return self._post_with_retry(article, max_retries=BotConstants.MAX_RETRIES)
    
    def _post_with_retry(self, article: Dict[str, Any], max_retries: int = BotConstants.MAX_RETRIES) -> Optional[str]:
        """Post to Twitter with conservative retry logic for daily rate limits"""
        for attempt in range(max_retries + 1):
            try:
                # Create the first tweet with a catchy summary
                tweet_text = TextUtils.create_tweet_text(article)
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
                logger.error(f"Invalid Twitter API response on attempt {attempt + 1}: {invalid_response}")
                if attempt < max_retries:
                    logger.info("Retrying immediately due to invalid response...")
                    continue
                else:
                    logger.error(f"Failed to post after {max_retries + 1} attempts due to invalid response")
                    return None

            except TweepyTooManyRequests as rate_limit_error:
                if attempt < max_retries:
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}. Waiting {BotConstants.RETRY_DELAY_SECONDS} seconds before retry...")
                    logger.warning(f"Daily rate limit is {BotConstants.DAILY_REQUEST_LIMIT} requests per 24 hours - being conservative with retries")
                    time.sleep(BotConstants.RETRY_DELAY_SECONDS)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries + 1} attempts. Skipping this article.")
                    logger.error(f"Daily rate limit reached ({BotConstants.DAILY_REQUEST_LIMIT} requests per 24 hours). Setting extended cooldown.")
                    # Set rate limit cooldown
                    from utils import TimeUtils, FileManager
                    cooldown_data = TimeUtils.create_rate_limit_cooldown()
                    FileManager.save_rate_limit_cooldown(cooldown_data)
                    return None

            except Exception as e:
                logger.error(f"Error posting to Twitter on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {BotConstants.RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(BotConstants.RETRY_DELAY_SECONDS)
                    continue
                else:
                    logger.error(f"Failed to post after {max_retries + 1} attempts")
                    return None

        return None
    
    def _select_and_upload_images(self, article: Dict[str, Any]) -> List[str]:
        """Select and upload images for the article"""
        if not self.image_selector:
            return []
        
        title = article.get("title", "")
        if not title:
            logger.info("No title available for image selection")
            return []
        
        # Select relevant images
        selected_images = self.image_selector.select_images_for_headline(title)
        if not selected_images:
            logger.info("No valid images found for article")
            return []
        
        # Upload images to Twitter
        media_ids = []
        for image_path in selected_images:
            try:
                media = self.twitter_client.create_media(filename=image_path)
                media_ids.append(media.media_id)
                logger.info(f"Uploaded image: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to upload image {image_path}: {e}")
        
        return media_ids
    
    def _looks_like_rate_limit_response(self, response: Any) -> bool:
        """Check if response looks like a rate limit error"""
        # Check for mock rate limit responses
        if hasattr(response, '__class__') and 'TooManyRequests' in str(response.__class__):
            return True
        if hasattr(response, 'data') and response.data is None:
            return True
        return False
    
    def _extract_tweet_id(self, tweet_response: Any) -> Optional[str]:
        """Extract tweet ID from Twitter API response"""
        try:
            if hasattr(tweet_response, 'data') and tweet_response.data:
                if hasattr(tweet_response.data, 'get'):
                    return tweet_response.data.get('id')
                elif hasattr(tweet_response.data, 'id'):
                    return tweet_response.data.id
                elif isinstance(tweet_response.data, dict):
                    return tweet_response.data.get('id')
            
            # Fallback for different response formats
            if hasattr(tweet_response, 'id'):
                return tweet_response.id
            elif isinstance(tweet_response, dict):
                return tweet_response.get('id')
            
            logger.warning(f"Could not extract tweet ID from response: {type(tweet_response)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting tweet ID: {e}")
            return None