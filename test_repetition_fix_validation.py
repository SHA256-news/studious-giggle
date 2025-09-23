#!/usr/bin/env python3
"""
Test script to validate the repetition fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def check_content_repetition(tweet1: str, tweet2: str, url: str = "") -> list:
    """Check for repetitive content between two tweets, excluding URL"""
    if not tweet1 or not tweet2:
        return []
    
    # Remove URL from analysis
    tweet1_content = tweet1.replace(url, "").strip() if url else tweet1
    tweet2_content = tweet2.replace(url, "").strip() if url else tweet2
    
    tweet1_lower = tweet1_content.lower()
    tweet2_lower = tweet2_content.lower()
    
    repetitions = []
    
    # Check for common repetitive elements in content only
    if "$100" in tweet1_lower and "$100" in tweet2_lower:
        repetitions.append("$100M amount")
    if "coinbase" in tweet1_lower and "coinbase" in tweet2_lower:
        repetitions.append("Coinbase reference")
    if "credit" in tweet1_lower and "credit" in tweet2_lower:
        repetitions.append("Credit line mention")
    if "mining" in tweet1_lower and "mining" in tweet2_lower:
        repetitions.append("Mining reference")
    if "cleanspark" in tweet1_lower and "cleanspark" in tweet2_lower:
        repetitions.append("CleanSpark company name")
    
    return repetitions

def test_repetition_fix():
    """Test that the repetition fix works correctly"""
    print("🔧 TESTING REPETITION FIX VALIDATION")
    print("="*60)
    
    # Test case 1: The exact problem from Twitter
    article = {
        "title": "CleanSpark expands capital strategy with $100M Bitcoin-backed credit from Coinbase Prime",
        "body": "The new credit facility provides non-dilutive financing...",
        "url": "https://cryptobriefing.com/cleanspark-coinbase-prime-100m-credit-expansion/",
        "uri": "2025-09-840996660",
        "gemini_headline": "The article details CleanSpark securing a $100 million Bitcoin-backed credit line from Coinbase Prime to fuel its mining expansion and enable...",
        "gemini_summary": "Key highlights:\n• $100M credit line secured\n• Mining ops expansion\n• 12,703 BTC holdings"
    }
    
    print("TEST 1: EXACT PROBLEM REPRODUCTION")
    print(f"Original problematic Gemini data:")
    print(f"  Headline: {article['gemini_headline']}")
    print(f"  Summary: {article['gemini_summary']}")
    print()
    
    # Generate tweets
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article)
    
    print("Generated tweets:")
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Summary): {summary_tweet}")
    print(f"  Tweet 3 (URL): {url_tweet}")
    print()
    
    # Check for content repetition (excluding URL)
    repetitions = check_content_repetition(hook_tweet, summary_tweet, article["url"])
    if repetitions:
        print(f"❌ CONTENT REPETITION: {', '.join(repetitions)}")
        return False
    else:
        print("✅ NO CONTENT REPETITION: Summary properly filtered")
    
    print()
    
    # Test case 2: Two-part thread with problematic data
    print("TEST 2: TWO-PART THREAD WITH FILTERED CONTENT")
    hook_tweet, link_tweet = TextUtils.create_thread_texts(article)
    
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Link): {link_tweet}")
    print()
    
    # Extract content part of link tweet (before URL)
    link_content = link_tweet.split('\n\n')[0] if '\n\n' in link_tweet else link_tweet.split(article["url"])[0]
    repetitions = check_content_repetition(hook_tweet, link_content)
    
    if repetitions:
        print(f"❌ CONTENT REPETITION: {', '.join(repetitions)}")
        return False
    else:
        print("✅ NO CONTENT REPETITION: Link content properly filtered")
    
    print()
    
    # Test case 3: Verify non-repetitive content is preserved
    article_good = {
        "title": "Bitcoin Mining Company Opens New Facility",
        "url": "https://example.com/news",
        "gemini_headline": "New Bitcoin mining facility opens in Texas with 50MW capacity",
        "gemini_summary": "Key highlights:\n• 50MW power capacity\n• 500 mining rigs\n• Operations start Q2"
    }
    
    print("TEST 3: NON-REPETITIVE CONTENT PRESERVATION")
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article_good)
    
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Summary): {summary_tweet}")
    print()
    
    if not summary_tweet.strip():
        print("❌ GOOD CONTENT FILTERED: Non-repetitive summary was removed")
        return False
    else:
        print("✅ GOOD CONTENT PRESERVED: Non-repetitive summary kept")
    
    print()
    print("🎉 ALL REPETITION FIXES VALIDATED SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    success = test_repetition_fix()
    sys.exit(0 if success else 1)