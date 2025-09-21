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


def test_second_tweet_failure():
    """Test that first tweet success is returned even if second tweet fails"""
    print("Testing second tweet failure handling...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            
            # Mock Twitter client
            mock_twitter_client = mock.Mock()
            
            # Mock successful first tweet
            first_tweet_response = mock.Mock()
            first_tweet_response.data = {"id": "12345"}
            mock_twitter_client.create_tweet.side_effect = [
                first_tweet_response,  # First tweet succeeds
                Exception("Twitter API Error")  # Second tweet fails
            ]
            
            with mock.patch('tweepy.Client', return_value=mock_twitter_client):
                bot = BitcoinMiningNewsBot()
                
                article = {
                    "title": "Test Bitcoin Mining Article",
                    "uri": "test-uri",
                    "url": "https://example.com/article"
                }
                
                # This should return None with current implementation (bug)
                # but should return the first tweet ID (fix)
                result = bot.post_to_twitter(article)
                
                # Current behavior (bug): returns None
                # Expected behavior (fix): returns "12345"
                if result is None:
                    print("✗ Bug reproduced: second tweet failure causes entire operation to fail")
                    return False
                elif result == "12345":
                    print("✓ Fix working: first tweet ID returned despite second tweet failure")
                    return True
                else:
                    print(f"✗ Unexpected result: {result}")
                    return False


def test_single_tweet_success():
    """Test that single tweet posting works correctly"""
    print("Testing successful single tweet posting...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            
            # Mock Twitter client
            mock_twitter_client = mock.Mock()
            
            # Mock successful tweet
            tweet_response = mock.Mock()
            tweet_response.data = {"id": "12345"}
            
            mock_twitter_client.create_tweet.return_value = tweet_response
            
            with mock.patch('tweepy.Client', return_value=mock_twitter_client):
                bot = BitcoinMiningNewsBot()
                
                article = {
                    "title": "Test Bitcoin Mining Article",
                    "uri": "test-uri",
                    "url": "https://example.com/article"
                }
                
                result = bot.post_to_twitter(article)
                
                if result == "12345":
                    print("✓ Single tweet posted successfully, tweet ID returned")
                    
                    # Verify that create_tweet was called twice (threaded tweet: hook + link)
                    assert mock_twitter_client.create_tweet.call_count == 2, f"Expected 2 calls (threaded tweet), got {mock_twitter_client.create_tweet.call_count}"
                    
                    # Verify the first call (hook tweet) was made correctly
                    first_call = mock_twitter_client.create_tweet.call_args_list[0]
                    # Check that the tweet contains the key content (with possible abbreviations)
                    tweet_text = first_call[1]['text']
                    assert "Test" in tweet_text and ("Bitcoin" in tweet_text or "BTC" in tweet_text) and "Mining" in tweet_text, f"Tweet should contain key elements: {tweet_text}"
                    
                    return True
                else:
                    print(f"✗ Unexpected result: {result}")
                    return False


def test_no_url_article():
    """Test that articles without URLs still work (single tweet posted)"""
    print("Testing article without URL...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            from bot import BitcoinMiningNewsBot
            
            # Mock Twitter client
            mock_twitter_client = mock.Mock()
            
            # Mock successful first tweet
            first_tweet_response = mock.Mock()
            first_tweet_response.data = {"id": "12345"}
            mock_twitter_client.create_tweet.return_value = first_tweet_response
            
            with mock.patch('tweepy.Client', return_value=mock_twitter_client):
                bot = BitcoinMiningNewsBot()
                
                article = {
                    "title": "Test Bitcoin Mining Article"
                    # No URL or URI provided
                }
                
                result = bot.post_to_twitter(article)
                
                if result == "12345":
                    print("✓ Article without URL handled correctly, single tweet posted")
                    
                    # Verify that create_tweet was called only once
                    assert mock_twitter_client.create_tweet.call_count == 1
                    
                    return True
                else:
                    print(f"✗ Unexpected result: {result}")
                    return False


if __name__ == "__main__":
    success = True
    success &= test_none_handling()
    success &= test_uri_validation()
    success &= test_tweet_length()
    success &= test_second_tweet_failure()
    success &= test_single_tweet_success()
    success &= test_no_url_article()
    
    if success:
        print("\n✓ All bug fix tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)