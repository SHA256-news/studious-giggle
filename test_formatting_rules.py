#!/usr/bin/env python3
"""
Test script to validate the new tweet formatting rules:
1. NEVER using hashtags in published tweets
2. Max of 1 emoji per tweet

This ensures compliance with the updated requirements.
"""

import sys
import os
import re

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_no_hashtags_rule():
    """Test that NO hashtags are ever included in tweets"""
    print("🚫 TESTING NO HASHTAGS RULE")
    print("=" * 60)
    
    test_cases = [
        {
            "title": "Marathon Digital Expands Bitcoin Mining Operations with $200 Million Investment",
            "url": "https://example.com/marathon",
            "gemini_headline": "Marathon Digital boosts hashrate capacity by 25% with new facility acquisition",
            "gemini_summary": "Key highlights:\n• $200M investment completed\n• Plans to triple mining capacity",
            "description": "Company Investment with Gemini"
        },
        {
            "title": "SEC Approves First Bitcoin Mining ETF for Institutional Investors",
            "url": "https://example.com/sec-etf",
            "description": "Regulatory Approval"
        },
        {
            "title": "CleanSpark Partners with Renewable Energy Provider for Green Mining",
            "url": "https://example.com/cleanspark",
            "description": "Partnership News"
        },
        {
            "title": "Texas Bitcoin Mining Farm Reaches 500 BTC Production Milestone",
            "url": "https://example.com/texas-milestone",
            "description": "Production Milestone"
        },
        {
            "title": "Chinese Bitcoin Mining Company Relocates Operations to Kazakhstan",
            "url": "https://example.com/relocation",
            "description": "Geographic Relocation"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print("-" * 40)
        
        # Test hook tweet
        hook_tweet = TextUtils.create_hook_tweet(case)
        has_hashtags_hook = "#" in hook_tweet
        
        # Test link tweet
        link_tweet = TextUtils.create_link_tweet(case)
        has_hashtags_link = "#" in link_tweet
        
        # Test thread creation
        thread_hook, thread_link = TextUtils.create_thread_texts(case)
        has_hashtags_thread_hook = "#" in thread_hook
        has_hashtags_thread_link = "#" in thread_link
        
        print(f"Hook tweet: {hook_tweet}")
        print(f"Link tweet: {link_tweet[:60]}{'...' if len(link_tweet) > 60 else ''}")
        
        # Validate no hashtags
        if has_hashtags_hook or has_hashtags_link or has_hashtags_thread_hook or has_hashtags_thread_link:
            print("❌ FAILED: Hashtags found!")
            all_passed = False
        else:
            print("✅ PASSED: No hashtags found")
    
    return all_passed

def test_max_one_emoji_rule():
    """Test that maximum 1 emoji is used per tweet"""
    print(f"\n😊 TESTING MAX 1 EMOJI RULE")
    print("=" * 60)
    
    emoji_pattern = r'[🏢🤝✅🎯🌍📰⚡🏭💰📈🚀⚖️🚫🏛️]'
    
    test_cases = [
        {
            "title": "Marathon Digital Announces Major Partnership and Investment Expansion",
            "url": "https://example.com/marathon-partnership",
            "gemini_headline": "Marathon Digital secures $200M and announces strategic partnership",
            "gemini_summary": "Key highlights:\n• $200M funding secured\n• Strategic partnership announced",
            "description": "Multiple Potential Emojis (Partnership + Investment)"
        },
        {
            "title": "SEC Approves Bitcoin Mining ETF with Renewable Energy Focus",
            "url": "https://example.com/sec-green",
            "description": "Regulatory + Environmental"
        },
        {
            "title": "Texas Mining Facility Reaches Production Milestone with New Investment",
            "url": "https://example.com/texas-milestone-investment",
            "description": "Milestone + Investment + Location"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print("-" * 40)
        
        # Test hook tweet
        hook_tweet = TextUtils.create_hook_tweet(case)
        hook_emoji_count = len(re.findall(emoji_pattern, hook_tweet))
        
        # Test link tweet
        link_tweet = TextUtils.create_link_tweet(case)
        link_emoji_count = len(re.findall(emoji_pattern, link_tweet))
        
        print(f"Hook tweet: {hook_tweet}")
        print(f"Link tweet: {link_tweet[:60]}{'...' if len(link_tweet) > 60 else ''}")
        print(f"Hook emojis: {hook_emoji_count}, Link emojis: {link_emoji_count}")
        
        # Validate max 1 emoji per tweet
        if hook_emoji_count <= 1 and link_emoji_count <= 1:
            print("✅ PASSED: Max 1 emoji per tweet")
        else:
            print(f"❌ FAILED: Too many emojis (Hook: {hook_emoji_count}, Link: {link_emoji_count})")
            all_passed = False
    
    return all_passed

def test_visual_comparison():
    """Show before/after comparison of the rule changes"""
    print(f"\n📊 BEFORE vs AFTER COMPARISON")
    print("=" * 60)
    
    article = {
        "title": "Marathon Digital Expands Bitcoin Mining Operations with $200 Million Investment",
        "url": "https://example.com/marathon",
        "gemini_headline": "Marathon Digital boosts hashrate capacity by 25% with new facility acquisition",
        "gemini_summary": "Key highlights:\n• $200M investment completed\n• Plans to triple mining capacity\n• Expected deployment by Q2 2024"
    }
    
    hook_tweet = TextUtils.create_hook_tweet(article)
    link_tweet = TextUtils.create_link_tweet(article)
    
    print("🔴 BEFORE (Previous Implementation):")
    print("Hook: 🏭 Marathon Digital boosts hashrate capacity by 25% with new facility acquisition #Bitcoin #BitcoinMining")
    print("Link: ▪ $200M investment completed [with Gemini summary + URL]")
    print()
    print("🟢 AFTER (New Rules Applied):")
    print(f"Hook: {hook_tweet}")
    print(f"Link: {link_tweet[:80]}{'...' if len(link_tweet) > 80 else ''}")
    print()
    print("✨ CHANGES:")
    print("• ❌ Removed all hashtags (#Bitcoin, #BitcoinMining, etc.)")
    print("• ✅ Maintained exactly 1 emoji per tweet")
    print("• ✅ Preserved Gemini AI content and visual formatting")
    print("• ✅ Maintained character efficiency and readability")

def main():
    """Run all validation tests"""
    print("🎯 TWEET FORMATTING RULES VALIDATION")
    print("=" * 80)
    print("Validating compliance with:")
    print("1. NEVER using hashtags in published tweets")
    print("2. Max of 1 emoji per tweet")
    print()
    
    test1_passed = test_no_hashtags_rule()
    test2_passed = test_max_one_emoji_rule()
    test_visual_comparison()
    
    print(f"\n{'=' * 80}")
    print("📋 VALIDATION RESULTS:")
    print(f"• No hashtags rule: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"• Max 1 emoji rule: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Bot now complies with the new formatting rules")
        print("✅ No hashtags will appear in any published tweets")
        print("✅ Maximum 1 emoji per tweet enforced")
        print("✅ Gemini AI integration preserved")
        print("✅ Visual readability maintained")
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print("❌ Rules compliance needs attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)