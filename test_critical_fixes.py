#!/usr/bin/env python3
"""
Test script to demonstrate the critical fixes for:
1. Ether/Ethereum filtering
2. Gemini metadata exposure prevention
3. Content validation before posting
"""

import sys
from core import BitcoinMiningBot, Config, Article, NewsAPI, GeminiClient

def test_ether_articles():
    """Test that ether/ethereum articles are properly filtered."""
    print("\n🧪 Testing Ether/Ethereum Filtering")
    print("=" * 60)
    
    config = Config()
    news_api = NewsAPI(config)
    
    # Test case 1: Article with "ether" in title
    test_articles = [
        {
            "title": "Bit Digital Pivots, Amasses $500M Ether Post-Mining Exit",
            "body": "Company transitions to Ethereum staking operations",
            "url": "https://example.com/ether1",
            "expected": False,
            "reason": "Contains 'ether' in title"
        },
        {
            "title": "Ethereum Mining Shifts to Proof of Stake",
            "body": "Ethereum network completes merge",
            "url": "https://example.com/ethereum1",
            "expected": False,
            "reason": "Contains 'ethereum' in title"
        },
        {
            "title": "Bitcoin Mining Operations Expand",
            "body": "Marathon Digital expands bitcoin mining operations",
            "url": "https://example.com/bitcoin1",
            "expected": True,
            "reason": "Valid Bitcoin mining article"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_articles:
        article_data = {
            "title": test_case["title"],
            "body": test_case["body"],
            "url": test_case["url"],
            "uri": test_case["url"],
            "source": {"title": "Test"},
            "dateTimePub": "2024-01-01T12:00:00Z"
        }
        article = Article.from_dict(article_data)
        is_relevant = news_api._is_bitcoin_relevant(article)
        
        if is_relevant == test_case["expected"]:
            print(f"✅ PASS: {test_case['title'][:50]}")
            print(f"   Reason: {test_case['reason']}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_case['title'][:50]}")
            print(f"   Expected: {test_case['expected']}, Got: {is_relevant}")
            print(f"   Reason: {test_case['reason']}")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_articles)} passed")
    return failed == 0

def test_gemini_metadata():
    """Test that Gemini metadata is properly filtered."""
    print("\n🧪 Testing Gemini Metadata Filtering")
    print("=" * 60)
    
    gemini = object.__new__(GeminiClient)
    
    test_cases = [
        {
            "input": "Okay, I have the article content. Now I need to find three facts...",
            "should_contain": "Bitcoin mining sector update",
            "reason": "Pure internal processing should return fallback"
        },
        {
            "input": "• Marathon Digital expands operations\n• Revenue increased 42%\n• Hash rate improved",
            "should_contain": "Marathon Digital",
            "reason": "Valid bullet points should be preserved"
        },
        {
            "input": "Now let's identify what not to repeat.\n• Q3 revenue increased 50% year-over-year\n• New facility opened in Texas this month\n• Hash rate doubled to 5 EH/s",
            "should_contain": "Q3 revenue increased",
            "reason": "Mixed content should preserve bullet points"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = gemini._process_summary_response(test_case["input"])
        
        if test_case["should_contain"] in result:
            print(f"✅ PASS: {test_case['reason']}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_case['reason']}")
            print(f"   Expected to contain: {test_case['should_contain']}")
            print(f"   Got: {result[:100]}...")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0

def test_content_validation():
    """Test that content validation catches forbidden patterns."""
    print("\n🧪 Testing Content Validation")
    print("=" * 60)
    
    config = Config()
    bot = BitcoinMiningBot(config=config)
    
    test_cases = [
        {
            "content": "Okay, I have analyzed the article",
            "should_pass": False,
            "reason": "Contains internal processing language"
        },
        {
            "content": "The article states that Marathon Digital is expanding",
            "should_pass": False,
            "reason": "Contains meta-language"
        },
        {
            "content": "Ethereum mining operations are growing",
            "should_pass": False,
            "reason": "Contains altcoin mention"
        },
        {
            "content": "Marathon Digital Expands Mining Operations",
            "should_pass": True,
            "reason": "Valid Bitcoin mining content"
        },
        {
            "content": "BREAKING: CleanSpark Reports Record Revenue",
            "should_pass": True,
            "reason": "Valid headline format"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = bot._validate_content_before_posting(test_case["content"])
        
        if result == test_case["should_pass"]:
            status = "✅ PASS" if test_case["should_pass"] else "✅ PASS (correctly rejected)"
            print(f"{status}: {test_case['reason']}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_case['reason']}")
            print(f"   Expected: {test_case['should_pass']}, Got: {result}")
            print(f"   Content: {test_case['content'][:60]}...")
            failed += 1
    
    print(f"\nResults: {passed}/{len(test_cases)} passed")
    return failed == 0

def main():
    """Run all critical fix tests."""
    print("\n" + "=" * 60)
    print("CRITICAL FIXES VERIFICATION TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("Ether/Ethereum Filtering", test_ether_articles()))
    results.append(("Gemini Metadata Filtering", test_gemini_metadata()))
    results.append(("Content Validation", test_content_validation()))
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL CRITICAL FIXES VERIFIED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please review above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
