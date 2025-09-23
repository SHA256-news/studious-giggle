#!/usr/bin/env python3
"""
Test script to reproduce the exact problem statement issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_actual_problem():
    """Test the exact problem described in the issue"""
    print("Testing actual problem: Reproducing the Twitter issue...")
    
    # The real article from queue that would cause this issue
    article = {
        "title": "CleanSpark expands capital strategy with $100M Bitcoin-backed credit from Coinbase Prime",
        "body": "The new credit facility provides non-dilutive financing, allowing CleanSpark to raise capital without issuing new shares.\n\nCleanSpark, a US-based sustainable Bitcoin mining company, secured a $100 million credit facility from Coinbase Prime, an institutional-grade platform for advanced trading and custody services.\n\nThe credit arrangement allows the mining company to leverage its Bitcoin holdings as collateral for non-dilutive financing, reflecting a broader trend among crypto companies accessing capital without issuing new shares.",
        "url": "https://cryptobriefing.com/cleanspark-coinbase-prime-100m-credit-expansion/",
        "uri": "2025-09-840996660"
        # Note: NO gemini_headline or gemini_summary - this is the key issue
    }
    
    print("=== TESTING ALL TWEET GENERATION METHODS ===")
    print("Article (no Gemini data):")
    print(f"Title: {article['title']}")
    print(f"Has gemini_headline: {'gemini_headline' in article}")
    print(f"Has gemini_summary: {'gemini_summary' in article}")
    print()
    
    # Test 1: Two-part thread (current production)
    print("1. TWO-PART THREAD (current production):")
    hook_tweet, link_tweet = TextUtils.create_thread_texts(article)
    print(f"   Tweet 1: {hook_tweet}")
    print(f"   Tweet 2: {link_tweet}")
    
    # Check for repetition
    repetitions = check_repetition(hook_tweet, link_tweet)
    print(f"   Repetition: {'❌ ' + ', '.join(repetitions) if repetitions else '✅ None'}")
    print()
    
    # Test 2: Three-part thread
    print("2. THREE-PART THREAD:")
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article)
    print(f"   Tweet 1: {hook_tweet}")
    print(f"   Tweet 2: {summary_tweet}")
    print(f"   Tweet 3: {url_tweet}")
    
    # Check for repetition between tweet 1 and 2
    repetitions = check_repetition(hook_tweet, summary_tweet)
    print(f"   Repetition (1-2): {'❌ ' + ', '.join(repetitions) if repetitions else '✅ None'}")
    print()
    
    # Test 3: What happens if we add mock Gemini data that creates repetition
    print("3. WITH PROBLEMATIC GEMINI DATA (reproduces the Twitter issue):")
    article_with_gemini = article.copy()
    article_with_gemini["gemini_headline"] = "The article details CleanSpark securing a $100 million Bitcoin-backed credit line from Coinbase Prime to fuel its mining expansion and enable..."
    article_with_gemini["gemini_summary"] = "Key highlights:\n• $100M credit line secured\n• Mining ops expansion\n• 12,703 BTC holdings"
    
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article_with_gemini)
    print(f"   Tweet 1: {hook_tweet}")
    print(f"   Tweet 2: {summary_tweet}")
    print(f"   Tweet 3: {url_tweet}")
    
    # Check for repetition
    repetitions = check_repetition(hook_tweet, summary_tweet)
    print(f"   Repetition: {'❌ ' + ', '.join(repetitions) if repetitions else '✅ None'}")
    print()
    
    return article_with_gemini, hook_tweet, summary_tweet

def check_repetition(tweet1: str, tweet2: str) -> list:
    """Check for repetitive content between two tweets"""
    if not tweet1 or not tweet2:
        return []
        
    tweet1_lower = tweet1.lower()
    tweet2_lower = tweet2.lower()
    
    repetitions = []
    
    # Check for common repetitive elements
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

if __name__ == "__main__":
    test_actual_problem()