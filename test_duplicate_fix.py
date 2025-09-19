#!/usr/bin/env python3
"""
Test script to verify duplicate article queue fix
"""

import os
import json
import tempfile
import unittest.mock as mock


def test_duplicate_queue_prevention():
    """Test that duplicate articles are not added to the queue"""
    print("Testing duplicate queue prevention...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
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
                    
                    # Create initial posted_articles with one article already in queue
                    initial_data = {
                        "posted_uris": ["already-posted-1"],
                        "queued_articles": [
                            {"uri": "already-queued-1", "title": "Already Queued Article"}
                        ]
                    }
                    with open("posted_articles.json", "w") as f:
                        json.dump(initial_data, f)
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Mock articles with some duplicates
                    test_articles = [
                        {"uri": "new-article-1", "title": "New Article 1", "url": "https://example.com/1"},
                        {"uri": "new-article-2", "title": "New Article 2", "url": "https://example.com/2"},
                        {"uri": "already-queued-1", "title": "Already Queued Article", "url": "https://example.com/queued"},  # Duplicate
                        {"uri": "new-article-3", "title": "New Article 3", "url": "https://example.com/3"},
                    ]
                    
                    # Mock successful posting
                    mock_twitter_client = mock.Mock()
                    tweet_response = mock.Mock()
                    tweet_response.data = {"id": "12345"}
                    mock_twitter_client.create_tweet.return_value = tweet_response
                    bot.twitter_client = mock_twitter_client
                    
                    # Mock fetch_bitcoin_mining_articles to return our test articles
                    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=test_articles):
                        bot.run()
                    
                    # Check results
                    queue_uris = [article["uri"] for article in bot.posted_articles["queued_articles"]]
                    queue_titles = [article["title"] for article in bot.posted_articles["queued_articles"]]
                    
                    print(f"Queue URIs: {queue_uris}")
                    print(f"Queue titles: {queue_titles}")
                    
                    # Verify no duplicates
                    assert len(queue_uris) == len(set(queue_uris)), f"Duplicate URIs found in queue: {queue_uris}"
                    
                    # Verify the duplicate was not added again
                    assert queue_uris.count("already-queued-1") == 1, "Duplicate article was added to queue"
                    
                    # Verify new articles were added
                    assert "new-article-2" in queue_uris, "New article 2 should be in queue"
                    assert "new-article-3" in queue_uris, "New article 3 should be in queue"
                    
                    print("✓ Duplicate prevention working correctly")
                    return True
                    
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    success = test_duplicate_queue_prevention()
    if success:
        print("\n✓ Duplicate queue fix test passed!")
    else:
        print("\n✗ Duplicate queue fix test failed!")
        exit(1)