#!/usr/bin/env python3
"""
Integration tests for the complete Bitcoin Mining Bot workflow.
Tests end-to-end functionality with proper mocking.
"""

import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core import BitcoinMiningBot, Config, Article
    from bot import BitcoinMiningNewsBotLegacy
    from tools import BotTools
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestBotIntegration:
    """Integration tests for complete bot workflows."""
    
    def test_complete_bot_workflow_with_mocks(self):
        """Test complete bot execution with mocked dependencies."""
        
        # Create test configuration
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret" 
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        # Mock articles data
        mock_articles = [
            {
                "title": "Bitcoin Mining Difficulty Adjustment",
                "body": "Mining difficulty has been adjusted upward.",
                "url": "https://example.com/article1",
                "uri": "https://example.com/article1",
                "source": {"title": "Crypto News"},
                "dateTimePub": "2024-01-01T12:00:00Z"
            },
            {
                "title": "New ASIC Miners Released",
                "body": "Latest generation ASIC miners are now available.",
                "url": "https://example.com/article2", 
                "uri": "https://example.com/article2",
                "source": {"title": "Mining Weekly"},
                "dateTimePub": "2024-01-01T11:00:00Z"
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            config.posted_articles_file = f.name
        
        try:
            # Mock external dependencies
            with patch('core.TwitterAPI') as MockTwitterAPI, \
                 patch('core.NewsAPI') as MockNewsAPI:
                
                # Setup mocks
                mock_twitter = MockTwitterAPI.return_value
                mock_twitter.post_tweet.return_value = "tweet123"
                
                mock_news = MockNewsAPI.return_value
                mock_news.fetch_articles.return_value = [
                    Article.from_dict(article) for article in mock_articles
                ]
                
                # Create bot and run
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Verify success
                assert result is True
                
                # Verify Twitter was called
                mock_twitter.post_tweet.assert_called_once()
                
                # Verify articles were queued
                posted_data = bot.posted_data
                assert len(posted_data["posted_uris"]) == 1
                assert len(posted_data["queued_articles"]) == 1
                
        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)
    
    def test_bot_with_no_new_articles(self):
        """Test bot behavior when no new articles are found."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token" 
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            config.posted_articles_file = f.name
        
        try:
            with patch('core.TwitterAPI'), patch('core.NewsAPI') as MockNewsAPI:
                # Mock no articles found
                mock_news = MockNewsAPI.return_value
                mock_news.fetch_articles.return_value = []
                
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Should still return True (no error)
                assert result is True
                
        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)
    
    def test_bot_with_all_articles_already_posted(self):
        """Test bot behavior when all articles have been posted before."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        # Pre-populate posted articles
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": ["https://example.com/article1"],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            config.posted_articles_file = f.name
        
        mock_article = {
            "title": "Already Posted Article",
            "body": "This article was already posted.",
            "url": "https://example.com/article1",
            "uri": "https://example.com/article1",
            "source": {"title": "Test Source"}
        }
        
        try:
            with patch('core.TwitterAPI'), patch('core.NewsAPI') as MockNewsAPI:
                mock_news = MockNewsAPI.return_value
                mock_news.fetch_articles.return_value = [Article.from_dict(mock_article)]
                
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Should return True but not post anything
                assert result is True
                
        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)
    
    def test_bot_error_handling(self):
        """Test bot error handling with network failures."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            config.posted_articles_file = f.name
        
        try:
            with patch('core.TwitterAPI'), patch('core.NewsAPI') as MockNewsAPI:
                # Mock network error
                mock_news = MockNewsAPI.return_value
                mock_news.fetch_articles.side_effect = Exception("Network error")
                
                bot = BitcoinMiningBot(config=config)
                result = bot.run()
                
                # Should return False due to error
                assert result is False
                
        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)


class TestToolsIntegration:
    """Integration tests for tools functionality."""
    
    def test_tools_with_empty_queue(self):
        """Test tools behavior with empty queue."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }, f)
            temp_file = f.name
        
        try:
            # Mock FileManager to use our temp file
            with patch('bot.FileManager.load_posted_articles') as mock_load:
                mock_load.return_value = {
                    "posted_uris": [],
                    "queued_articles": [],
                    "last_run_time": None
                }
                
                # Test preview with empty queue
                result = BotTools.show_next_tweet()
                assert result is True  # Should handle empty queue gracefully
                
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    def test_diagnostic_functionality(self):
        """Test comprehensive diagnostics."""
        result = BotTools.diagnose_bot()
        
        # Should complete without crashing
        assert isinstance(result, bool)


def run_integration_tests():
    """Run all integration tests."""
    test_classes = [TestBotIntegration, TestToolsIntegration]
    
    total_tests = 0
    passed_tests = 0 
    failed_tests = []
    
    print("🔄 Running Integration Tests")
    print("=" * 40)
    
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
    
    print("\n" + "=" * 40)
    print(f"📊 Integration Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
        return False
    else:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)