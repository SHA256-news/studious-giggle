#!/usr/bin/env python3
"""
Simple test to debug the queue processing issue
"""

import sys
import os
import unittest.mock as mock

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import BitcoinMiningNewsBot


def debug_queue_processing():
    """Debug what happens when no new articles and queue exists"""
    print("🔍 Debugging queue processing")
    print("=" * 60)
    
    # Create mocked dependencies
    with mock.patch('bot.APIClientManager'):
        bot = BitcoinMiningNewsBot()
        
        # Set up queue with articles (no dates)
        bot.posted_articles = {
            "posted_uris": [],
            "queued_articles": [
                {"uri": "queued-uri-1", "title": "Queued Article", "url": "https://example.com/queued"},
                {"uri": "queued-uri-2", "title": "Another Queued Article", "url": "https://example.com/queued2"}
            ]
        }
        
        print(f"   Queue setup: {len(bot.posted_articles['queued_articles'])} articles")
        
        # Test staleness check
        is_stale = bot._is_queue_stale()
        print(f"   Queue staleness: {is_stale}")
        
        # Mock no new articles from EventRegistry
        sample_articles = []
        
        with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
            with mock.patch.object(bot, '_post_article', return_value=True) as mock_post:
                with mock.patch.object(bot, '_is_minimum_interval_respected', return_value=True):
                    with mock.patch.object(bot, '_is_rate_limit_cooldown_active', return_value=False):
                        with mock.patch('utils.FileManager.save_posted_articles'):
                            print(f"   Running bot...")
                            bot.run()
                            print(f"   Post attempts: {mock_post.call_count}")
                            if mock_post.call_count > 0:
                                posted_article = mock_post.call_args[0][0]
                                print(f"   Posted article URI: {posted_article['uri']}")
                            else:
                                print(f"   No articles posted")


if __name__ == "__main__":
    debug_queue_processing()