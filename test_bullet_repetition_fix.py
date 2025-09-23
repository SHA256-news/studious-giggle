#!/usr/bin/env python3
"""
Test script to validate the bullet point repetition fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_bullet_repetition_fix():
    """Test that the bullet point repetition issue from the problem statement is fixed"""
    print("🔧 TESTING BULLET POINT REPETITION FIX")
    print("=" * 60)
    
    # Test case 1: The exact problem from the issue
    print("TEST 1: EXACT ISSUE REPRODUCTION")
    print("Problem statement shows bullet points repeated between Tweet 1 and Tweet 2")
    
    article = {
        "title": "Trump's UN Speech on Energy and Bitcoin Mining",
        "body": "Trump speech content about energy and crypto...",
        "url": "https://example.com/trump-speech-news",
        "uri": "trump-speech-uri",
        # Gemini headline with bullet points (this is the problem source)
        "gemini_headline": "Trump's UN Speech: Calls Green Energy a \"Hoax,\" Paving the Way for Cheaper Traditional Electricity & Lower Bitcoin Mining Costs! • Cheap energy cuts BTC cost. • Nationalism aids crypto. • Anti-green energy stance.",
        # Summary with same bullet points  
        "gemini_summary": "• Cheap energy cuts BTC cost.\n• Nationalism aids crypto.\n• Anti-green energy stance."
    }
    
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article)
    
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Summary): {summary_tweet}")
    print(f"  Tweet 3 (URL): {url_tweet}")
    print()
    
    # Check for bullet point repetition
    if not summary_tweet.strip():
        print("✅ BULLET REPETITION FIXED: All duplicate bullet points filtered out")
        print("  No content in summary tweet because all bullets were duplicates")
    else:
        # Check if any bullet points from hook appear in summary
        hook_bullets = []
        summary_bullets = []
        
        for bullet_char in ['•', '▪']:
            if bullet_char in hook_tweet:
                hook_bullets.extend([p.strip().lower() for p in hook_tweet.split(bullet_char)[1:]])
            if bullet_char in summary_tweet:
                summary_bullets.extend([p.strip().lower() for p in summary_tweet.split(bullet_char)[1:]])
        
        # Clean up bullet contents for comparison
        hook_bullets = [b.rstrip('.').strip() for b in hook_bullets if b.strip()]
        summary_bullets = [b.rstrip('.').strip() for b in summary_bullets if b.strip()]
        
        overlaps = []
        for hook_bullet in hook_bullets:
            for summary_bullet in summary_bullets:
                if hook_bullet == summary_bullet:
                    overlaps.append(hook_bullet)
        
        if overlaps:
            print(f"❌ BULLET REPETITION STILL EXISTS: {overlaps}")
            return False
        else:
            print("✅ NO BULLET REPETITION: Unique content preserved")
    
    print()
    
    # Test case 2: Mixed content (some duplicate, some unique)
    print("TEST 2: MIXED CONTENT (PARTIAL FILTERING)")
    
    mixed_article = {
        "title": "Mining Company Expansion",
        "body": "Mining expansion news...",
        "url": "https://example.com/expansion",
        "uri": "expansion-uri",
        "gemini_headline": "🏭 Mining Company Expands Operations • 50MW power capacity • New facility", 
        "gemini_summary": "• 50MW power capacity\n• 500 mining rigs\n• Operations start Q2"
    }
    
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(mixed_article)
    
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Summary): {summary_tweet}")
    print()
    
    # Check that duplicate is removed but unique content preserved
    if "50mw power capacity" in summary_tweet.lower():
        print("❌ DUPLICATE NOT FILTERED: '50MW power capacity' should be removed")
        return False
    
    if "500 mining rigs" not in summary_tweet.lower():
        print("❌ UNIQUE CONTENT LOST: '500 mining rigs' should be preserved")
        return False
    
    if "operations start q2" not in summary_tweet.lower():
        print("❌ UNIQUE CONTENT LOST: 'Operations start Q2' should be preserved")
        return False
    
    print("✅ MIXED CONTENT HANDLED CORRECTLY:")
    print("  - Duplicate bullet point filtered out")
    print("  - Unique bullet points preserved")
    
    print()
    
    # Test case 3: No repetition (baseline)
    print("TEST 3: NO REPETITION BASELINE")
    
    no_repeat_article = {
        "title": "Bitcoin Price Update",
        "body": "Price update news...",
        "url": "https://example.com/price",
        "uri": "price-uri",
        "gemini_headline": "📈 Bitcoin Price Reaches New High of $50,000",
        "gemini_summary": "• Market volume up 25%\n• Institutional buying surge\n• Analyst predictions bullish"
    }
    
    hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(no_repeat_article)
    
    print(f"  Tweet 1 (Hook): {hook_tweet}")
    print(f"  Tweet 2 (Summary): {summary_tweet}")
    print()
    
    # Check that all content is preserved when there's no repetition
    expected_content = ["market volume up 25%", "institutional buying surge", "analyst predictions bullish"]
    summary_lower = summary_tweet.lower()
    
    preserved_count = sum(1 for content in expected_content if content in summary_lower)
    
    if preserved_count == len(expected_content):
        print("✅ NO REPETITION SCENARIO: All unique content preserved")
    else:
        print(f"❌ CONTENT INCORRECTLY FILTERED: {preserved_count}/{len(expected_content)} items preserved")
        return False
    
    print()
    print("🎉 ALL BULLET POINT REPETITION TESTS PASSED!")
    print("✅ The exact issue from the problem statement has been fixed")
    return True

if __name__ == "__main__":
    success = test_bullet_repetition_fix()
    sys.exit(0 if success else 1)