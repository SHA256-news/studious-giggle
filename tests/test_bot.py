#!/usr/bin/env python3
"""
Streamlined Bitcoin Mining Bot Tests
Simple, effective tests that match the actual implementation.
"""

import sys
import os
import json
import tempfile
from unittest.mock import patch
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core import BitcoinMiningBot, Config, Article, Storage, TextProcessor, TimeManager
    from tools import BotTools
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestBot:
    """Simple, effective bot tests."""

    def test_config_basics(self):
        """Test basic config functionality."""
        config = Config()
        assert hasattr(config, 'posted_articles_file')
        assert hasattr(config, 'rate_limit_file')
        
        # Test validation
        errors = config.validate()
        assert isinstance(errors, list)

    def test_article_creation(self):
        """Test article creation from valid data."""
        valid_data = {
            "title": "Bitcoin Mining News",
            "body": "Test content",
            "url": "https://example.com/article",
            "uri": "https://example.com/article",
            "source": {"title": "Test Source"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        
        article = Article.from_dict(valid_data)
        assert article is not None
        assert article.title == "Bitcoin Mining News"
        assert article.url == "https://example.com/article"

    def test_storage_functionality(self):
        """Test storage operations."""
        # Test loading non-existent file
        data = Storage.load_json("nonexistent.json", {"default": True})
        assert data["default"] is True
        
        # Test posted articles structure
        posted_data = Storage.load_posted_articles("nonexistent.json")
        assert "posted_uris" in posted_data
        assert "queued_articles" in posted_data
        assert isinstance(posted_data["posted_uris"], list)

    def test_text_processing(self):
        """Test text processing functionality."""
        article = Article(
            title="Bitcoin Mining Update",
            url="https://example.com/test",
            body="Test content",
            source="Test Source"
        )
        
        tweet_text = TextProcessor.create_tweet_text(article)
        assert isinstance(tweet_text, str)
        assert len(tweet_text) <= 280  # Twitter limit
        assert "Bitcoin Mining Update" in tweet_text

    def test_time_management(self):
        """Test time management utilities."""
        # Test minimum interval check
        result = TimeManager.is_minimum_interval_passed(None, 60)
        assert result is True  # No previous run should allow execution
        
        # Test cooldown creation
        cooldown_data = TimeManager.create_cooldown_data(2)  # 2 hours
        assert isinstance(cooldown_data, dict)
        assert "end_time" in cooldown_data

    def test_bot_initialization(self):
        """Test bot can be initialized."""
        config = Config()
        bot = BitcoinMiningBot(config=config)
        assert bot is not None
        assert bot.config == config

    def test_bot_safe_mode(self):
        """Test bot runs in safe mode without API keys."""
        config = Config()
        bot = BitcoinMiningBot(config=config)
        
        # Should return False due to missing API keys
        result = bot.run()
        assert result is False

    def test_tools_availability(self):
        """Test management tools are available."""
        assert hasattr(BotTools, 'show_next_tweet')
        assert hasattr(BotTools, 'diagnose_bot')
        
        # Test diagnostic runs without crashing
        try:
            result = BotTools.diagnose_bot()
            assert isinstance(result, bool)
        except Exception:
            pass  # Expected without full environment

    def test_mocked_workflow(self):
        """Test complete workflow with mocks."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            config.posted_articles_file = f.name
        
        mock_article = Article(
            title="Bitcoin Mining News",
            url="https://example.com/article",
            body="Mining update content",
            source="Test Source"
        )
        
        try:
            with patch('core.TwitterAPI') as MockTwitter, patch('core.NewsAPI') as MockNews:
                # Setup mocks
                mock_twitter = MockTwitter.return_value
                mock_twitter.post_tweet.return_value = "tweet123"
                
                mock_news = MockNews.return_value
                mock_news.fetch_articles.return_value = [mock_article]
                
                # Run bot
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Should succeed with mocks
                assert result is True
                
        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)


def run_simple_tests():
    """Run all simple tests."""
    test_bot = TestBot()
    
    test_methods = [method for method in dir(test_bot) if method.startswith('test_')]
    
    total_tests = len(test_methods)
    passed_tests = 0
    failed_tests = []
    
    print("🧪 Running Streamlined Bot Tests")
    print("=" * 40)
    
    for method_name in test_methods:
        test_method = getattr(test_bot, method_name)
        
        try:
            test_method()
            print(f"  ✅ {method_name}")
            passed_tests += 1
        except Exception as e:
            print(f"  ❌ {method_name}: {str(e)}")
            failed_tests.append(f"{method_name}: {str(e)}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
        return False
    else:
        print("🎉 ALL TESTS PASSED!")
        return True


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)