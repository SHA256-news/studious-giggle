#!/usr/bin/env python3
"""
Test script for enhanced tweet text creation functionality
"""

import os
import unittest.mock as mock
from utils import TextUtils


def test_enhanced_tweet_formatting():
    """Test enhanced tweet text creation with various scenarios"""
    print("Testing enhanced tweet formatting...")
    
    # Test case 1: Company investment scenario (like the example in the problem statement)
    test_article_1 = {
        "title": "200 BTC Annually: Hong Kong's Investment Holding Company Sets To Bitcoin Mining",
        "body": "DL Holdings, a Hong Kong-based investment holding company, has announced a $21.85 million investment in Bitcoin mining operations through a bond agreement with Fortune Peak. The company expects to generate approximately 200 BTC annually from their planned deployment of over 2,200 mining rigs.",
        "uri": "test-uri-1"
    }
    
    # Test case 2: Mining expansion scenario
    test_article_2 = {
        "title": "Texas Bitcoin Mining Farm Expands Operations with 100 New Rigs",
        "body": "A major mining facility in Texas has announced the expansion of its operations with the addition of 100 new mining rigs, representing a $5 million investment. The facility aims to increase its hashrate by 10 TH/s.",
        "uri": "test-uri-2"
    }
    
    # Test case 3: Regulatory news
    test_article_3 = {
        "title": "SEC Approves First Bitcoin Mining ETF Application",
        "body": "The Securities and Exchange Commission has approved the first Bitcoin mining ETF, marking a significant milestone for the industry.",
        "uri": "test-uri-3"
    }
    
    # Test case 4: Partnership announcement
    test_article_4 = {
        "title": "Riot Platforms Partners with CleanSpark for Renewable Energy Mining",
        "body": "Riot Platforms has announced a strategic partnership with CleanSpark to develop renewable energy-powered Bitcoin mining operations worth $50 million.",
        "uri": "test-uri-4"
    }
    
    test_cases = [
        (test_article_1, "Should include company name, investment amount, and technical specs"),
        (test_article_2, "Should include location, expansion details, and investment amount"),
        (test_article_3, "Should include regulatory body and significance"),
        (test_article_4, "Should include both companies and partnership value")
    ]
    
    for article, description in test_cases:
        tweet_text = TextUtils.create_enhanced_tweet_text(article)
        
        print(f"\nOriginal title: {article['title']}")
        print(f"Enhanced tweet: {tweet_text}")
        print(f"Character count: {len(tweet_text)}")
        print(f"Test case: {description}")
        
        # Validate constraints
        assert isinstance(tweet_text, str), "Tweet text should be a string"
        assert len(tweet_text) <= 280, f"Tweet text too long: {len(tweet_text)} chars"
        assert len(tweet_text) > 0, "Tweet text should not be empty"
        
        # Check that abbreviations are applied
        if "Bitcoin" in article["title"] and "BTC" not in article["title"]:
            assert "BTC" in tweet_text, "Should use BTC abbreviation"
        
        print("✓ Enhanced tweet formatted correctly")
    
    return True


def test_key_information_extraction():
    """Test that key information is correctly extracted from articles"""
    print("\nTesting key information extraction...")
    
    test_article = {
        "title": "DL Holdings Invests $21.85 Million in Bitcoin Mining with Fortune Peak",
        "body": "The company plans to deploy 2,200+ miners to generate 200 BTC annually.",
        "uri": "test-uri"
    }
    
    info = TextUtils.extract_key_info(test_article)
    
    print(f"Extracted info: {info}")
    
    # Validate extraction
    assert isinstance(info, dict), "Should return a dictionary"
    assert "financial_amounts" in info, "Should extract financial amounts"
    assert "technical_specs" in info, "Should extract technical specs"
    assert "companies" in info, "Should extract companies"
    
    # Check specific extractions
    assert any("$21.85" in amount for amount in info["financial_amounts"]), "Should extract dollar amount"
    assert any("200 BTC" in spec or "2,200" in spec for spec in info["technical_specs"]), "Should extract technical specs"
    
    print("✓ Key information extracted correctly")
    return True


def test_abbreviation_system():
    """Test the abbreviation system"""
    print("\nTesting abbreviation system...")
    
    test_cases = [
        ("Bitcoin mining with 5 million dollars", "BTC mining w/ 5 M dollars"),
        ("Investment company announces partnership", "Invest co announces partnership"),
        ("Mining operations targeting 100 Bitcoin per year", "Mining operations targeting 100 BTC per yr")
    ]
    
    for original, expected_pattern in test_cases:
        result = TextUtils._apply_abbreviations(original)
        print(f"Original: {original}")
        print(f"Abbreviated: {result}")
        
        # Check that key abbreviations are applied
        if "Bitcoin" in original:
            assert "BTC" in result, "Should abbreviate Bitcoin to BTC"
        if "with" in original:
            assert "w/" in result, "Should abbreviate with to w/"
        if "million" in original:
            assert "M" in result, "Should abbreviate million to M"
        
        print("✓ Abbreviations applied correctly")
    
    return True


def test_backward_compatibility():
    """Test that the system falls back gracefully"""
    print("\nTesting backward compatibility...")
    
    # Test with minimal article (should fall back to original method)
    minimal_article = {"title": "Simple Bitcoin News", "uri": "test-uri"}
    
    tweet_text = TextUtils.create_tweet_text(minimal_article)
    print(f"Minimal article tweet: {tweet_text}")
    
    assert isinstance(tweet_text, str), "Should return string"
    assert len(tweet_text) <= 280, "Should respect character limit"
    assert len(tweet_text) > 0, "Should not be empty"
    
    # Test with None title (should fall back gracefully)
    none_article = {"title": None, "uri": "test-uri"}
    tweet_text = TextUtils.create_tweet_text(none_article)
    print(f"None title tweet: {tweet_text}")
    
    assert isinstance(tweet_text, str), "Should return string even with None title"
    
    print("✓ Backward compatibility maintained")
    return True


def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Tweet Text Creation")
    print("=" * 50)
    
    try:
        test_enhanced_tweet_formatting()
        test_key_information_extraction()
        test_abbreviation_system()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("✅ All enhanced tweet tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)