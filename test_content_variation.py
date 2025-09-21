#!/usr/bin/env python3
"""
Test script for content variation functionality to prevent duplicate tweets
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils


def test_content_variation():
    """Test that content variation produces different outputs for same input"""
    print("🔍 Testing content variation to prevent duplicate tweets")
    print("=" * 60)
    
    # Test article
    article = {
        "title": "Rail Boss 'Stole Electricity from Russian Railways to Fund $12M Bitcoin Mining Operation'",
        "url": "https://example.com/test-article",
        "body": "Test article about Bitcoin mining"
    }
    
    # Generate multiple tweet versions
    variations = []
    for i in range(10):
        tweet = TextUtils.create_hook_tweet(article)
        variations.append(tweet)
        print(f"Version {i+1}: {tweet}")
    
    # Check that we got some variation
    unique_tweets = set(variations)
    print(f"\n📊 Results:")
    print(f"   Generated: {len(variations)} tweets")
    print(f"   Unique: {len(unique_tweets)} tweets")
    print(f"   Variation rate: {len(unique_tweets)/len(variations)*100:.1f}%")
    
    # Test specific variation functions
    print(f"\n🧪 Testing individual variation strategies:")
    base_text = "Company invests $12M in BTC mining via Partner"
    
    # Test each strategy
    time_varied = TextUtils._add_time_context(base_text)
    punctuation_varied = TextUtils._vary_punctuation(base_text)
    industry_varied = TextUtils._add_industry_context(base_text)
    structure_varied = TextUtils._vary_structure(base_text)
    
    print(f"   Original: {base_text}")
    print(f"   Time context: {time_varied}")
    print(f"   Punctuation: {punctuation_varied}")
    print(f"   Industry context: {industry_varied}")
    print(f"   Structure: {structure_varied}")
    
    # Verify length constraints
    print(f"\n📏 Length validation:")
    for i, tweet in enumerate(variations[:5]):
        print(f"   Tweet {i+1}: {len(tweet)} chars (max 280)")
        if len(tweet) > 280:
            print(f"      ❌ TOO LONG!")
            return False
        else:
            print(f"      ✅ OK")
    
    # Success if we got some variation
    if len(unique_tweets) > 1:
        print(f"\n✅ Content variation working! Generated {len(unique_tweets)} unique tweets")
        return True
    else:
        print(f"\n❌ Content variation failed - all tweets identical")
        return False


if __name__ == "__main__":
    success = test_content_variation()
    exit(0 if success else 1)