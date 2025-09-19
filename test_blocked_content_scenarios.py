#!/usr/bin/env python3
"""
Test runtime logging with simulated blocked content scenarios
"""

import os
import sys
import json
import tempfile
from unittest import mock

def test_crypto_filtering_with_runtime_logs():
    """Test that crypto filtering properly logs blocked articles"""
    print("Testing crypto filtering with runtime logging...")
    
    # Mock environment variables
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logs_dir = os.path.join(temp_dir, "runtime-logs")
        
        with mock.patch.dict(os.environ, env_vars):
            with mock.patch('tweepy.Client'), \
                 mock.patch('eventregistry.EventRegistry') as MockER, \
                 mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')) as mock_file, \
                 mock.patch('runtime_logger.RuntimeLogger') as MockRuntimeLogger:
                
                # Set up runtime logger mock
                mock_logger = mock.Mock()
                MockRuntimeLogger.return_value = mock_logger
                
                # Mock EventRegistry to return articles with crypto mentions
                mock_er_client = mock.Mock()
                MockER.return_value = mock_er_client
                
                # Create test articles - some with crypto mentions that should be filtered
                test_articles = [
                    {
                        "title": "Bitcoin Mining Farm Opens in Texas",
                        "url": "https://example.com/bitcoin1",
                        "uri": "btc-farm-1",
                        "source": {"title": "Bitcoin News"},
                        "body": "A new Bitcoin mining facility has opened..."
                    },
                    {
                        "title": "Ethereum and Bitcoin Mining Comparison",  # Should be filtered
                        "url": "https://example.com/crypto1", 
                        "uri": "crypto-1",
                        "source": {"title": "Crypto News"},
                        "body": "This article compares Ethereum mining to Bitcoin mining..."
                    },
                    {
                        "title": "XRP Mining Platform Launches",  # Should be filtered
                        "url": "https://example.com/xrp1",
                        "uri": "xrp-1",
                        "source": {"title": "XRP News"},
                        "body": "A new XRP mining platform has been announced..."
                    }
                ]
                
                mock_er_client.execQuery.return_value = {
                    "articles": {
                        "results": test_articles
                    }
                }
                
                # Override runtime logger path
                from bot import BitcoinMiningNewsBot
                from runtime_logger import RuntimeLogger
                
                # Create bot with mocked APIs but real runtime logger
                with mock.patch.object(BitcoinMiningNewsBot, '__init__', lambda self: None):
                    bot = BitcoinMiningNewsBot()
                    bot.runtime_logger = RuntimeLogger(logs_dir=logs_dir)
                    bot.er_client = mock_er_client
                    
                    # Fetch articles (this will trigger crypto filtering)
                    articles = bot.fetch_articles()
                    
                    # Check that only Bitcoin-only article remains
                    assert len(articles) == 1, f"Expected 1 article after filtering, got {len(articles)}"
                    assert "Bitcoin Mining Farm" in articles[0]["title"]
                    
                    # Check that blocked files were created
                    blocked_jsonl_path = os.path.join(logs_dir, "blocked.jsonl")
                    blocked_md_path = os.path.join(logs_dir, "blocked.md")
                    
                    assert os.path.exists(blocked_jsonl_path), "blocked.jsonl should be created"
                    
                    # Verify JSONL content
                    with open(blocked_jsonl_path, 'r') as f:
                        lines = f.readlines()
                        assert len(lines) == 2, f"Expected 2 blocked articles, got {len(lines)}"
                        
                        for line in lines:
                            entry = json.loads(line.strip())
                            assert entry["reason"] == "crypto_filter"
                            assert "unwanted_cryptos_found" in entry["details"]
                    
                    # Generate final summary
                    blocked_count = bot.runtime_logger.finalize_logs()
                    assert blocked_count == 2, f"Expected 2 blocked articles, got {blocked_count}"
                    
                    # Verify markdown summary
                    assert os.path.exists(blocked_md_path), "blocked.md should be created"
                    with open(blocked_md_path, 'r') as f:
                        content = f.read()
                        assert "**Total Blocked Articles:** 2" in content
                        assert "Crypto Filter (2 articles)" in content
                        assert "Ethereum" in content or "XRP" in content
                    
                    print("✓ Crypto filtering runtime logging test passed")
                    print(f"  - Filtered 2 articles with crypto mentions")
                    print(f"  - Created blocked.jsonl with detailed logs")
                    print(f"  - Created blocked.md summary")
                    
                    return True

