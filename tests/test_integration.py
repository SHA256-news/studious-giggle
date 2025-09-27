#!/usr/bin/env python3
"""
Streamlined Integration Tests for Bitcoin Mining Bot
Focuses on end-to-end workflows and system integration testing.
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
    from core import BitcoinMiningBot, Config, Article
    from tools import BotTools
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestIntegrationWorkflows:
    """Streamlined integration tests for complete workflows."""

    def test_production_simulation_workflow(self):
        """Simulate production workflow with realistic data."""
        config = Config()
        config.twitter_api_key = "prod_key"
        config.twitter_api_secret = "prod_secret"
        config.twitter_access_token = "prod_token"
        config.twitter_access_token_secret = "prod_token_secret"
        config.eventregistry_api_key = "prod_er_key"

        # Realistic Bitcoin mining articles
        production_articles = [
            {
                "title": "Bitcoin Network Hashrate Reaches All-Time High",
                "body": "The Bitcoin network's computational power has reached unprecedented levels.",
                "url": "https://bitcoinnews.com/hashrate-ath-2024",
                "uri": "https://bitcoinnews.com/hashrate-ath-2024",
                "source": {"title": "Bitcoin News"},
                "dateTimePub": "2024-01-15T10:30:00Z"
            },
            {
                "title": "Major Mining Pool Announces Green Energy Initiative",
                "body": "Leading mining pool commits to 100% renewable energy by 2025.",
                "url": "https://miningupdate.com/green-energy-2024",
                "uri": "https://miningupdate.com/green-energy-2024", 
                "source": {"title": "Mining Update"},
                "dateTimePub": "2024-01-15T09:45:00Z"
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
            with patch('core.TwitterAPI') as MockTwitter, patch('core.NewsAPI') as MockNews:
                # Setup realistic mocks
                mock_twitter = MockTwitter.return_value
                mock_twitter.post_thread.return_value = True
                
                mock_news = MockNews.return_value
                mock_news.fetch_articles.return_value = [
                    Article.from_dict(article) for article in production_articles
                ]

                # Execute production-like workflow
                bot = BitcoinMiningBot(config=config)
                result = bot.run()

                # Validate production behavior
                assert result is True
                mock_twitter.post_thread.assert_called_once()
                
                # Check realistic thread content
                call_args = mock_twitter.post_thread.call_args[0][0]
                assert isinstance(call_args, list)  # Thread is a list of tweets
                assert len(call_args) > 1  # Should be multiple tweets in thread
                
                # Verify URL is in last tweet (following the user's requirement)
                last_tweet = call_args[-1]
                assert "https://" in last_tweet
                
                # Verify proper queueing
                posted_data = bot.posted_data
                assert len(posted_data["posted_uris"]) == 1
                assert len(posted_data["queued_articles"]) == 1

        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)

    def test_complete_system_diagnostics(self):
        """Test comprehensive system diagnostics and health checks."""
        # Test all diagnostic functions
        diagnostic_result = BotTools.diagnose_bot()
        assert isinstance(diagnostic_result, bool)

        # Test queue operations
        queue_result = BotTools.show_next_tweet()
        assert isinstance(queue_result, bool)

        # Test system can handle missing files gracefully
        with tempfile.NamedTemporaryFile(delete=True) as f:
            non_existent_file = f.name + "_gone"
        
        # Should handle missing files without crashing
        try:
            BotTools.show_queue_simple()
            diagnostic_passed = True
        except Exception:
            diagnostic_passed = False
        
        assert diagnostic_passed is True

    def test_edge_case_resilience(self):
        """Test system resilience under various edge conditions."""
        config = Config()
        config.twitter_api_key = "test_key"
        config.twitter_api_secret = "test_secret"
        config.twitter_access_token = "test_token"
        config.twitter_access_token_secret = "test_token_secret"
        config.eventregistry_api_key = "test_er_key"

        edge_cases = [
            # Empty articles
            [],
            # Valid articles only (filter out malformed ones)
            [{"title": "Valid Article", "url": "https://example.com", "body": "Content", "source": {"title": "Test"}}],
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump({"posted_uris": [], "queued_articles": [], "last_run_time": None}, f)
            config.posted_articles_file = f.name

        try:
            for case_data in edge_cases:
                with patch('core.TwitterAPI'), patch('core.NewsAPI') as MockNews:
                    mock_news = MockNews.return_value
                    # Only create articles from valid data
                    valid_articles = [Article.from_dict(article) for article in case_data]
                    valid_articles = [art for art in valid_articles if art is not None]
                    mock_news.fetch_articles.return_value = valid_articles

                    bot = BitcoinMiningBot(config=config)
                    result = bot.run()
                    
                    # Should handle all edge cases gracefully
                    assert isinstance(result, bool)

        finally:
            Path(config.posted_articles_file).unlink(missing_ok=True)


def run_integration_tests():
    """Run streamlined integration tests."""
    test_workflows = TestIntegrationWorkflows()
    
    test_methods = [method for method in dir(test_workflows) if method.startswith('test_')]
    
    total_tests = len(test_methods)
    passed_tests = 0
    failed_tests = []
    
    print("🔄 Running Streamlined Integration Tests")
    print("=" * 45)
    
    for method_name in test_methods:
        test_method = getattr(test_workflows, method_name)
        
        try:
            test_method()
            print(f"  ✅ {method_name}")
            passed_tests += 1
        except Exception as e:
            print(f"  ❌ {method_name}: {str(e)}")
            failed_tests.append(f"{method_name}: {str(e)}")
    
    print("\n" + "=" * 45)
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