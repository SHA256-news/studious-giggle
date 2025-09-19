#!/usr/bin/env python3
"""
Test script to validate specific bug fixes
"""

import unittest.mock as mock
import os


def test_crypto_filter_overlapping_keywords():
    """Test that overlapping keywords are handled correctly in crypto filter"""
    print("Testing crypto filter overlapping keywords bug fix...")
    
    from crypto_filter import get_unwanted_crypto_found
    
    # Test case that previously returned duplicates
    text = "Mine Bitcoin and several altcoins"
    found = get_unwanted_crypto_found(text)
    
    # Should only find "several altcoins", not "altcoins" as well
    assert found == ["several altcoins"], f"Expected ['several altcoins'], got {found}"
    
    # Test another case
    text2 = "Multiple cryptocurrencies and various coins"
    found2 = get_unwanted_crypto_found(text2)
    
    # Should find the longer phrases, not the shorter overlapping ones
    expected = ["multiple cryptocurrencies", "various coins"]
    assert set(found2) == set(expected), f"Expected {expected}, got {found2}"
    
    print("✓ Crypto filter overlapping keywords fix working correctly")
    return True


def test_entity_extractor_none_handling():
    """Test that entity extractor handles None input gracefully"""
    print("Testing entity extractor None handling bug fix...")
    
    from entity_extractor import EntityExtractor
    
    extractor = EntityExtractor()
    
    # Test None input (previously crashed)
    result = extractor.extract_entities(None)
    expected = {'locations': [], 'companies': [], 'regulatory': [], 'concepts': []}
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test empty string
    result2 = extractor.extract_entities("")
    assert result2 == expected, f"Expected {expected}, got {result2}"
    
    # Test normal input still works
    result3 = extractor.extract_entities("Bitcoin mining in Texas")
    assert "texas" in result3["locations"], f"Expected 'texas' in locations, got {result3}"
    
    print("✓ Entity extractor None handling fix working correctly")
    return True


def test_integration_with_bot():
    """Test that the fixes work properly with the bot integration"""
    print("Testing integration with bot...")
    
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
            from crypto_filter import filter_bitcoin_only_articles
            
            bot = BitcoinMiningNewsBot()
            
            # Test articles that would trigger the overlapping keywords issue
            test_articles = [
                {
                    "title": "Bitcoin mining facility opens",
                    "body": "A new Bitcoin mining facility...",
                    "uri": "bitcoin-1",
                    "url": "https://example.com/1"
                },
                {
                    "title": "Mining several altcoins and Bitcoin",
                    "body": "This platform supports multiple cryptocurrencies...",
                    "uri": "multi-1", 
                    "url": "https://example.com/2"
                }
            ]
            
            # Filter articles
            filtered, excluded_count, excluded_details = filter_bitcoin_only_articles(test_articles)
            
            # Should filter out the multi-crypto article
            assert len(filtered) == 1, f"Expected 1 Bitcoin article, got {len(filtered)}"
            assert excluded_count == 1, f"Expected 1 excluded article, got {excluded_count}"
            
            # Check that overlapping keywords are handled correctly in excluded details
            excluded = excluded_details[0]
            found_keywords = excluded['found_in_title'] + excluded['found_in_body']
            
            # Should not have duplicate overlapping keywords
            assert "several altcoins" in found_keywords, "Should find 'several altcoins'"
            assert "altcoins" not in found_keywords, "Should not find overlapping 'altcoins'"
            assert "multiple cryptocurrencies" in found_keywords, "Should find 'multiple cryptocurrencies'" 
            
            # Test entity extraction with None title
            article_with_none_title = {"title": None, "url": "https://example.com", "uri": "test-uri"}
            tweet_text = bot.create_tweet_text(article_with_none_title)
            assert isinstance(tweet_text, str), "Should handle None title gracefully"
            
            print("✓ Integration tests passed")
            return True


if __name__ == "__main__":
    success = True
    success &= test_crypto_filter_overlapping_keywords()
    success &= test_entity_extractor_none_handling()
    success &= test_integration_with_bot()
    
    if success:
        print("\n✅ ALL BUG FIX TESTS PASSED!")
        print("Both bugs have been successfully fixed:")
        print("  1. Overlapping keywords in crypto filter")
        print("  2. None input handling in entity extractor")
    else:
        print("\n❌ Some bug fix tests failed!")
        exit(1)