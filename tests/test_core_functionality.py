#!/usr/bin/env python3
"""
Clean, comprehensive tests for the refactored Bitcoin Mining Bot architecture.
Tests all core functionality with proper mocking and error handling.
"""

import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core import BitcoinMiningBot, Config, Article, Storage, TextProcessor, TimeManager
    from bot import BitcoinMiningNewsBotLegacy, FileManager, TextUtils
    from tools import BotTools
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestConfig:
    """Test configuration management."""
    
    def test_config_creation(self):
        """Test basic config creation."""
        config = Config()
        assert config.max_articles == 20
        assert config.min_interval_minutes == 90
        assert config.cooldown_hours == 2
        
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        missing = config.validate()
        
        # Should have 5 missing required fields
        assert len(missing) == 5
        assert "TWITTER_API_KEY" in missing
        assert "EVENTREGISTRY_API_KEY" in missing
        
    def test_config_from_env(self):
        """Test loading config from environment."""
        with patch.dict(os.environ, {
            'TWITTER_API_KEY': 'test_key',
            'TWITTER_API_SECRET': 'test_secret'
        }):
            config = Config.from_env()
            assert config.twitter_api_key == 'test_key'
            assert config.twitter_api_secret == 'test_secret'


class TestArticle:
    """Test Article data model."""
    
    def test_article_from_dict(self):
        """Test creating article from dictionary."""
        data = {
            "title": "Test Bitcoin Mining Article",
            "body": "This is a test article about Bitcoin mining.",
            "url": "https://example.com/test",
            "source": {"title": "Test Source"}
        }
        
        article = Article.from_dict(data)
        assert article.title == "Test Bitcoin Mining Article"
        assert article.url == "https://example.com/test"
        assert article.source == "Test Source"
        
    def test_article_from_dict_validation(self):
        """Test article validation with missing data."""
        # Missing title
        try:
            Article.from_dict({"url": "https://example.com"})
            assert False, "Should have raised ValueError for missing title"
        except ValueError:
            pass
            
        # Missing URL
        try:
            Article.from_dict({"title": "Test"})
            assert False, "Should have raised ValueError for missing URL"
        except ValueError:
            pass
    
    def test_article_source_extraction(self):
        """Test various source format handling."""
        # Dictionary source
        data1 = {
            "title": "Test", 
            "url": "http://test.com",
            "source": {"title": "News Site"}
        }
        article1 = Article.from_dict(data1)
        assert article1.source == "News Site"
        
        # String source
        data2 = {
            "title": "Test",
            "url": "http://test.com", 
            "source": "Direct Source"
        }
        article2 = Article.from_dict(data2)
        assert article2.source == "Direct Source"
        
        # Missing source
        data3 = {
            "title": "Test",
            "url": "http://test.com"
        }
        article3 = Article.from_dict(data3)
        assert article3.source == "Unknown Source"


