#!/usr/bin/env python3
"""
Test runtime logging functionality
"""

import sys
import os
import tempfile
import json
from unittest import mock

def test_runtime_logger():
    """Test the runtime logger functionality"""
    print("Testing RuntimeLogger...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Import the runtime logger
        from runtime_logger import RuntimeLogger
        
        # Initialize logger with temp directory
        logger = RuntimeLogger(logs_dir=temp_dir)
        
        # Test logging various types of blocked content
        test_article = {
            "title": "Test Bitcoin Mining Article",
            "url": "https://example.com/test",
            "uri": "test-123",
            "source": {"title": "Test Source"}
        }
        
        # Test crypto filtering log
        logger.log_blocked_article(
            test_article, 
            "crypto_filter", 
            {"unwanted_cryptos_found": ["ethereum", "ripple"]}
        )
        
        # Test rate limiting log
        logger.log_rate_limited_article(test_article)
        
        # Test duplicate log
        logger.log_duplicate_article(test_article)
        
        # Test failed post log
        logger.log_failed_post(test_article, "Twitter API error")
        
        # Finalize logs
        blocked_count = logger.finalize_logs()
        
        # Verify files were created
        blocked_jsonl_path = os.path.join(temp_dir, "blocked.jsonl")
        blocked_md_path = os.path.join(temp_dir, "blocked.md")
        
        assert os.path.exists(blocked_jsonl_path), "blocked.jsonl should be created"
        assert os.path.exists(blocked_md_path), "blocked.md should be created"
        
        # Verify JSONL content
        with open(blocked_jsonl_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 4, f"Expected 4 lines in JSONL, got {len(lines)}"
            
            # Parse each line as JSON
            for line in lines:
                entry = json.loads(line.strip())
                assert "timestamp" in entry
                assert "reason" in entry
                assert "title" in entry
        
        # Verify markdown content
        with open(blocked_md_path, 'r') as f:
            content = f.read()
            assert "# Runtime Logs Summary" in content
            assert "**Total Blocked Articles:** 4" in content
            assert "Crypto Filter" in content
            assert "Rate Limit" in content
            
        print("✓ RuntimeLogger test passed")
        print(f"  - Logged {blocked_count} blocked items")
        print(f"  - Created JSONL file: {blocked_jsonl_path}")
        print(f"  - Created markdown summary: {blocked_md_path}")
        
        return True

def test_bot_integration():
    """Test runtime logger integration with bot"""
    print("Testing bot integration...")
    
    # Mock environment variables
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with mock.patch.dict(os.environ, env_vars):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')) as mock_file:
            
            # Create temporary directory for runtime logs
            with tempfile.TemporaryDirectory() as temp_dir:
                # Patch RuntimeLogger to use temp directory
                with mock.patch('runtime_logger.RuntimeLogger') as MockRuntimeLogger:
                    mock_logger = mock.Mock()
                    MockRuntimeLogger.return_value = mock_logger
                    
                    from bot import BitcoinMiningNewsBot
                    
                    # Initialize bot
                    bot = BitcoinMiningNewsBot()
                    
                    # Verify runtime logger was initialized
                    MockRuntimeLogger.assert_called_once()
                    
                    # Verify the bot has the runtime logger
                    assert hasattr(bot, 'runtime_logger')
                    
                    print("✓ Bot integration test passed")
                    print("  - RuntimeLogger properly integrated into bot")
                    print("  - Bot initialization includes runtime logging")
                    
                    return True

if __name__ == "__main__":
    try:
        success = True
        success &= test_runtime_logger()
        success &= test_bot_integration()
        
        if success:
            print("\n✅ All runtime logging tests passed!")
        else:
            print("\n❌ Some runtime logging tests failed!")
            sys.exit(1)
            
    except Exception as e:
        import traceback
        print(f"\n❌ Runtime logging test failed with error: {e}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)