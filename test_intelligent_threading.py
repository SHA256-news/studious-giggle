#!/usr/bin/env python3
"""
Test script for intelligent threading functionality to prevent text truncation
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils
from config import BotConstants


def test_intelligent_threading():
    """Test that intelligent threading creates proper threads instead of truncating"""
    print("🧵 Testing intelligent threading to prevent truncation")
    print("=" * 60)
    
    # Test case 1: Very long title that would normally get truncated
    long_article = {
        "title": "Research Study Reveals That Advanced Bitcoin Mining Operations Using Latest Generation ASIC Mining Hardware Can Achieve Unprecedented Efficiency Levels of Up to 95 Percent Energy Utilization While Simultaneously Reducing Carbon Footprint Through Integration With Renewable Energy Sources and Advanced Cooling Technologies Implemented Across Modern Mining Facilities",
        "url": "https://example.com/efficiency-study",
        "body": "Detailed research findings..."
    }
    
    print("📰 Test Article 1 (Long research study):")
    print(f"   Title length: {len(long_article['title'])} chars")
    
    # Test what enhanced generic would do (should truncate)
    info = TextUtils.extract_key_info(long_article)
    enhanced_generic = TextUtils._create_enhanced_generic_tweet(info, long_article['title'])
    print(f"   Enhanced generic ({len(enhanced_generic)} chars): {enhanced_generic}")
    
    # Test intelligent threading
    hook, link = TextUtils.create_thread_texts(long_article)
    print(f"   Thread Tweet 1 ({len(hook)} chars): {hook}")
    print(f"   Thread Tweet 2 ({len(link)} chars): {link}")
    
    # Verify threading was used instead of truncation
    assert not hook.endswith("...") or "(1/2)" in hook, "Should create proper thread instead of simple truncation"
    assert len(hook) <= BotConstants.TWEET_MAX_LENGTH, f"Tweet 1 too long: {len(hook)} chars"
    assert len(link) <= BotConstants.TWEET_MAX_LENGTH, f"Tweet 2 too long: {len(link)} chars"
    assert long_article["url"] in link, "URL should be in second tweet"
    print("   ✅ Proper threading detected!")
    
    print()
    
    # Test case 2: Company expansion with very long details
    expansion_article = {
        "title": "Major International Cryptocurrency Mining Corporation With Operations Spanning Multiple Continents Announces Unprecedented Five Hundred Million Dollar Expansion of Bitcoin Mining Operations Including Construction of Advanced State-of-the-Art Data Centers Equipped With Latest Generation Mining Hardware Across Multiple International Facilities Including New Facilities in Texas Wyoming North Dakota Montana and Several International Locations With Expected Completion by End of 2024",
        "url": "https://example.com/major-expansion",
        "body": "Company expansion details..."
    }
    
    print("📰 Test Article 2 (Company expansion):")
    print(f"   Title length: {len(expansion_article['title'])} chars")
    
    hook2, link2 = TextUtils.create_thread_texts(expansion_article)
    print(f"   Thread Tweet 1 ({len(hook2)} chars): {hook2}")
    print(f"   Thread Tweet 2 ({len(link2)} chars): {link2}")
    
    # Verify proper threading
    assert len(hook2) <= BotConstants.TWEET_MAX_LENGTH, f"Tweet 1 too long: {len(hook2)} chars"
    assert len(link2) <= BotConstants.TWEET_MAX_LENGTH, f"Tweet 2 too long: {len(link2)} chars"
    assert expansion_article["url"] in link2, "URL should be in second tweet"
    print("   ✅ Proper threading detected!")
    
    print()
    
    # Test case 3: Normal length content (should not trigger intelligent threading)
    normal_article = {
        "title": "CleanSpark Expands Bitcoin Mining Operations",
        "url": "https://example.com/normal-news",
        "body": "Normal expansion news..."
    }
    
    print("📰 Test Article 3 (Normal length):")
    hook3, link3 = TextUtils.create_thread_texts(normal_article)
    print(f"   Tweet 1 ({len(hook3)} chars): {hook3}")
    print(f"   Tweet 2 ({len(link3)} chars): {link3}")
    
    # Should not have thread indicators for normal content
    assert "(1/2)" not in hook3, "Normal content should not trigger threading"
    assert "(2/2)" not in link3, "Normal content should not trigger threading"
    print("   ✅ Normal threading behavior preserved!")
    
    print()
    
    # Verify no information is lost in threading
    print("🔍 Verifying information preservation:")
    
    # Check that key information from original title appears in threaded tweets
    original_words = set(long_article["title"].lower().split())
    thread_words = set((hook + " " + link).lower().split())
    
    # Key terms should be preserved
    key_terms = ["bitcoin", "mining", "efficiency", "energy", "renewable", "facilities"]
    preserved_terms = [term for term in key_terms if term in thread_words]
    print(f"   Key terms preserved: {preserved_terms}")
    
    # Should preserve most important information
    assert len(preserved_terms) >= 4, "Should preserve most key terms"
    print("   ✅ Important information preserved!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_intelligent_threading()
        if success:
            print("\n🎉 All intelligent threading tests passed!")
            exit(0)
        else:
            print("\n❌ Some tests failed!")
            exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        exit(1)