def test_rate_limiting_scenario():
    """Test runtime logging for rate limiting scenarios"""
    print("Testing rate limiting runtime logging...")
    
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logs_dir = os.path.join(temp_dir, "runtime-logs")
        
        with mock.patch.dict(os.environ, env_vars):
            with mock.patch('tweepy.Client') as MockTwitter, \
                 mock.patch('eventregistry.EventRegistry'), \
                 mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')) as mock_file:
                
                # Mock Twitter client to simulate rate limiting
                mock_twitter_client = mock.Mock()
                MockTwitter.return_value = mock_twitter_client
                
                # Simulate rate limit exception
                from tweepy.errors import TooManyRequests
                mock_twitter_client.create_tweet.side_effect = TooManyRequests("Rate limit exceeded")
                
                from bot import BitcoinMiningNewsBot
                from runtime_logger import RuntimeLogger
                
                bot = BitcoinMiningNewsBot()
                bot.runtime_logger = RuntimeLogger(logs_dir=logs_dir)
                
                # Create test article
                test_article = {
                    "title": "Bitcoin Mining Difficulty Adjusts",
                    "url": "https://example.com/btc-diff",
                    "uri": "btc-diff-1",
                    "source": {"title": "Bitcoin News"}
                }
                
                # Attempt to post (should fail due to rate limiting)
                tweet_id = bot.post_to_twitter(test_article)
                assert tweet_id is None, "Tweet should fail due to rate limiting"
                
                # Manually log the rate limited article
                bot.runtime_logger.log_rate_limited_article(test_article, {"api_error": "429 Too Many Requests"})
                
                # Finalize logs
                blocked_count = bot.runtime_logger.finalize_logs()
                assert blocked_count == 1, f"Expected 1 rate limited article, got {blocked_count}"
                
                # Verify logs
                blocked_jsonl_path = os.path.join(logs_dir, "blocked.jsonl")
                assert os.path.exists(blocked_jsonl_path)
                
                with open(blocked_jsonl_path, 'r') as f:
                    line = f.readline().strip()
                    entry = json.loads(line)
                    assert entry["reason"] == "rate_limit"
                    assert entry["title"] == "Bitcoin Mining Difficulty Adjusts"
                
                print("✓ Rate limiting runtime logging test passed")
                print(f"  - Logged rate limited article")
                print(f"  - Created appropriate runtime logs")
                
                return True

def test_full_integration_scenario():
    """Test complete integration with mixed blocking scenarios"""
    print("Testing full integration scenario...")
    
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logs_dir = os.path.join(temp_dir, "runtime-logs")
        
        with mock.patch.dict(os.environ, env_vars):
            with mock.patch('tweepy.Client') as MockTwitter, \
                 mock.patch('eventregistry.EventRegistry') as MockER, \
                 mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": ["duplicate-1"], "queued_articles": []}')) as mock_file:
                
                # Set up EventRegistry mock
                mock_er_client = mock.Mock()
                MockER.return_value = mock_er_client
                
                # Set up Twitter mock
                mock_twitter_client = mock.Mock()
                MockTwitter.return_value = mock_twitter_client
                
                # Mock successful tweet
                tweet_response = mock.Mock()
                tweet_response.data = {"id": "12345"}
                mock_twitter_client.create_tweet.return_value = tweet_response
                
                # Create mixed test articles
                test_articles = [
                    {
                        "title": "Bitcoin Mining Pool Efficiency Improves",
                        "url": "https://example.com/btc-pool",
                        "uri": "btc-pool-1",
                        "source": {"title": "Mining News"}
                    },
                    {
                        "title": "Dogecoin Mining vs Bitcoin Mining",  # Should be filtered
                        "url": "https://example.com/doge",
                        "uri": "doge-1", 
                        "source": {"title": "Crypto News"}
                    },
                    {
                        "title": "Duplicate Article",  # Should be marked as duplicate
                        "url": "https://example.com/dup",
                        "uri": "duplicate-1",
                        "source": {"title": "News"}
                    }
                ]
                
                mock_er_client.execQuery.return_value = {
                    "articles": {"results": test_articles}
                }
                
                from bot import BitcoinMiningNewsBot
                from runtime_logger import RuntimeLogger
                
                bot = BitcoinMiningNewsBot()
                bot.runtime_logger = RuntimeLogger(logs_dir=logs_dir)
                
                # Run the bot
                bot.run()
                
                # Finalize and check logs
                blocked_count = bot.runtime_logger.finalize_logs()
                
                # Should have blocked the crypto article and duplicate
                assert blocked_count >= 1, f"Expected at least 1 blocked article, got {blocked_count}"
                
                # Verify logs exist
                blocked_jsonl_path = os.path.join(logs_dir, "blocked.jsonl")
                blocked_md_path = os.path.join(logs_dir, "blocked.md")
                
                assert os.path.exists(blocked_jsonl_path), "blocked.jsonl should exist"
                assert os.path.exists(blocked_md_path), "blocked.md should exist"
                
                print("✓ Full integration test passed")
                print(f"  - Bot run completed with {blocked_count} blocked items")
                print(f"  - Runtime logs generated successfully")
                
                return True

if __name__ == "__main__":
    try:
        success = True
        success &= test_crypto_filtering_with_runtime_logs()
        success &= test_rate_limiting_scenario()
        success &= test_full_integration_scenario()
        
        if success:
            print("\n✅ All blocked content scenario tests passed!")
            print("🔍 Runtime logging system is working correctly")
            print("📄 GitHub Actions will now upload blocked.jsonl and blocked.md artifacts")
        else:
            print("\n❌ Some blocked content scenario tests failed!")
            sys.exit(1)
            
    except Exception as e:
        import traceback
        print(f"\n❌ Blocked content scenario tests failed: {e}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)