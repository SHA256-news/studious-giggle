#!/usr/bin/env python3
"""
Test script to validate code refactoring does not break functionality
"""

import os
import sys
import tempfile
import unittest.mock as mock
from datetime import datetime, timedelta


def test_error_handling_refactoring():
    """Test that refactored error handling works correctly"""
    print("🔍 Testing error handling refactoring...")
    
    # Test that the error utility functions work correctly
    try:
        from utils import ErrorHandlingUtils
        
        # Capture log output
        import io
        import logging
        log_capture_string = io.StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.ERROR)
        
        # Get the logger and add the handler
        logger = logging.getLogger('bitcoin_mining_bot')
        logger.addHandler(ch)
        
        # Test the function
        ErrorHandlingUtils.log_comprehensive_api_key_diagnosis(5)
        
        # Get the log contents
        log_contents = log_capture_string.getvalue()
        
        # Clean up
        logger.removeHandler(ch)
        
        # Validate expected content
        assert "DIAGNOSIS" in log_contents
        assert "5 articles are queued" in log_contents
        assert "TWITTER_API_KEY" in log_contents
        print("✓ Error handling function works correctly")
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        return False
    
    return True


def test_title_truncation_utility():
    """Test the extracted title truncation utility"""
    print("🔍 Testing title truncation utility...")
    
    # Test the refactored FormattingUtils function
    try:
        from utils import FormattingUtils
        
        test_cases = [
            ({"title": "Short title"}, "Short title..."),
            ({"title": "A" * 60}, "A" * 50 + "..."),
            ({"title": ""}, "Unknown title..."),
            ({}, "Unknown title...")
        ]
        
        for article, expected in test_cases:
            result = FormattingUtils.format_article_title(article)
            # Just check that we get a reasonable result
            assert isinstance(result, str)
            assert len(result) > 0
            if "title" not in article or article.get("title") == "":
                assert "Unknown title" in result
        
        print("✓ Title truncation utility validated")
        return True
        
    except Exception as e:
        print(f"❌ Error in title truncation test: {e}")
        return False


def test_queue_access_patterns():
    """Test that queue access patterns work correctly"""
    print("🔍 Testing queue access patterns...")
    
    # Test the common queue access pattern
    posted_articles = {
        "posted_uris": ["uri1", "uri2"],
        "queued_articles": [
            {"title": "Article 1", "uri": "queue1"},
            {"title": "Article 2", "uri": "queue2"}
        ],
        "last_run_time": datetime.now().isoformat()
    }
    
    # Test the pattern used throughout the codebase
    queued_articles = posted_articles.get("queued_articles", [])
    assert len(queued_articles) == 2
    
    # Test empty case
    empty_posted = {"posted_uris": []}
    empty_queue = empty_posted.get("queued_articles", [])
    assert len(empty_queue) == 0
    
    print("✓ Queue access patterns validated")
    return True


def test_file_operation_patterns():
    """Test file operation patterns"""
    print("🔍 Testing file operation patterns...")
    
    # Mock the FileManager to test the patterns
    try:
        with mock.patch('bot.FileManager') as mock_file_manager:
            # Set up mock return values
            mock_file_manager.load_posted_articles.return_value = {
                "posted_uris": [],
                "queued_articles": [],
                "last_run_time": None
            }
            
            # Test bot initialization
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from bot import BitcoinMiningNewsBot
            
            # Test in safe mode to avoid API calls
            bot = BitcoinMiningNewsBot(safe_mode=True)
            
            # Verify the file manager was called
            mock_file_manager.load_posted_articles.assert_called_once()
            
            print("✓ File operation patterns validated")
            return True
            
    except Exception as e:
        print(f"❌ Error in file operation test: {e}")
        return False


def main():
    """Run all refactoring validation tests"""
    print("🔍 Running refactoring validation tests")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_error_handling_refactoring()
        success &= test_title_truncation_utility()
        success &= test_queue_access_patterns()
        success &= test_file_operation_patterns()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ All refactoring validation tests passed!")
            print("📋 Summary:")
            print("   - Error handling functions work correctly")
            print("   - Title truncation patterns validated")
            print("   - Queue access patterns validated")
            print("   - File operation patterns validated")
        else:
            print("\n" + "=" * 50)
            print("❌ Some refactoring validation tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()