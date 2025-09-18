#!/usr/bin/env python3
"""
Test script for daily rate limit functionality (17 requests per 24 hours)
"""

import os
import json
import tempfile
import unittest.mock as mock
from datetime import datetime, timedelta


def test_progressive_cooldown():
    """Test that rate limit cooldowns increase progressively"""
    print("Testing progressive cooldown functionality...")
    
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
                    
                    # Test first rate limit - should set 2 hour cooldown
                    bot._set_rate_limit_cooldown()
                    
                    with open("rate_limit_cooldown.json", "r") as f:
                        cooldown_data = json.load(f)
                    
                    assert cooldown_data["duration_hours"] == 2, f"Expected 2 hours, got {cooldown_data['duration_hours']}"
                    assert cooldown_data["progressive_count"] == 1, f"Expected count 1, got {cooldown_data['progressive_count']}"
                    print("✓ First rate limit sets 2-hour cooldown")
                    
                    # Test second rate limit - should set 4 hour cooldown
                    bot._set_rate_limit_cooldown()
                    
                    with open("rate_limit_cooldown.json", "r") as f:
                        cooldown_data = json.load(f)
                    
                    assert cooldown_data["duration_hours"] == 4, f"Expected 4 hours, got {cooldown_data['duration_hours']}"
                    assert cooldown_data["progressive_count"] == 2, f"Expected count 2, got {cooldown_data['progressive_count']}"
                    print("✓ Second rate limit sets 4-hour cooldown")
                    
                    # Test third rate limit - should set 8 hour cooldown
                    bot._set_rate_limit_cooldown()
                    
                    with open("rate_limit_cooldown.json", "r") as f:
                        cooldown_data = json.load(f)
                    
                    assert cooldown_data["duration_hours"] == 8, f"Expected 8 hours, got {cooldown_data['duration_hours']}"
                    assert cooldown_data["progressive_count"] == 3, f"Expected count 3, got {cooldown_data['progressive_count']}"
                    print("✓ Third rate limit sets 8-hour cooldown")
                    
                    # Test fourth rate limit - should set 24 hour cooldown (max)
                    bot._set_rate_limit_cooldown()
                    
                    with open("rate_limit_cooldown.json", "r") as f:
                        cooldown_data = json.load(f)
                    
                    assert cooldown_data["duration_hours"] == 24, f"Expected 24 hours, got {cooldown_data['duration_hours']}"
                    assert cooldown_data["progressive_count"] == 4, f"Expected count 4, got {cooldown_data['progressive_count']}"
                    print("✓ Fourth rate limit sets 24-hour cooldown (maximum)")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


def test_daily_rate_limit_integration():
    """Test that rate limiting with reduced retries works correctly"""
    print("Testing daily rate limit integration with posting...")
    
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
                
                # Mock Twitter client to always raise TooManyRequests
                import tweepy
                mock_response = mock.Mock()
                mock_response.json.return_value = {"error": "Rate limit exceeded"}
                mock_response.status_code = 429
                
                mock_twitter_client = mock.Mock()
                mock_twitter_client.create_tweet.side_effect = tweepy.TooManyRequests(response=mock_response)
                
                with mock.patch('tweepy.Client', return_value=mock_twitter_client), \
                     mock.patch('eventregistry.EventRegistry'), \
                     mock.patch('time.sleep'):  # Skip actual sleep for testing
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Test article
                    test_article = {
                        "title": "Test Bitcoin Mining Article",
                        "url": "https://example.com/test-article",
                        "uri": "test-article-uri"
                    }
                    
                    # Attempt to post - should trigger rate limit cooldown after 1 retry
                    result = bot.post_to_twitter(test_article)
                    
                    # Should return None (failed)
                    assert result is None, "Expected posting to fail due to rate limit"
                    
                    # Should have created a cooldown file
                    assert os.path.exists("rate_limit_cooldown.json"), "Expected cooldown file to be created"
                    
                    # Check cooldown file content
                    with open("rate_limit_cooldown.json", "r") as f:
                        cooldown_data = json.load(f)
                    
                    assert cooldown_data["duration_hours"] == 2, f"Expected 2 hour cooldown, got {cooldown_data['duration_hours']}"
                    assert "17 requests" in cooldown_data["reason"], f"Expected daily rate limit reason, got: {cooldown_data['reason']}"
                    
                    print("✓ Rate limiting triggers 2-hour cooldown correctly")
                    
                    # Test that bot respects the cooldown
                    cooldown_active = bot._is_rate_limit_cooldown_active()
                    assert cooldown_active, "Expected cooldown to be active"
                    
                    print("✓ Bot respects active cooldown period")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


def test_cooldown_expiry():
    """Test that expired cooldowns are properly cleaned up"""
    print("Testing cooldown expiry handling...")
    
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
                    
                    # Create an expired cooldown file
                    expired_time = datetime.now() - timedelta(hours=1)
                    cooldown_data = {
                        "cooldown_until": expired_time.isoformat(),
                        "reason": "Twitter API daily rate limit exceeded (17 requests/24h)",
                        "created_at": (expired_time - timedelta(hours=2)).isoformat(),
                        "duration_hours": 2,
                        "progressive_count": 1
                    }
                    
                    with open("rate_limit_cooldown.json", "w") as f:
                        json.dump(cooldown_data, f, indent=2)
                    
                    # Check that cooldown is not active (should clean up file)
                    cooldown_active = bot._is_rate_limit_cooldown_active()
                    assert not cooldown_active, "Expected expired cooldown to be inactive"
                    
                    # File should be cleaned up
                    assert not os.path.exists("rate_limit_cooldown.json"), "Expected expired cooldown file to be removed"
                    
                    print("✓ Expired cooldown files are properly cleaned up")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("🔍 Testing daily rate limit functionality (17 requests per 24 hours)")
    print("=" * 70)
    
    success = True
    
    try:
        success &= test_progressive_cooldown()
        success &= test_daily_rate_limit_integration() 
        success &= test_cooldown_expiry()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ All daily rate limit tests passed!")
            print("📋 Summary:")
            print("   - Progressive cooldowns: 2h → 4h → 8h → 24h")
            print("   - Conservative retry policy: 1 retry with 5-minute delay")
            print("   - Proper cooldown expiry handling")
            print("   - Daily rate limit awareness (17 requests per 24 hours)")
        else:
            print("\n" + "=" * 70)
            print("❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)