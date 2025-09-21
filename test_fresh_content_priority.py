#!/usr/bin/env python3
"""
Test script for fresh content prioritization logic
"""

import sys
import os
import unittest.mock as mock
from datetime import datetime, timedelta

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import BitcoinMiningNewsBot


def test_stale_queue_detection():
    """Test that stale queue detection works correctly"""
    print("🔍 Testing stale queue detection logic")
    print("=" * 60)
    
    # Mock the bot to avoid API key requirements
    with mock.patch('bot.APIClientManager'):
        bot = BitcoinMiningNewsBot()
    
    # Test 1: Empty queue
    bot.posted_articles = {"posted_uris": [], "queued_articles": []}
    result = bot._is_queue_stale()
    print(f"   Empty queue: {result} (should be False)")
    assert not result
    # Test 2: Queue with no date information (should not be considered stale)
    bot.posted_articles = {
        "posted_uris": [],
        "queued_articles": [
            {"uri": "test-1", "title": "Test Article 1"},
            {"uri": "test-2", "title": "Test Article 2"}
        ]
    }
    result = bot._is_queue_stale()
    print(f"   Queue without dates: {result} (should be False)")
    assert not result
    
    # Test 3: Queue with fresh articles (within 48 hours)
    fresh_time = datetime.now() - timedelta(hours=12)
    bot.posted_articles = {
        "posted_uris": [],
        "queued_articles": [
            {"uri": "test-1", "title": "Fresh Article 1", "dateTimePub": fresh_time.isoformat() + "Z"},
            {"uri": "test-2", "title": "Fresh Article 2", "dateTimePub": fresh_time.isoformat() + "Z"}
        ]
    }
    result = bot._is_queue_stale()
    print(f"   Fresh queue (12h old): {result} (should be False)")
    assert not result
    
    # Test 4: Queue with stale articles (older than 48 hours)
    stale_time = datetime.now() - timedelta(hours=72)
    bot.posted_articles = {
        "posted_uris": [],
        "queued_articles": [
            {"uri": "test-1", "title": "Stale Article 1", "dateTimePub": stale_time.isoformat() + "Z"},
            {"uri": "test-2", "title": "Stale Article 2", "dateTimePub": stale_time.isoformat() + "Z"}
        ]
    }
    result = bot._is_queue_stale()
    print(f"   Stale queue (72h old): {result} (should be True)")
    assert result
    
    # Test 5: Mixed queue (half fresh, half stale)
    bot.posted_articles = {
        "posted_uris": [],
        "queued_articles": [
            {"uri": "test-1", "title": "Fresh Article", "dateTimePub": fresh_time.isoformat() + "Z"},
            {"uri": "test-2", "title": "Stale Article", "dateTimePub": stale_time.isoformat() + "Z"}
        ]
    }
    result = bot._is_queue_stale()
    print(f"   Mixed queue (50% stale): {result} (should be False, not majority stale)")
    assert not result
    
    print("   ✅ All stale queue detection tests passed!")
    return True


def test_fresh_content_prioritization():
    """Test that fresh content is prioritized over stale queue"""
    print("\n🔍 Testing fresh content prioritization")
    print("=" * 60)
    
    # Test behavior when queue has stale content and new articles are available
    with mock.patch('bot.APIClientManager'):
        bot = BitcoinMiningNewsBot()
        
        # Set up stale queue
        stale_time = datetime.now() - timedelta(hours=72)
        bot.posted_articles = {
            "posted_uris": [],
            "queued_articles": [
                {"uri": "stale-1", "title": "Stale Article", "dateTimePub": stale_time.isoformat() + "Z"}
            ]
        }
        
        # New fresh articles
        fresh_articles = [
            {"uri": "fresh-1", "title": "Fresh Article", "url": "https://example.com/fresh"}
        ]
        
        print(f"   Setup: 1 stale queued article, 1 fresh article available")
        
        # The bot should prioritize fresh content and post it, not the stale queue
        with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=fresh_articles):
            with mock.patch.object(bot, '_post_article', return_value=True) as mock_post:
                with mock.patch.object(bot, '_is_minimum_interval_respected', return_value=True):
                    with mock.patch.object(bot, '_is_rate_limit_cooldown_active', return_value=False):
                        with mock.patch('utils.FileManager.save_posted_articles'):
                            bot.run()
                
                # Should post the fresh article, not the stale one
                assert mock_post.call_count == 1
                posted_article = mock_post.call_args[0][0]
                assert posted_article["uri"] == "fresh-1"
                print(f"   ✅ Bot correctly prioritized fresh article over stale queue")
        
    return True


def test_queue_processing_when_no_fresh_content():
    """Test that queue is processed when no fresh content and queue is not stale"""
    print("\n🔍 Testing queue processing fallback")
    print("=" * 60)
    
    with mock.patch('bot.APIClientManager'):
        bot = BitcoinMiningNewsBot()
        
        # Set up fresh queue (not stale)
        fresh_time = datetime.now() - timedelta(hours=12)
        bot.posted_articles = {
            "posted_uris": [],
            "queued_articles": [
                {"uri": "fresh-queued-1", "title": "Fresh Queued Article", "dateTimePub": fresh_time.isoformat() + "Z"}
            ]
        }
        
        # No new articles
        fresh_articles = []
        
        print(f"   Setup: 1 fresh queued article, 0 new articles available")
        
        # Should process the fresh queued article
        with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=fresh_articles):
            with mock.patch.object(bot, '_post_article', return_value=True) as mock_post:
                with mock.patch.object(bot, '_is_minimum_interval_respected', return_value=True):
                    with mock.patch.object(bot, '_is_rate_limit_cooldown_active', return_value=False):
                        with mock.patch('utils.FileManager.save_posted_articles'):
                            bot.run()
                
                # Should post the queued article
                assert mock_post.call_count == 1
                posted_article = mock_post.call_args[0][0]
                assert posted_article["uri"] == "fresh-queued-1"
                print(f"   ✅ Bot correctly processed fresh queued article when no new content")
        
    return True


def main():
    """Run all fresh content prioritization tests"""
    print("🧪 Testing Fresh Content Prioritization Logic")
    print("=" * 80)
    
    success = True
    
    try:
        success &= test_stale_queue_detection()
        success &= test_fresh_content_prioritization()
        success &= test_queue_processing_when_no_fresh_content()
        
        if success:
            print("\n" + "=" * 80)
            print("✅ All fresh content prioritization tests passed!")
            print("🔧 The bot correctly prioritizes fresh content over stale queued articles.")
        else:
            print("\n" + "=" * 80)
            print("❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        success = False
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)