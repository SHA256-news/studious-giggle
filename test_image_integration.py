#!/usr/bin/env python3
"""
Test Image Attachment Integration
"""

import json
import sys
import tempfile
import os
from unittest import mock

import pytest

# Mock tweepy and eventregistry before imports
if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

if "eventregistry" not in sys.modules:
    sys.modules["eventregistry"] = mock.MagicMock()

def test_image_attachment_integration():
    """Test that bot integrates image attachments correctly"""
    print("Testing image attachment integration...")
    
    # Mock environment variables
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with mock.patch.dict(os.environ, env_vars):
        with mock.patch('tweepy.Client') as MockTwitterClient, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')) as mock_file:
            
            # Mock Twitter client responses
            mock_twitter_client = mock.Mock()
            MockTwitterClient.return_value = mock_twitter_client
            
            # Mock successful tweet response
            first_tweet = mock.Mock()
            first_tweet.data = {"id": "123456"}
            
            second_tweet = mock.Mock()
            second_tweet.data = {"id": "789012"}
            
            # Mock successful media upload
            mock_media = mock.Mock()
            mock_media.media_id = "media_123"
            mock_twitter_client.create_media.return_value = mock_media
            
            mock_twitter_client.create_tweet.side_effect = [first_tweet, second_tweet]
            
            # Import and test bot
            from bot import BitcoinMiningNewsBot
            
            # Create bot instance
            bot = BitcoinMiningNewsBot()
            
            # Verify image selector is initialized
            assert hasattr(bot, 'image_selector'), "Bot should have image_selector attribute"
            assert bot.image_selector is not None, "Image selector should be initialized"
            
            print("✓ Bot initialized with image support")
            
            # Test image selection and upload
            test_article = {
                "title": "Texas Bitcoin Mining Farm Expands Operations",
                "uri": "test-uri",
                "url": "https://example.com/article"
            }
            
            # Mock image selection to return actual downloaded images
            with mock.patch.object(bot.image_selector, 'select_images_for_headline') as mock_select:
                with mock.patch.object(bot.image_selector, 'validate_images_for_twitter') as mock_validate:
                    # Use actual downloaded images from our test
                    mock_select.return_value = ["images/bitcoin_bitcoin_logo.png"]
                    mock_validate.return_value = ["images/bitcoin_bitcoin_logo.png"]
                    
                    # Test posting with images
                    result = bot.post_to_twitter(test_article)
                    
                    # Verify tweet was posted
                    assert result == "123456", "Should return tweet ID"
                    
                    # Verify create_tweet was called twice (threaded tweet: main + reply)
                    assert mock_twitter_client.create_tweet.call_count == 2, "Should call create_tweet twice (threaded tweet with URL)"
                    
                    # Check the call (main tweet with images)
                    call_args = mock_twitter_client.create_tweet.call_args_list[0][1]
                    assert "media_ids" in call_args, "Tweet should include media_ids"
                    assert call_args["media_ids"] == ["media_123"], "Should use uploaded media ID"
                    
                    # Verify media upload was called
                    mock_twitter_client.create_media.assert_called_once()
                    
                    print("✓ Tweet posted with image attachment")
            
            return True

