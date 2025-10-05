#!/usr/bin/env python3
"""
Bitcoin Mining News Twitter Bot
===============================
Elegant Twitter bot for Bitcoin mining news using the new core architecture.

This is the main entry point that maintains backward compatibility while
using the new streamlined core module.
"""

import sys
from core import BitcoinMiningBot, Config, Article, Storage, TextProcessor, TimeManager


# =============================================================================
# BACKWARD COMPATIBILITY LAYER
# =============================================================================

class BitcoinMiningNewsBotLegacy(BitcoinMiningBot):
    """
    Legacy compatibility wrapper for the old bot interface.
    Maintains backward compatibility with existing tests and usage patterns.
    """
    
    def __init__(self, safe_mode: bool = False):
        """Initialize with legacy parameters."""
        config = Config.from_env()
        super().__init__(config=config, safe_mode=safe_mode)
        
        # Legacy attributes for test compatibility
        self.rate_limit_cooldown_file = config.rate_limit_file
        self.posted_articles = self.posted_data
        
        # Legacy API client properties
        self.api_manager = self
        self.tweet_poster = self
        self.image_selector = None  # Image functionality simplified away for now
    
    # Legacy method mappings for backward compatibility
    def fetch_bitcoin_mining_articles(self, max_articles: int = 20):
        """Legacy method for fetching articles."""
        if self.safe_mode:
            return []
        return [self._article_to_dict(article) for article in self.news.fetch_articles(max_articles)]
    
    def create_tweet_text(self, article_dict):
        """Legacy method for creating tweet text."""
        article = Article.from_dict(article_dict)
        return TextProcessor.create_tweet_text(article)
    
    def post_to_twitter(self, article_dict):
        """Legacy method for posting to Twitter."""
        article = Article.from_dict(article_dict)
        return self.twitter.post_tweet(TextProcessor.create_tweet_text(article))
    
    def _save_posted_articles(self):
        """Legacy method for saving posted articles."""
        self._save_data()
    
    def _set_rate_limit_cooldown(self):
        """Legacy method for setting rate limit cooldown."""
        cooldown_data = TimeManager.create_cooldown_data(self.config.cooldown_hours)
        self.storage.save_json(self.config.rate_limit_file, cooldown_data)
    
    def _is_rate_limit_cooldown_active(self):
        """Legacy method for checking rate limit cooldown."""
        return self._is_rate_limited()
    
    def _is_minimum_interval_respected(self):
        """Legacy method for checking minimum interval."""
        return self._can_run_now()
    
    def _post_with_retry(self, article_dict, max_retries: int = 1):
        """Legacy method for posting with retry."""
        article = Article.from_dict(article_dict)
        success = self._post_article(article)
        return "mock_tweet_id" if success else None
    
    # Legacy property mappings
    @property
    def twitter_client(self):
        """Legacy property for Twitter client access."""
        return self.twitter.client if hasattr(self.twitter, 'client') else None
    
    def get_twitter_client(self):
        """Legacy method for getting Twitter client."""
        return self.twitter
    
    def get_eventregistry_client(self):
        """Legacy method for getting EventRegistry client."""
        return self.news
    
    def get_gemini_client(self):
        """Legacy method for getting Gemini client (not implemented in core)."""
        return None
    
    def _article_to_dict(self, article: Article) -> dict:
        """Convert Article object to legacy dict format."""
        return {
            "title": article.title,
            "body": article.body,
            "url": article.url,
            "uri": article.url,
            "source": {"title": article.source},
            "dateTimePub": article.date_published.isoformat() if article.date_published else None
        }


# =============================================================================
# SIMPLE UTILITIES FOR EXTERNAL SCRIPTS
# =============================================================================

class FileManager:
    """Legacy FileManager for external script compatibility."""
    
    @staticmethod
    def load_posted_articles():
        return Storage.load_posted_articles("posted_articles.json")
    
    @staticmethod
    def save_posted_articles(data):
        return Storage.save_json("posted_articles.json", data)
    
    @staticmethod
    def load_rate_limit_cooldown():
        return Storage.load_json("rate_limit_cooldown.json", {})
    
    @staticmethod
    def save_rate_limit_cooldown(data):
        return Storage.save_json("rate_limit_cooldown.json", data)


class TimeUtils:
    """Legacy TimeUtils for external script compatibility."""
    
    @staticmethod
    def is_minimum_interval_respected(last_run_time):
        return TimeManager.is_minimum_interval_passed(last_run_time, 90)
    
    @staticmethod
    def create_rate_limit_cooldown():
        return TimeManager.create_cooldown_data(2)
    
    @staticmethod
    def is_rate_limit_cooldown_active(cooldown_data):
        return TimeManager.is_cooldown_active(cooldown_data)


class TextUtils:
    """Legacy TextUtils for external script compatibility."""
    
    @staticmethod
    def create_tweet_text(article_dict):
        article = Article.from_dict(article_dict)
        return TextProcessor.create_tweet_text(article)
    
    @staticmethod
    def create_enhanced_tweet_text(article_dict):
        # Simplified version - just return regular tweet text
        return TextUtils.create_tweet_text(article_dict)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function with legacy compatibility."""
    # Use legacy wrapper for backward compatibility
    bot = BitcoinMiningNewsBotLegacy(
        safe_mode='--diagnose' in sys.argv
    )
    
    success = bot.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()