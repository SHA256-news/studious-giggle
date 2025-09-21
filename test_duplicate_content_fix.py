#!/usr/bin/env python3
"""
Test script for duplicate content error handling and retry mechanism
"""

import sys
import os
import unittest.mock as mock

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tweet_poster import TweetPoster
from api_clients import TwitterClient


class MockDuplicateContentException(Exception):
    """Mock exception for duplicate content testing"""
    def __init__(self, message="403 Forbidden\nYou are not allowed to create a Tweet with duplicate content."):
        super().__init__(message)
        # Add response attribute for more realistic simulation
        self.response = mock.Mock()
        self.response.status_code = 403
        self.response.text = message


def test_duplicate_content_detection():
    """Test that duplicate content errors are properly detected"""
    print("🔍 Testing duplicate content error detection")
    print("=" * 60)
    
    # Create a TwitterClient mock
    twitter_client = mock.Mock(spec=TwitterClient)
    poster = TweetPoster(twitter_client)
    
    # Test duplicate content error detection
    test_cases = [
        (MockDuplicateContentException(), True, "Mock duplicate content exception"),
        (Exception("403 Forbidden"), True, "Generic 403 error"),
        (Exception("You are not allowed to create a Tweet with duplicate content"), True, "Direct duplicate message"),
        (Exception("Status is a duplicate"), True, "Duplicate status message"),
        (Exception("Rate limit exceeded"), False, "Rate limit error"),
        (Exception("Internal server error"), False, "Generic error"),
    ]
    
    success = True
    for i, (error, should_detect, description) in enumerate(test_cases, 1):
        is_duplicate = poster._is_duplicate_content_error(error)
        status = "✅" if is_duplicate == should_detect else "❌"
        print(f"   Test {i}: {status} {description} -> {is_duplicate}")
        if is_duplicate != should_detect:
            success = False
    
    return success


def test_duplicate_content_retry_logic():
    """Test that the bot retries with new content variation when duplicate content is detected"""
    print("\n🔍 Testing duplicate content retry with variation")
    print("=" * 60)
    
    # Create a TwitterClient mock
    twitter_client = mock.Mock(spec=TwitterClient)
    
    # Set up the mock to fail with duplicate content on first attempt, succeed on second
    twitter_client.create_tweet.side_effect = [
        MockDuplicateContentException(),  # First attempt fails
        mock.Mock(data=mock.Mock(id="123456789"))  # Second attempt succeeds
    ]
    
    poster = TweetPoster(twitter_client)
    
    # Test article
    article = {
        "title": "Test Company Invests $10M in Bitcoin Mining",
        "url": "https://example.com/test",
        "body": "Test article content"
    }
    
    # Attempt to post
    result = poster.post_to_twitter(article)
    
    # Check results
    print(f"   Twitter API calls made: {twitter_client.create_tweet.call_count}")
    print(f"   Result: {result}")
    
    # Verify that create_tweet was called twice (retry after duplicate error)
    if twitter_client.create_tweet.call_count == 2:
        print("   ✅ Bot correctly retried after duplicate content error")
        
        # Check that the two calls had different content (due to variation)
        call_1_text = twitter_client.create_tweet.call_args_list[0][1]['text']
        call_2_text = twitter_client.create_tweet.call_args_list[1][1]['text']
        
        print(f"   First attempt: {call_1_text}")
        print(f"   Second attempt: {call_2_text}")
        
        if call_1_text != call_2_text:
            print("   ✅ Content variation applied successfully")
            return True
        else:
            print("   ❌ Content was identical on retry (variation failed)")
            return False
    else:
        print(f"   ❌ Expected 2 calls, got {twitter_client.create_tweet.call_count}")
        return False


def test_max_retries_duplicate_content():
    """Test that bot stops retrying after max attempts with duplicate content"""
    print("\n🔍 Testing max retries with persistent duplicate content")
    print("=" * 60)
    
    # Create a TwitterClient mock that always fails with duplicate content
    twitter_client = mock.Mock(spec=TwitterClient)
    twitter_client.create_tweet.side_effect = MockDuplicateContentException()
    
    poster = TweetPoster(twitter_client)
    
    # Test article
    article = {
        "title": "Test Company Invests $10M in Bitcoin Mining",
        "url": "https://example.com/test",
        "body": "Test article content"
    }
    
    # Attempt to post (should fail after max retries)
    result = poster.post_to_twitter(article)
    
    print(f"   Twitter API calls made: {twitter_client.create_tweet.call_count}")
    print(f"   Result: {result}")
    
    # Should make 2 attempts (initial + 1 retry), then give up
    if twitter_client.create_tweet.call_count == 2 and result is None:
        print("   ✅ Bot correctly stopped after max retries")
        return True
    else:
        print(f"   ❌ Expected 2 calls and None result, got {twitter_client.create_tweet.call_count} calls and {result}")
        return False


def main():
    """Run all duplicate content tests"""
    print("🧪 Testing Duplicate Content Fix")
    print("=" * 80)
    
    success = True
    
    try:
        success &= test_duplicate_content_detection()
        success &= test_duplicate_content_retry_logic()
        success &= test_max_retries_duplicate_content()
        
        if success:
            print("\n" + "=" * 80)
            print("✅ All duplicate content tests passed!")
            print("🔧 The bot should now handle Twitter's duplicate content errors correctly.")
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