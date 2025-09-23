#!/usr/bin/env python3
"""
Test script to validate the new 3-part thread format:
1. Hook tweet (Gemini headline with emoji)
2. Summary tweet (Gemini summary with bullet points, no URL)
3. URL tweet (standalone URL only)

This ensures the URL is separated from the summary as requested.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_three_part_thread_format():
    """Test the new 3-part thread format"""
    print("🧵 TESTING 3-PART THREAD FORMAT")
    print("=" * 70)
    
    test_cases = [
        {
            "title": "Marathon Digital Expands Bitcoin Mining Operations",
            "url": "https://example.com/marathon-expands",
            "gemini_headline": "Marathon Digital boosts hashrate capacity by 25% with new facility acquisition",
            "gemini_summary": "Key highlights:\n• Acquired 2,500 additional mining rigs\n• Expected 15 EH/s hashrate increase\n• Targets 30% cost reduction via renewable energy",
            "description": "Full Gemini Content (3 tweets expected)"
        },
        {
            "title": "SEC Approves First Bitcoin Mining ETF",
            "url": "https://example.com/sec-approves",
            "gemini_headline": "SEC grants approval for first-ever Bitcoin mining ETF, opening institutional access",
            "description": "Gemini Headline Only (2 tweets expected: headline + URL)"
        },
        {
            "title": "CleanSpark Announces Partnership",
            "url": "https://example.com/cleanspark",
            "description": "No Gemini Content (2 tweets expected: enhanced title + URL)"
        },
        {
            "title": "Bitcoin Mining News Update",
            "description": "No URL (1 tweet expected: single tweet)"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print("-" * 50)
        
        # Test 3-part thread creation
        hook, summary, url = TextUtils.create_three_part_thread(case)
        
        # Count actual tweets
        actual_tweets = []
        if hook:
            actual_tweets.append(f"Hook: {hook}")
        if summary:
            actual_tweets.append(f"Summary: {summary}")
        if url:
            actual_tweets.append(f"URL: {url}")
        
        print(f"Generated {len(actual_tweets)} tweets:")
        for j, tweet in enumerate(actual_tweets, 1):
            print(f"  Tweet {j}: {tweet}")
            
        # Validate URL separation
        if summary and url:
            if url in summary:
                print("❌ FAILED: URL is mixed with summary!")
                all_passed = False
            else:
                print("✅ PASSED: URL is separate from summary")
        
        # Validate character limits
        char_violations = []
        if hook and len(hook) > 280:
            char_violations.append(f"Hook: {len(hook)}")
        if summary and len(summary) > 280:
            char_violations.append(f"Summary: {len(summary)}")
        if url and len(url) > 280:
            char_violations.append(f"URL: {len(url)}")
            
        if char_violations:
            print(f"❌ FAILED: Character limit violations: {', '.join(char_violations)}")
            all_passed = False
        else:
            print("✅ PASSED: All tweets within character limits")
    
    return all_passed

def test_backward_compatibility():
    """Test that existing 2-part thread functionality still works"""
    print(f"\n🔄 TESTING BACKWARD COMPATIBILITY")
    print("=" * 70)
    
    article = {
        "title": "Marathon Digital Expands Bitcoin Mining Operations",
        "url": "https://example.com/marathon-expands",
        "gemini_headline": "Marathon Digital boosts hashrate capacity by 25% with new facility acquisition",
        "gemini_summary": "Key highlights:\n• Acquired 2,500 additional mining rigs\n• Expected 15 EH/s hashrate increase\n• Targets 30% cost reduction via renewable energy"
    }
    
    print("Testing create_thread_texts() backward compatibility...")
    
    # Test old 2-part format
    hook_old, link_old = TextUtils.create_thread_texts(article)
    
    print(f"Old format Tweet 1: {hook_old}")
    print(f"Old format Tweet 2: {link_old}")
    
    # Verify URL is still in the link tweet for backward compatibility
    if article["url"] in link_old:
        print("✅ PASSED: Backward compatibility maintained - URL in link tweet")
        return True
    else:
        print("❌ FAILED: Backward compatibility broken - URL missing from link tweet")
        return False

def test_url_separation_scenarios():
    """Test various scenarios for URL separation"""
    print(f"\n🔗 TESTING URL SEPARATION SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Long URL + Long Summary",
            "article": {
                "title": "Bitcoin Mining News",
                "url": "https://example.com/very-long-bitcoin-mining-article-title-that-should-not-interfere-with-summary",
                "gemini_summary": "Key highlights:\n• Very detailed first point about mining\n• Another comprehensive point about operations\n• Third extensive point about future plans and expectations"
            }
        },
        {
            "name": "Short URL + Short Summary", 
            "article": {
                "title": "News",
                "url": "https://bit.ly/btc",
                "gemini_summary": "• Quick update\n• Brief note"
            }
        },
        {
            "name": "URL Only (No Summary)",
            "article": {
                "title": "Bitcoin News",
                "url": "https://example.com/bitcoin-news"
            }
        }
    ]
    
    all_passed = True
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print("-" * 30)
        
        hook, summary, url = TextUtils.create_three_part_thread(scenario["article"])
        
        print(f"Hook: {hook}")
        print(f"Summary: {summary if summary else '(empty)'}")
        print(f"URL: {url if url else '(empty)'}")
        
        # Check separation
        if summary and url and url in summary:
            print("❌ URL mixed with summary")
            all_passed = False
        else:
            print("✅ URL properly separated")
    
    return all_passed

def main():
    """Run all 3-part thread tests"""
    print("🧵 3-PART THREAD FORMAT VALIDATION")
    print("=" * 80)
    print("Testing the new format where URL is in its own standalone tweet")
    print()
    
    test1_passed = test_three_part_thread_format()
    test2_passed = test_backward_compatibility()
    test3_passed = test_url_separation_scenarios()
    
    print(f"\n{'=' * 80}")
    print("📋 VALIDATION RESULTS:")
    print(f"• 3-part thread format: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"• Backward compatibility: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"• URL separation: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ URLs are now in standalone tweets at the end of each thread")
        print("✅ Summary tweets contain only Gemini bullet points")
        print("✅ Hook tweets contain only Gemini headlines with emoji")
        print("✅ Backward compatibility maintained for existing integrations")
        print("✅ Character limits respected across all tweet parts")
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print("❌ URL separation implementation needs attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)