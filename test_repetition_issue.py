#!/usr/bin/env python3
"""
Test script to demonstrate the repetition issue in three-part threads
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_repetition_issue():
    """Test that demonstrates the repetition issue"""
    print("Testing three-part thread repetition issue...")
    
    # Sample article that would cause repetition like the CleanSpark example
    article = {
        "title": "CleanSpark Secures $100M Credit Line from Coinbase Prime",
        "body": "CleanSpark, a Bitcoin mining company, has secured an additional $100 million credit line from Coinbase Prime, backed by its Bitcoin holdings. The credit is non-dilutive and the stock has increased by 33% following the announcement.",
        "url": "https://example.com/cleanspark-news",
        "uri": "cleanspark-news-uri",
        "gemini_headline": "CleanSpark secured an additional $100 million credit line from Coinbase Prime, backed by its Bitcoin holdings",
        "gemini_summary": "Key highlights:\n• $100M Coinbase credit\n• BTC-backed non-dilutive\n• Stock up 33%"
    }
    
    print(f"Article title: {article['title']}")
    print(f"Gemini headline: {article['gemini_headline']}")
    print(f"Gemini summary: {article['gemini_summary']}")
    print()
    
    # Create three-part thread
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article)
    
    print("=== THREE-PART THREAD ===")
    print(f"Tweet 1 (Hook): {hook_tweet}")
    print(f"Tweet 2 (Summary): {summary_tweet}")
    print(f"Tweet 3 (URL): {url_tweet}")
    print()
    
    # Check for repetition
    hook_lower = hook_tweet.lower()
    summary_lower = summary_tweet.lower()
    
    # Find common phrases
    repetitions = []
    
    # Check for repeated information
    if "$100" in hook_lower and "$100" in summary_lower:
        repetitions.append("$100M amount")
    if "coinbase" in hook_lower and "coinbase" in summary_lower:
        repetitions.append("Coinbase reference")
    if "credit" in hook_lower and "credit" in summary_lower:
        repetitions.append("Credit line mention")
    if "btc" in hook_lower and "btc" in summary_lower:
        repetitions.append("BTC/Bitcoin reference")
    
    if repetitions:
        print(f"❌ REPETITION DETECTED: {', '.join(repetitions)}")
        print("The hook tweet and summary tweet contain overlapping information")
    else:
        print("✅ No repetition detected")
    
    # Also check the generic issue of starting with "The article states that..."
    if hook_tweet.lower().startswith("the article"):
        print("❌ GENERIC HEADLINE: Hook tweet starts with 'The article...' - not catchy")
    elif hook_tweet.lower().startswith("new bitcoin"):
        print("❌ GENERIC HEADLINE: Hook tweet starts with 'New Bitcoin...' - not catchy")
    else:
        print("✅ Hook tweet has a catchy headline")
    
    return repetitions, hook_tweet, summary_tweet, url_tweet

if __name__ == "__main__":
    test_repetition_issue()