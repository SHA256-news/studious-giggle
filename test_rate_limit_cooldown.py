#!/usr/bin/env python3
"""
Test script for rate limit cooldown functionality
"""

import os
import json
import tempfile
import unittest.mock as mock
from datetime import datetime, timedelta


def test_rate_limit_cooldown():
    """Test that rate limit cooldown prevents automation runs for 1 hour"""
    print("Testing rate limit cooldown functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory to avoid polluting the real directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            with mock.patch.dict(os.environ, {
                'TWITTER_API_KEY': 'test_key',
                'TWITTER_API_SECRET': 'test_secret',
                'TWITTER_ACCESS_TOKEN': 'test_token',
                'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
                'EVENTREGISTRY_API_KEY': 'test_er_key'
            }):
                with mock.patch('tweepy.Client'), \
                     mock.patch('eventregistry.EventRegistry'):
                    
                    # Mock the posted_articles.json file
                    with open("posted_articles.json", "w") as f:
                        json.dump({"posted_uris": []}, f)
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Test 1: No cooldown file exists - should not be in cooldown
                    assert not bot._is_rate_limit_cooldown_active(), "Should not be in cooldown when no file exists"
                    print("✓ No cooldown when file doesn't exist")
                    
                    # Test 2: Set cooldown and verify it's active
                    bot._set_rate_limit_cooldown()
                    assert bot._is_rate_limit_cooldown_active(), "Should be in cooldown after setting it"
                    print("✓ Cooldown active after setting")
                    
                    # Test 3: Verify cooldown file structure
                    assert os.path.exists(bot.rate_limit_cooldown_file), "Cooldown file should exist"
                    with open(bot.rate_limit_cooldown_file, "r") as f:
                        cooldown_data = json.load(f)
                        assert "cooldown_until" in cooldown_data, "Cooldown file should contain cooldown_until"
                        assert "reason" in cooldown_data, "Cooldown file should contain reason"
                        assert "created_at" in cooldown_data, "Cooldown file should contain created_at"
                    print("✓ Cooldown file has correct structure")
                    
                    # Test 4: Test expired cooldown (simulate past time)
                    past_time = datetime.now() - timedelta(hours=2)
                    expired_cooldown = {
                        "cooldown_until": past_time.isoformat(),
                        "reason": "Twitter API rate limit exceeded",
                        "created_at": past_time.isoformat()
                    }
                    with open(bot.rate_limit_cooldown_file, "w") as f:
                        json.dump(expired_cooldown, f)
                    
                    assert not bot._is_rate_limit_cooldown_active(), "Should not be in cooldown when time has passed"
                    assert not os.path.exists(bot.rate_limit_cooldown_file), "Expired cooldown file should be removed"
                    print("✓ Expired cooldown file removed correctly")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


def test_rate_limit_integration():
    """Test that rate limiting in _post_with_retry triggers cooldown"""
    print("Testing rate limit integration with posting...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            with mock.patch.dict(os.environ, {
                'TWITTER_API_KEY': 'test_key',
                'TWITTER_API_SECRET': 'test_secret',
                'TWITTER_ACCESS_TOKEN': 'test_token',
                'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
                'EVENTREGISTRY_API_KEY': 'test_er_key'
            }):
                # Mock the posted_articles.json file
                with open("posted_articles.json", "w") as f:
                    json.dump({"posted_uris": []}, f)
                
                # Mock Twitter client to simulate rate limiting properly
                mock_twitter_client = mock.Mock()
                
                with mock.patch('tweepy.Client', return_value=mock_twitter_client), \
                     mock.patch('eventregistry.EventRegistry'):
                    
                    from bot import BitcoinMiningNewsBot
                    
                    bot = BitcoinMiningNewsBot()
                    
                    # Create a custom exception that will be detected as rate limiting
                    class MockTooManyRequests(Exception):
                        def __init__(self, message="TooManyRequests"):
                            super().__init__(message)
                            self.response = mock.Mock()
                            self.response.status_code = 429
                    
                    # Set up rate limit exception mock
                    def mock_create_tweet_rate_limited(*args, **kwargs):
                        raise MockTooManyRequests("TooManyRequests")
                    
                    bot.twitter_client.create_tweet = mock_create_tweet_rate_limited
                    
                    # Test article
                    test_article = {
                        "title": "Test Bitcoin Mining Article",
                        "url": "https://example.com/test",
                        "uri": "test-uri-123"
                    }
                    
                    # This should trigger rate limiting after max_retries and set cooldown
                    result = bot._post_with_retry(test_article, max_retries=1)  # Use fewer retries for faster test
                    
                    assert result is None, "Should return None when rate limited"
                    assert os.path.exists(bot.rate_limit_cooldown_file), "Cooldown file should be created after rate limiting"
                    assert bot._is_rate_limit_cooldown_active(), "Should be in cooldown after rate limiting"
                    print("✓ Rate limiting triggers cooldown correctly")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


def test_run_with_cooldown():
    """Test that bot.run() respects cooldown period"""
    print("Testing that run() respects cooldown period...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            with mock.patch.dict(os.environ, {
                'TWITTER_API_KEY': 'test_key',
                'TWITTER_API_SECRET': 'test_secret',
                'TWITTER_ACCESS_TOKEN': 'test_token',
                'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
                'EVENTREGISTRY_API_KEY': 'test_er_key'
            }):
                with mock.patch('tweepy.Client'), \
                     mock.patch('eventregistry.EventRegistry'):
                    
                    # Mock the posted_articles.json file
                    with open("posted_articles.json", "w") as f:
                        json.dump({"posted_uris": []}, f)
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Set cooldown manually
                    bot._set_rate_limit_cooldown()
                    
                    # Mock fetch_bitcoin_mining_articles to ensure it's not called during cooldown
                    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles') as mock_fetch:
                        bot.run()
                        
                        # fetch_bitcoin_mining_articles should not have been called due to cooldown
                        mock_fetch.assert_not_called()
                        print("✓ Bot run skipped due to active cooldown")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("🔍 Testing rate limit cooldown functionality")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_rate_limit_cooldown()
        success &= test_rate_limit_integration() 
        success &= test_run_with_cooldown()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All rate limit cooldown tests passed!")
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)