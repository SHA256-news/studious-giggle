"""
Utility functions for Bitcoin Mining News Bot
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from config import BotConstants

logger = logging.getLogger('bitcoin_mining_bot')


class FileManager:
    """Manages file operations for the bot"""
    
    @staticmethod
    def load_posted_articles() -> Dict[str, Any]:
        """Load the list of already posted article URIs and queued articles"""
        try:
            with open(BotConstants.POSTED_ARTICLES_FILE, "r") as f:
                data = json.load(f)
                # Auto-upgrade old format to include queued_articles and last_run_time
                if "queued_articles" not in data:
                    data["queued_articles"] = []
                    logger.info("Auto-upgrading posted_articles.json to include queued_articles")
                if "last_run_time" not in data:
                    data["last_run_time"] = None
                    logger.info("Auto-upgrading posted_articles.json to include last_run_time")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing posted articles file found, creating new one")
            return {"posted_uris": [], "queued_articles": [], "last_run_time": None}
    
    @staticmethod
    def save_posted_articles(posted_articles: Dict[str, Any]) -> None:
        """Save the list of posted article URIs and queued articles"""
        # Update last run time before saving
        posted_articles["last_run_time"] = datetime.now().isoformat()
        
        with open(BotConstants.POSTED_ARTICLES_FILE, "w") as f:
            json.dump(posted_articles, f, indent=2)
        queued_count = len(posted_articles.get("queued_articles", []))
        posted_count = len(posted_articles["posted_uris"])
        logger.info(f"Saved {posted_count} posted article URIs and {queued_count} queued articles")
    
    @staticmethod
    def load_rate_limit_cooldown() -> Optional[Dict[str, Any]]:
        """Load rate limit cooldown data"""
        try:
            with open(BotConstants.RATE_LIMIT_COOLDOWN_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def save_rate_limit_cooldown(cooldown_data: Dict[str, Any]) -> None:
        """Save rate limit cooldown data"""
        with open(BotConstants.RATE_LIMIT_COOLDOWN_FILE, "w") as f:
            json.dump(cooldown_data, f, indent=2)
    
    @staticmethod
    def remove_rate_limit_cooldown() -> None:
        """Remove rate limit cooldown file"""
        try:
            os.remove(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
        except FileNotFoundError:
            pass


class TimeUtils:
    """Time-related utility functions"""
    
    @staticmethod
    def is_minimum_interval_respected(last_run_time: Optional[str]) -> bool:
        """Check if at least 90 minutes have passed since the last successful run"""
        if not last_run_time:
            return True  # No previous run recorded
        
        try:
            last_run = datetime.fromisoformat(last_run_time)
            time_since_last_run = datetime.now() - last_run
            minimum_interval = timedelta(minutes=BotConstants.MINIMUM_INTERVAL_MINUTES)
            
            if time_since_last_run < minimum_interval:
                remaining_minutes = int((minimum_interval - time_since_last_run).total_seconds() / 60)
                logger.warning(f"Minimum {BotConstants.MINIMUM_INTERVAL_MINUTES}-minute interval not respected. "
                             f"Last run was {int(time_since_last_run.total_seconds() / 60)} minutes ago. "
                             f"Waiting {remaining_minutes} more minutes.")
                return False
            return True
        except (ValueError, TypeError):
            logger.warning("Invalid last_run_time format, proceeding with run")
            return True
    
    @staticmethod
    def is_rate_limit_cooldown_active(cooldown_data: Optional[Dict[str, Any]]) -> bool:
        """Check if we're still in rate limit cooldown period"""
        if not cooldown_data:
            return False
            
        try:
            cooldown_timestamp = datetime.fromisoformat(cooldown_data["cooldown_until"])
            
            if datetime.now() < cooldown_timestamp:
                remaining_seconds = (cooldown_timestamp - datetime.now()).total_seconds()
                remaining_hours = int(remaining_seconds / 3600)
                remaining_minutes = int((remaining_seconds % 3600) / 60)
                
                if remaining_hours > 0:
                    logger.warning(f"Rate limit cooldown active. Skipping run. {remaining_hours}h {remaining_minutes}m remaining.")
                else:
                    logger.warning(f"Rate limit cooldown active. Skipping run. {remaining_minutes} minutes remaining.")
                return True
            else:
                # Cooldown period has passed
                FileManager.remove_rate_limit_cooldown()
                logger.info("Rate limit cooldown period ended. Proceeding with normal operation.")
                return False
        except (KeyError, ValueError):
            # Invalid format - proceed normally
            return False
    
    @staticmethod
    def create_rate_limit_cooldown() -> Dict[str, Any]:
        """Create a new rate limit cooldown period"""
        # Simple cooldown: Start with 2 hours, then 4 hours for subsequent hits
        existing_cooldown_exists = os.path.exists(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
        cooldown_hours = BotConstants.RATE_LIMIT_SUBSEQUENT_HOURS if existing_cooldown_exists else BotConstants.RATE_LIMIT_INITIAL_HOURS
        
        cooldown_until = datetime.now() + timedelta(hours=cooldown_hours)
        cooldown_data = {
            "cooldown_until": cooldown_until.isoformat(),
            "reason": f"Twitter API rate limit exceeded ({BotConstants.DAILY_REQUEST_LIMIT} requests per 24 hours)",
            "created_at": datetime.now().isoformat(),
            "duration_hours": cooldown_hours
        }
        
        logger.warning(f"Rate limit cooldown set for {cooldown_hours} hours. "
                      f"Bot will not run until: {cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning("This prevents the bot from exceeding Twitter's rate limits.")
        
        return cooldown_data


class TextUtils:
    """Text processing utility functions"""
    
    @staticmethod
    def create_tweet_text(article: Dict[str, Any]) -> str:
        """Create catchy tweet text for the article"""
        import random
        
        try:
            # Choose a catchy prefix
            prefix = random.choice(BotConstants.TWEET_PREFIXES)

            # Create a summary (use article title if it's concise enough)
            title = article.get("title", "") or ""  # Handle None values
            title = title.strip() if title else ""

            # Clean up and shorten the title if needed
            if len(title) <= BotConstants.TITLE_MAX_LENGTH:  # Leave some room for the prefix
                summary = title
            else:
                # Take first sentence or truncate
                first_period = title.find(".")
                if first_period > 0 and first_period < BotConstants.TITLE_MAX_LENGTH:
                    summary = title[:first_period+1]
                else:
                    summary = title[:BotConstants.TITLE_MAX_LENGTH] + "..."

            # Create the tweet text with the prefix
            tweet_text = f"{prefix}{summary}"

            # Truncate if too long for Twitter (280 character limit)
            if len(tweet_text) > BotConstants.TWEET_MAX_LENGTH:
                tweet_text = tweet_text[:BotConstants.TWEET_TRUNCATE_LENGTH] + "..."

            return tweet_text

        except Exception as e:
            logger.error(f"Error creating tweet text: {str(e)}")
            # Return a fallback tweet text with proper None handling
            fallback_title = article.get("title", "") or ""
            return "New Bitcoin mining article: " + fallback_title[:BotConstants.TITLE_MAX_LENGTH]