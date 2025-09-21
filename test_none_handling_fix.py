#!/usr/bin/env python3
"""
Test to verify None handling fix for Issue #85

This test verifies that TextUtils methods handle None article inputs gracefully
instead of raising AttributeError when trying to call methods on None.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_none_handling_fix():
    """Test that the None handling fix works correctly"""
    print("Testing None handling fix for Issue #85...")
    
    from utils import TextUtils
    
    # Test the main methods that should handle None gracefully
    test_cases = [
        ("create_tweet_text", TextUtils.create_tweet_text, str),
        ("create_hook_tweet", TextUtils.create_hook_tweet, str),
        ("create_link_tweet", TextUtils.create_link_tweet, str),
        ("create_enhanced_tweet_text", TextUtils.create_enhanced_tweet_text, str),
        ("create_original_tweet_text", TextUtils.create_original_tweet_text, str),
        ("create_thread_texts", TextUtils.create_thread_texts, tuple),
    ]
    
    all_passed = True
    
    for method_name, method, expected_type in test_cases:
        try:
            result = method(None)
            if isinstance(result, expected_type):
                print(f"✓ {method_name}(None) handled gracefully")
            else:
                print(f"✗ {method_name}(None) returned wrong type: {type(result)}")
                all_passed = False
        except AttributeError as e:
            print(f"✗ {method_name}(None) still raises AttributeError: {e}")
            all_passed = False
        except Exception as e:
            print(f"✗ {method_name}(None) failed with unexpected error: {e}")
            all_passed = False
    
    return all_passed

def test_none_title_handling():
    """Test that None titles are handled properly"""
    print("Testing None title handling...")
    
    from utils import TextUtils
    
    # Test various combinations of None values in articles
    test_articles = [
        {"title": None, "url": "https://example.com"},
        {"title": None, "uri": "test-uri", "url": None},
        {"gemini_headline": None, "title": None},
    ]
    
    all_passed = True
    
    for i, article in enumerate(test_articles, 1):
        try:
            result = TextUtils.create_tweet_text(article)
            if isinstance(result, str) and len(result) > 0:
                print(f"✓ Article {i} with None title handled correctly")
            else:
                print(f"✗ Article {i} produced empty result")
                all_passed = False
        except Exception as e:
            print(f"✗ Article {i} failed: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("None Handling Fix Test (Issue #85)")
    print("=" * 40)
    
    success1 = test_none_handling_fix()
    success2 = test_none_title_handling()
    
    if success1 and success2:
        print("\n✅ All None handling tests passed!")
        print("✅ Issue #85 fixed - Functions now handle None inputs gracefully")
    else:
        print("\n❌ Some None handling tests failed")
        print("❌ Issue #85 - Fix needs more work")