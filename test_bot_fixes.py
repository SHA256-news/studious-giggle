#!/usr/bin/env python3
"""
Test script to verify bug fixes in the Bitcoin Mining News Bot
"""

import os
import unittest.mock as mock


def test_none_handling():
    """Test that None values are handled properly"""
    print("Testing None value handling...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Test None title
            none_article = {"title": None, "url": "https://example.com", "uri": "test-uri"}
            tweet_text = bot.create_tweet_text(none_article)
            assert isinstance(tweet_text, str), "Tweet text should be a string"
            assert len(tweet_text) <= 280, f"Tweet text too long: {len(tweet_text)} chars"
            print("✓ None title handled correctly")
            
            # Test empty article
            empty_article = {}
            tweet_text = bot.create_tweet_text(empty_article)
            assert isinstance(tweet_text, str), "Tweet text should be a string"
            print("✓ Empty article handled correctly")
            
            return True


def test_uri_validation():
    """Test that None URIs are handled in the run method"""
    print("Testing URI validation...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Mock fetch_bitcoin_mining_articles to return articles with None URI
            test_articles = [
                {"title": "Valid Article", "uri": None, "url": "https://example.com"},
                {"title": "Another Article", "uri": "valid-uri", "url": "https://example2.com"}
            ]
            
            with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=test_articles), \
                 mock.patch.object(bot, 'post_to_twitter', return_value="tweet-id"), \
                 mock.patch.object(bot, '_save_posted_articles'):
                
                # This should not crash due to None URI
                bot.run()
                print("✓ None URI handled correctly in run method")
                
            return True


def test_tweet_length():
    """Test that tweets don't exceed character limits"""
    print("Testing tweet length limits...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client'), \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Test very long title
            long_article = {
                "title": "Bitcoin Mining " * 50,  # Very long title
                "uri": "test-uri",
                "url": "https://example.com"
            }
            
            tweet_text = bot.create_tweet_text(long_article)
            assert len(tweet_text) <= 280, f"Tweet too long: {len(tweet_text)} chars"
            print(f"✓ Long title truncated to {len(tweet_text)} chars")
            
            return True


if __name__ == "__main__":
    success = True
    success &= test_none_handling()
    success &= test_uri_validation()
    success &= test_tweet_length()
    
    if success:
        print("\n✓ All bug fix tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)