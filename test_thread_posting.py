#!/usr/bin/env python3
"""
Test script to verify the thread posting bug fix
"""

import os
import unittest.mock as mock


def test_successful_thread_posting():
    """Test that both tweets are posted successfully"""
    print("Testing successful thread posting...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client') as mock_client, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            # Mock successful tweet creation
            mock_first_tweet = mock.MagicMock()
            mock_first_tweet.data = {"id": "tweet_123"}
            mock_second_tweet = mock.MagicMock()
            mock_second_tweet.data = {"id": "tweet_456"}
            
            mock_client_instance = mock_client.return_value
            mock_client_instance.create_tweet.side_effect = [mock_first_tweet, mock_second_tweet]
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            test_article = {
                "title": "Bitcoin Mining News",
                "url": "https://example.com/article",
                "uri": "test-uri"
            }
            
            # Post to Twitter
            tweet_id = bot.post_to_twitter(test_article)
            
            # Verify both tweets were attempted and first tweet ID returned
            assert tweet_id == "tweet_123", f"Expected tweet_123, got {tweet_id}"
            assert mock_client_instance.create_tweet.call_count == 2, "Should have called create_tweet twice"
            
            # Check the calls
            calls = mock_client_instance.create_tweet.call_args_list
            
            # First call should be the main tweet
            first_call = calls[0]
            assert "Bitcoin Mining News" in first_call[1]['text'] or first_call[0][0], "First tweet should contain article title"
            
            # Second call should be the reply with URL
            second_call = calls[1]
            assert "Read more: https://example.com/article" in (second_call[1]['text'] if 'text' in second_call[1] else second_call.kwargs['text']), "Second tweet should contain URL"
            assert 'reply' in (second_call[1] if len(second_call) > 1 else second_call.kwargs), "Second tweet should be a reply"
            
            print("✓ Both tweets posted successfully")
            return True


def test_second_tweet_failure():
    """Test that first tweet ID is returned even if second tweet fails"""
    print("Testing second tweet failure scenario...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client') as mock_client, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            # Mock first tweet success, second tweet failure
            mock_first_tweet = mock.MagicMock()
            mock_first_tweet.data = {"id": "tweet_123"}
            
            mock_client_instance = mock_client.return_value
            mock_client_instance.create_tweet.side_effect = [
                mock_first_tweet,  # First tweet succeeds
                Exception("Twitter API limit exceeded")  # Second tweet fails
            ]
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            test_article = {
                "title": "Bitcoin Mining News",
                "url": "https://example.com/article",
                "uri": "test-uri"
            }
            
            # Post to Twitter
            tweet_id = bot.post_to_twitter(test_article)
            
            # Verify first tweet ID is still returned despite second tweet failure
            assert tweet_id == "tweet_123", f"Expected tweet_123, got {tweet_id}"
            assert mock_client_instance.create_tweet.call_count == 2, "Should have attempted both tweets"
            
            print("✓ First tweet ID returned despite second tweet failure")
            return True


def test_first_tweet_failure():
    """Test that None is returned if first tweet fails"""
    print("Testing first tweet failure scenario...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client') as mock_client, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            # Mock first tweet failure
            mock_client_instance = mock_client.return_value
            mock_client_instance.create_tweet.side_effect = Exception("Twitter API error")
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            test_article = {
                "title": "Bitcoin Mining News",
                "url": "https://example.com/article",
                "uri": "test-uri"
            }
            
            # Post to Twitter
            tweet_id = bot.post_to_twitter(test_article)
            
            # Verify None is returned when first tweet fails
            assert tweet_id is None, f"Expected None, got {tweet_id}"
            assert mock_client_instance.create_tweet.call_count == 1, "Should have only attempted first tweet"
            
            print("✓ None returned when first tweet fails")
            return True


def test_no_url_scenario():
    """Test behavior when article has no URL"""
    print("Testing no URL scenario...")
    
    with mock.patch.dict(os.environ, {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }):
        with mock.patch('tweepy.Client') as mock_client, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": []}')):
            
            # Mock successful first tweet
            mock_first_tweet = mock.MagicMock()
            mock_first_tweet.data = {"id": "tweet_123"}
            
            mock_client_instance = mock_client.return_value
            mock_client_instance.create_tweet.return_value = mock_first_tweet
            
            from bot import BitcoinMiningNewsBot
            bot = BitcoinMiningNewsBot()
            
            # Article without URL
            test_article = {
                "title": "Bitcoin Mining News",
                "uri": "test-uri"
                # No URL field
            }
            
            # Post to Twitter
            tweet_id = bot.post_to_twitter(test_article)
            
            # Verify first tweet ID is returned and only one tweet was posted
            assert tweet_id == "tweet_123", f"Expected tweet_123, got {tweet_id}"
            assert mock_client_instance.create_tweet.call_count == 1, "Should have only posted first tweet when no URL"
            
            print("✓ Only first tweet posted when no URL available")
            return True


if __name__ == "__main__":
    success = True
    success &= test_successful_thread_posting()
    success &= test_second_tweet_failure()
    success &= test_first_tweet_failure()
    success &= test_no_url_scenario()
    
    if success:
        print("\n✓ All thread posting tests passed!")
    else:
        print("\n✗ Some thread posting tests failed!")
        exit(1)