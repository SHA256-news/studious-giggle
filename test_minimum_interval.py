#!/usr/bin/env python3
"""
Test script for minimum 90-minute interval functionality
Tests the new feature that prevents posting within 90 minutes of the last run
"""

import os
import json
import tempfile
import unittest.mock as mock
from datetime import datetime, timedelta


def test_minimum_interval_check():
    """Test that the minimum 90-minute interval is respected"""
    print("Testing minimum interval functionality...")
    
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
                # Mock the posted_articles.json file with recent run time
                recent_time = datetime.now() - timedelta(minutes=30)  # 30 minutes ago
                
                with open("posted_articles.json", "w") as f:
                    json.dump({
                        "posted_uris": [],
                        "queued_articles": [],
                        "last_run_time": recent_time.isoformat()
                    }, f)
                
                # Mock Twitter and EventRegistry
                with mock.patch('tweepy.Client'), \
                     mock.patch('eventregistry.EventRegistry'):
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Test 1: Recent run should prevent posting
                    assert not bot._is_minimum_interval_respected(), "Should reject run within 90 minutes"
                    print("✓ Recent run correctly rejected (30 minutes ago)")
                    
                    # Test 2: Update to 89 minutes ago - should still be rejected
                    old_time = datetime.now() - timedelta(minutes=89)
                    bot.posted_articles["last_run_time"] = old_time.isoformat()
                    
                    assert not bot._is_minimum_interval_respected(), "Should reject run at 89 minutes"
                    print("✓ Run at 89 minutes correctly rejected")
                    
                    # Test 3: Update to 91 minutes ago - should be allowed
                    old_time = datetime.now() - timedelta(minutes=91)
                    bot.posted_articles["last_run_time"] = old_time.isoformat()
                    
                    assert bot._is_minimum_interval_respected(), "Should allow run after 90 minutes"
                    print("✓ Run at 91 minutes correctly allowed")
                    
                    # Test 4: No previous run should be allowed
                    bot.posted_articles["last_run_time"] = None
                    
                    assert bot._is_minimum_interval_respected(), "Should allow run with no previous run"
                    print("✓ First run correctly allowed")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


def test_integration_with_bot_run():
    """Test that bot.run() respects the minimum interval"""
    print("\nTesting integration with bot.run()...")
    
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
                # Mock the posted_articles.json file with recent run time
                recent_time = datetime.now() - timedelta(minutes=45)
                
                with open("posted_articles.json", "w") as f:
                    json.dump({
                        "posted_uris": [],
                        "queued_articles": [],
                        "last_run_time": recent_time.isoformat()
                    }, f)
                
                # Mock Twitter and EventRegistry
                with mock.patch('tweepy.Client'), \
                     mock.patch('eventregistry.EventRegistry'):
                    
                    from bot import BitcoinMiningNewsBot
                    bot = BitcoinMiningNewsBot()
                    
                    # Mock fetch_bitcoin_mining_articles to ensure it's not called due to interval check
                    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles') as mock_fetch:
                        bot.run()
                        
                        # fetch_bitcoin_mining_articles should not have been called due to interval check
                        mock_fetch.assert_not_called()
                        print("✓ Bot run skipped due to minimum interval check")
                    
                    return True
                    
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    print("🔍 Testing minimum 90-minute interval functionality")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_minimum_interval_check()
        success &= test_integration_with_bot_run()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All minimum interval tests passed!")
            print("📋 Summary:")
            print("   - Minimum 90-minute interval properly enforced")
            print("   - Bot.run() respects interval check")
            print("   - First run (no previous run) allowed")
            print("   - Edge cases handled correctly (89 vs 91 minutes)")
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)