def test_image_fallback_without_images():
    """Test that bot gracefully falls back to text-only when images fail"""
    print("Testing image fallback behavior...")
    
    env_vars = {
        'TWITTER_API_KEY': 'test_key',
        'TWITTER_API_SECRET': 'test_secret',
        'TWITTER_ACCESS_TOKEN': 'test_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
        'EVENTREGISTRY_API_KEY': 'test_er_key'
    }
    
    with mock.patch.dict(os.environ, env_vars):
        with mock.patch('tweepy.Client') as MockTwitterClient, \
             mock.patch('eventregistry.EventRegistry'), \
             mock.patch('builtins.open', mock.mock_open(read_data='{"posted_uris": [], "queued_articles": []}')) as mock_file:
            
            # Mock Twitter client responses
            mock_twitter_client = mock.Mock()
            MockTwitterClient.return_value = mock_twitter_client
            
            # Mock successful tweet response
            first_tweet = mock.Mock()
            first_tweet.data = {"id": "123456"}
            
            second_tweet = mock.Mock()
            second_tweet.data = {"id": "789012"}
            
            mock_twitter_client.create_tweet.side_effect = [first_tweet, second_tweet]
            
            # Import and test bot
            from bot import BitcoinMiningNewsBot
            
            # Create bot instance
            bot = BitcoinMiningNewsBot()
            
            # Test with image upload failure
            test_article = {
                "title": "Bitcoin Mining News Without Images",
                "uri": "test-uri",
                "url": "https://example.com/article"
            }
            
            # Mock image selector to fail
            with mock.patch.object(bot.image_selector, 'select_images_for_headline', side_effect=Exception("Image selection failed")):
                # Test posting should still work (fallback to text-only)
                result = bot.post_to_twitter(test_article)
                
                # Verify tweet was posted without images
                assert result == "123456", "Should return tweet ID even without images"
                
                # Verify create_tweet was called twice (threaded tweet: main + reply)
                assert mock_twitter_client.create_tweet.call_count == 2, "Should call create_tweet twice (threaded tweet with URL)"
                
                # Check the call (main tweet without images)
                call_args = mock_twitter_client.create_tweet.call_args_list[0][1]
                assert "media_ids" not in call_args or not call_args.get("media_ids"), "Should not include media_ids when images fail"
                
                print("✓ Graceful fallback to text-only tweet")
            
            return True

def test_entity_extraction_accuracy():
    """Test entity extraction accuracy on various headlines"""
    print("Testing entity extraction accuracy...")
    
    from entity_extractor import EntityExtractor
    extractor = EntityExtractor()
    
    test_cases = [
        {
            "headline": "Michigan Bitcoin Reserve Bill Moves Forward After Months of Delay",
            "expected_location": "michigan",
            "expected_context": "adoption"
        },
        {
            "headline": "Texas Bitcoin Mining Farm Expands Operations with 100 New Rigs",
            "expected_location": "texas", 
            "expected_context": "mining"
        },
        {
            "headline": "Coinbase Announces New Bitcoin Mining Support Features",
            "expected_company": "coinbase",
            "expected_context": "mining"
        },
        {
            "headline": "SEC Approves First Bitcoin Mining ETF Application",
            "expected_regulatory": "sec",
            "expected_context": "etf"
        },
        {
            "headline": "Bitcoin Mining Difficulty Reaches All-Time High",
            "expected_concept": "difficulty",
            "expected_context": "mining"
        }
    ]
    
    for test_case in test_cases:
        analysis = extractor.analyze_headline(test_case["headline"])
        
        # Check expected location
        if "expected_location" in test_case:
            assert test_case["expected_location"] in analysis["entities"]["locations"], \
                f"Should detect location '{test_case['expected_location']}' in: {test_case['headline']}"
        
        # Check expected company
        if "expected_company" in test_case:
            assert test_case["expected_company"] in analysis["entities"]["companies"], \
                f"Should detect company '{test_case['expected_company']}' in: {test_case['headline']}"
        
        # Check expected regulatory body
        if "expected_regulatory" in test_case:
            assert test_case["expected_regulatory"] in analysis["entities"]["regulatory"], \
                f"Should detect regulatory body '{test_case['expected_regulatory']}' in: {test_case['headline']}"
        
        # Check expected concept
        if "expected_concept" in test_case:
            assert test_case["expected_concept"] in analysis["entities"]["concepts"], \
                f"Should detect concept '{test_case['expected_concept']}' in: {test_case['headline']}"
        
        # Check context
        assert analysis["bitcoin_context"] == test_case["expected_context"], \
            f"Should detect context '{test_case['expected_context']}' in: {test_case['headline']}"
    
    print("✓ Entity extraction working accurately")
    return True

if __name__ == "__main__":
    success = True
    
    try:
        success &= test_image_attachment_integration()
        success &= test_image_fallback_without_images()
        success &= test_entity_extraction_accuracy()
    except Exception as e:
        print(f"Test failed: {e}")
        success = False
    
    if success:
        print("\n✅ All image integration tests passed!")
    else:
        print("\n❌ Some image integration tests failed!")
        sys.exit(1)