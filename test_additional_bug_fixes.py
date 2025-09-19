#!/usr/bin/env python3
"""
Test script for additional bug fixes found during analysis
"""

import os
import unittest.mock as mock
import tempfile


def test_logger_import_error_fix():
    """Test that logger is defined before image import to prevent NameError"""
    print("Testing logger import error fix...")
    
    # Save original file
    if os.path.exists('image_selector.py'):
        os.rename('image_selector.py', 'image_selector.py.temp')
    
    try:
        # This should not crash with NameError anymore
        import bot
        print("✓ Logger import error fix working - no NameError on import failure")
        return True
    except NameError as e:
        if "logger" in str(e):
            print(f"✗ Logger import error bug still exists: {e}")
            return False
        else:
            # Different NameError, re-raise
            raise
    except ImportError:
        # ImportError is expected since we removed image_selector
        print("✓ Logger import error fix working - ImportError handled gracefully")
        return True
    finally:
        # Restore file
        if os.path.exists('image_selector.py.temp'):
            os.rename('image_selector.py.temp', 'image_selector.py')


def test_none_uri_tracking_fix():
    """Test that None URIs are not added to posted_uris list"""
    print("Testing None URI tracking fix...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')):
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Test the run method with an article that has None URI
            test_articles = [
                {"title": "Valid Article", "uri": "valid-uri", "url": "https://example.com"},
                {"title": "Invalid Article", "uri": None, "url": "https://example2.com"}
            ]
            
            with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=test_articles), \
                 mock.patch.object(bot, 'post_to_twitter', return_value="tweet-id"), \
                 mock.patch.object(bot, '_save_posted_articles'):
                
                # Run the bot
                bot.run()
                
                # Check that None is not in posted_uris
                if None in bot.posted_articles["posted_uris"]:
                    print("✗ None URI tracking bug still exists")
                    return False
                else:
                    print("✓ None URI tracking fix working - None not added to posted_uris")
                    return True


def test_comprehensive_edge_cases():
    """Test various edge cases that could cause bugs"""
    print("Testing comprehensive edge cases...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')):
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Test edge cases in create_tweet_text
            edge_cases = [
                {},  # Empty dict
                {"title": None},  # None title
                {"title": ""},  # Empty title
                {"title": " "},  # Whitespace only title
                {"title": "Bitcoin Mining " * 100},  # Very long title
            ]
            
            for i, article in enumerate(edge_cases):
                try:
                    tweet_text = bot.create_tweet_text(article)
                    if not isinstance(tweet_text, str):
                        print(f"✗ Edge case {i+1} failed: not a string")
                        return False
                    if len(tweet_text) > 280:
                        print(f"✗ Edge case {i+1} failed: tweet too long ({len(tweet_text)} chars)")
                        return False
                except Exception as e:
                    print(f"✗ Edge case {i+1} failed with exception: {e}")
                    return False
            
            print("✓ All edge cases handled correctly")
            return True


if __name__ == "__main__":
    success = True
    success &= test_logger_import_error_fix()
    success &= test_none_uri_tracking_fix()
    success &= test_comprehensive_edge_cases()
    
    if success:
        print("\n✅ All additional bug fix tests passed!")
    else:
        print("\n❌ Some additional bug fix tests failed!")
        exit(1)