"""
Utility functions for Bitcoin Mining News Bot - Simplified Version
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from config import BotConstants

logger = logging.getLogger('bitcoin_mining_bot')


class RuntimeLogger:
    """Simplified runtime logger stub for compatibility"""
    
    @staticmethod
    def initialize_runtime_logs():
        """Initialize runtime logs - simplified stub"""
        # This is a stub for compatibility with the GitHub Actions workflow
        # The workflow creates the runtime-logs directory and files
        pass


class FileManager:
    """Manages file operations for the bot"""
    
    @staticmethod
    def _load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """Load JSON file safely"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    @staticmethod
    def _save_json_file(file_path: str, data: Dict[str, Any]) -> None:
        """Save JSON file safely"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_posted_articles() -> Dict[str, Any]:
        """Load posted articles with auto-upgrade"""
        data = FileManager._load_json_file(BotConstants.POSTED_ARTICLES_FILE)
        
        if data is None:
            data = {"posted_uris": [], "queued_articles": [], "last_run_time": None}
        else:
            # Auto-upgrade old format
            if "queued_articles" not in data:
                logger.info("Auto-upgrading posted_articles.json to include queued_articles")
                data["queued_articles"] = []
            if "last_run_time" not in data:
                logger.info("Auto-upgrading posted_articles.json to include last_run_time")
                data["last_run_time"] = None
        
        return data
    
    @staticmethod
    def save_posted_articles(posted_articles: Dict[str, Any], update_last_run_time: bool = False) -> None:
        """Save posted articles with optional timestamp update"""
        if update_last_run_time:
            posted_articles["last_run_time"] = datetime.now().isoformat()
        
        FileManager._save_json_file(BotConstants.POSTED_ARTICLES_FILE, posted_articles)
        
        posted_count = len(posted_articles.get("posted_uris", []))
        queued_count = len(posted_articles.get("queued_articles", []))
        logger.info(f"Saved {posted_count} posted article URIs and {queued_count} queued articles")
    
    @staticmethod
    def load_rate_limit_cooldown() -> Optional[Dict[str, Any]]:
        """Load rate limit cooldown data"""
        return FileManager._load_json_file(BotConstants.RATE_LIMIT_COOLDOWN_FILE)
    
    @staticmethod
    def save_rate_limit_cooldown(cooldown_data: Dict[str, Any]) -> None:
        """Save rate limit cooldown data"""
        FileManager._save_json_file(BotConstants.RATE_LIMIT_COOLDOWN_FILE, cooldown_data)
    
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
    def get_last_run_time(posted_articles: Dict[str, Any]) -> Optional[datetime]:
        """Get last run time from posted articles data"""
        last_run_str = posted_articles.get("last_run_time")
        if last_run_str:
            try:
                return datetime.fromisoformat(last_run_str)
            except ValueError:
                return None
        return None
    
    @staticmethod
    def is_minimum_interval_respected(posted_articles: Dict[str, Any]) -> bool:
        """Check if minimum interval since last run is respected"""
        last_run_time = TimeUtils.get_last_run_time(posted_articles)
        if last_run_time is None:
            return True
        
        time_since_last_run = datetime.now() - last_run_time
        minimum_interval = timedelta(minutes=BotConstants.MINIMUM_INTERVAL_MINUTES)
        
        if time_since_last_run < minimum_interval:
            remaining = minimum_interval - time_since_last_run
            logger.info(f"⏰ Minimum interval not reached. Need to wait {remaining} more.")
            return False
        
        return True
    
    @staticmethod
    def create_rate_limit_cooldown() -> Dict[str, Any]:
        """Create rate limit cooldown data"""
        cooldown_until = datetime.now() + timedelta(hours=BotConstants.RATE_LIMIT_INITIAL_HOURS)
        
        cooldown_data = {
            "cooldown_until": cooldown_until.isoformat(),
            "cooldown_count": 1
        }
        
        logger.warning(f"Rate limit cooldown set for {BotConstants.RATE_LIMIT_INITIAL_HOURS} hours. Bot will not run until: {cooldown_until.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning("This prevents the bot from exceeding Twitter's rate limits.")
        
        return cooldown_data
    
    @staticmethod
    def is_rate_limit_cooldown_active(cooldown_data: Optional[Dict[str, Any]]) -> bool:
        """Check if we're still in rate limit cooldown period"""
        if not cooldown_data:
            return False
        
        try:
            cooldown_until = datetime.fromisoformat(cooldown_data["cooldown_until"])
            if datetime.now() < cooldown_until:
                remaining = cooldown_until - datetime.now()
                logger.info(f"⏰ Rate limit cooldown active. {remaining} remaining.")
                return True
            return False
        except (KeyError, ValueError):
            return False


class TextUtils:
    """Simplified text processing utility functions"""
    
    @staticmethod
    def create_tweet_text(article: Dict[str, Any]) -> str:
        """Create tweet text - alias for enhanced tweet text"""
        return TextUtils.create_enhanced_tweet_text(article)
    
    @staticmethod
    def create_enhanced_tweet_text(article: Dict[str, Any]) -> str:
        """Create tweet text with basic optimization"""
        # Use Gemini headline if available, otherwise use original title
        title = article.get("gemini_headline") or article.get("title", "")
        
        if not title or not title.strip():
            return "Bitcoin Mining News Update"
        
        # Basic truncation to fit tweet limits
        max_length = BotConstants.TWEET_TRUNCATE_LENGTH
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."
        
        return title
    
    @staticmethod
    def create_hook_tweet(article: Dict[str, Any]) -> str:
        """Create hook tweet - same as enhanced tweet for simplicity"""
        return TextUtils.create_enhanced_tweet_text(article)
    
    @staticmethod
    def create_link_tweet(article: Dict[str, Any]) -> str:
        """Create link tweet with URL and proper truncation"""
        url = article.get("url", "")
        if not url:
            return ""
        
        link_text = f"{BotConstants.TWEET_CALL_TO_ACTION} {url}"
        
        # Truncate if too long
        if len(link_text) > BotConstants.TWEET_MAX_LENGTH:
            # Truncate the URL with "..."
            max_url_length = BotConstants.TWEET_MAX_LENGTH - len(BotConstants.TWEET_CALL_TO_ACTION) - 1 - 3  # space + "..."
            truncated_url = url[:max_url_length] + "..."
            link_text = f"{BotConstants.TWEET_CALL_TO_ACTION} {truncated_url}"
        
        return link_text
    
    @staticmethod
    def create_thread_texts(article: Dict[str, Any]) -> tuple[str, str]:
        """Create thread texts for article - returns (hook_text, link_text)"""
        hook_text = TextUtils.create_hook_tweet(article)
        url = article.get("url", "")
        
        # Check if URL is already in hook text to prevent duplication
        if url and url in hook_text:
            link_text = BotConstants.TWEET_CALL_TO_ACTION  # Just the call to action without URL
        else:
            link_text = TextUtils.create_link_tweet(article)
        
        return (hook_text, link_text)