class TestStorage:
    """Test storage operations."""
    
    def test_load_json_nonexistent_file(self):
        """Test loading non-existent JSON file."""
        result = Storage.load_json("nonexistent.json", {"default": True})
        assert result == {"default": True}
    
    def test_save_and_load_json(self):
        """Test saving and loading JSON data."""
        test_data = {"test": "data", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Test save
            success = Storage.save_json(temp_file, test_data)
            assert success
            
            # Test load
            loaded_data = Storage.load_json(temp_file)
            assert loaded_data == test_data
            
        finally:
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)
    
    def test_load_posted_articles_structure(self):
        """Test posted articles data structure."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": ["http://example.com/1"],
                "queued_articles": [],
                "last_run_time": "2024-01-01T12:00:00"
            }, f)
            temp_file = f.name
        
        try:
            data = Storage.load_posted_articles(temp_file)
            assert "posted_uris" in data
            assert "queued_articles" in data
            assert "last_run_time" in data
            assert len(data["posted_uris"]) == 1
            
        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestTextProcessor:
    """Test text processing functionality."""
    
    def test_create_tweet_text(self):
        """Test tweet text generation."""
        article = Article(
            title="Bitcoin Mining Difficulty Increases",
            body="Mining difficulty has reached new highs.",
            url="https://example.com/mining-news"
        )
        
        tweet_text = TextProcessor.create_tweet_text(article)
        
        # Should contain emoji prefix
        assert any(prefix in tweet_text for prefix in TextProcessor.PREFIXES)
        
        # Should contain URL
        assert "https://example.com/mining-news" in tweet_text
        
        # Should be within Twitter limits
        assert len(tweet_text) <= 280
    
    def test_clean_title(self):
        """Test title cleaning functionality."""
        # Test removing common prefixes
        clean_title = TextProcessor._clean_title("BREAKING: Bitcoin Mining News")
        assert clean_title == "Bitcoin Mining News"
        
        clean_title = TextProcessor._clean_title("News: Important Update")
        assert clean_title == "Important Update"
        
        # Test whitespace cleanup
        clean_title = TextProcessor._clean_title("  Multiple   Spaces  ")
        assert clean_title == "Multiple Spaces"


class TestTimeManager:
    """Test time-related utilities."""
    
    def test_minimum_interval_check(self):
        """Test minimum interval validation."""
        # No previous run time
        assert TimeManager.is_minimum_interval_passed(None, 90)
        
        # Recent run (should fail)
        recent_time = (datetime.now() - timedelta(minutes=30)).isoformat()
        assert not TimeManager.is_minimum_interval_passed(recent_time, 90)
        
        # Old run (should pass)
        old_time = (datetime.now() - timedelta(minutes=120)).isoformat()
        assert TimeManager.is_minimum_interval_passed(old_time, 90)
    
    def test_cooldown_management(self):
        """Test cooldown creation and validation."""
        # Create cooldown
        cooldown_data = TimeManager.create_cooldown_data(2)
        assert "cooldown_start" in cooldown_data
        assert "cooldown_end" in cooldown_data
        assert cooldown_data["cooldown_hours"] == 2
        
        # Should be active immediately
        assert TimeManager.is_cooldown_active(cooldown_data)
        
        # Test expired cooldown
        expired_cooldown = {
            "cooldown_end": (datetime.now() - timedelta(hours=1)).isoformat()
        }
        assert not TimeManager.is_cooldown_active(expired_cooldown)


class TestBitcoinMiningBot:
    """Test main bot functionality."""
    
    @patch('core.TwitterAPI')
    @patch('core.NewsAPI')
    def test_bot_initialization(self, mock_news_api, mock_twitter_api):
        """Test bot initialization."""
        config = Config()
        bot = BitcoinMiningBot(config=config)
        
        assert bot.config == config
        assert bot.storage is not None
        assert isinstance(bot.posted_data, dict)
    
    def test_bot_safe_mode(self):
        """Test bot in safe mode."""
        bot = BitcoinMiningBot(safe_mode=True)
        result = bot.run()
        
        # Should return False due to missing API keys in safe mode
        assert not result


class TestLegacyCompatibility:
    """Test backward compatibility layer."""
    
    def test_legacy_bot_initialization(self):
        """Test legacy bot wrapper."""
        bot = BitcoinMiningNewsBotLegacy(safe_mode=True)
        
        # Should have legacy properties
        assert hasattr(bot, 'posted_articles')
        assert hasattr(bot, 'rate_limit_cooldown_file')
        assert hasattr(bot, 'skip_gemini_analysis')
    
    def test_legacy_methods_exist(self):
        """Test that legacy methods are available."""
        bot = BitcoinMiningNewsBotLegacy(safe_mode=True)
        
        # Test method availability
        assert hasattr(bot, 'fetch_bitcoin_mining_articles')
        assert hasattr(bot, 'create_tweet_text')
        assert hasattr(bot, 'post_to_twitter')
        assert hasattr(bot, '_save_posted_articles')
    
    def test_file_manager_compatibility(self):
        """Test FileManager legacy interface."""
        # Should not crash
        try:
            FileManager.load_posted_articles()
            FileManager.load_rate_limit_cooldown()
        except Exception as e:
            # File not found is OK, other errors are not
            if "No such file" not in str(e):
                raise
    
    def test_text_utils_compatibility(self):
        """Test TextUtils legacy interface."""
        test_article = {
            "title": "Test Article",
            "url": "https://example.com",
            "body": "Test content"
        }
        
        # Should not crash
        tweet_text = TextUtils.create_tweet_text(test_article)
        assert isinstance(tweet_text, str)
        assert len(tweet_text) > 0


class TestToolsFunctionality:
    """Test tools module functionality."""
    
    def test_bot_tools_methods_exist(self):
        """Test that BotTools methods exist."""
        assert hasattr(BotTools, 'show_next_tweet')
        assert hasattr(BotTools, 'show_queue_simple')
        assert hasattr(BotTools, 'clean_queue')
        assert hasattr(BotTools, 'diagnose_bot')


def run_all_tests():
    """Run all tests and report results."""
    test_classes = [
        TestConfig, TestArticle, TestStorage, TestTextProcessor,
        TestTimeManager, TestBitcoinMiningBot, TestLegacyCompatibility,
        TestToolsFunctionality
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    print("🧪 Running Comprehensive Bot Tests")
    print("=" * 50)
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n📋 {class_name}")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_instance, method_name)
            
            try:
                test_method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {str(e)}")
                failed_tests.append(f"{class_name}.{method_name}: {str(e)}")
    
    print("\n" + "=" * 50)
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
    success = run_all_tests()
    sys.exit(0 if success else 1)