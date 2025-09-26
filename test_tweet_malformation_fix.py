#!/usr/bin/env python3
"""
Test to verify the tweet text malformation bug is fixed.

This test specifically addresses the issue where tweet generation creates
malformed text like: "🎯 Bitmain 9 BTC HIVE Digital Technologies Reaches..."
instead of properly formatted headlines.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils, TweetFormatter
from config import BotConstants


def test_company_focused_tweet_formatting():
    """Test that company-focused tweets are formatted properly, not concatenated."""
    
    # Create a test article similar to the HIVE one causing issues
    test_article = {
        "title": "HIVE Digital Technologies Reaches 2% of Global Bitcoin Network, Mining 9 BTC Daily and Surpassing 20 EH/s",
        "body": "HIVE Digital Technologies Ltd. announced it has exceeded 20 Exahash per second of global Bitcoin mining capacity following the deployment of ASICs at its Phase 3 Valenzuela facility in Paraguay...",
        "url": "https://example.com/hive-news"
    }
    
    # Test the original problematic case
    tweet_text = TextUtils.create_tweet_text(test_article)
    
    print(f"Generated tweet text: {tweet_text}")
    print(f"Length: {len(tweet_text)} characters")
    
    # Assertions to ensure proper formatting
    assert len(tweet_text) <= BotConstants.TWEET_MAX_LENGTH, f"Tweet too long: {len(tweet_text)} > {BotConstants.TWEET_MAX_LENGTH}"
    
    # Should not have malformed concatenation like "Bitmain 9 BTC HIVE Digital..."
    # The issue was raw concatenation without proper formatting
    assert not ("Bitmain 9 BTC HIVE" in tweet_text), "Tweet still contains malformed concatenation"
    
    # Should have proper structure with prefix emoji
    assert tweet_text.startswith(tuple(BotConstants.TWEET_PREFIXES)), "Tweet should start with emoji prefix"
    
    # Should be readable - check for proper spacing and structure
    # After prefix, should not have strange concatenations
    content_after_prefix = tweet_text[2:]  # Remove emoji prefix
    words = content_after_prefix.split()
    
    # Should not have obvious malformed patterns
    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        
        # Check for patterns like "Bitmain 9" followed by "BTC"
        if current_word == "9" and next_word == "BTC":
            # This should be part of a proper sentence, not raw concatenation
            # Look for context around it
            if i > 0:
                prev_word = words[i - 1]
                # "Bitmain 9 BTC Title" is malformed
                # "Mining 9 BTC daily" or "announces 9 BTC deal" is proper
                assert prev_word not in ["Bitmain", "CleanSpark", "HIVE", "IREN"], \
                    f"Found malformed concatenation: {prev_word} {current_word} {next_word}"
    
    print("✅ Tweet formatting is correct and readable")


def test_company_focused_tweet_with_financial_amount():
    """Test that company + financial amount integration works properly."""
    
    # Create test with clear company and financial info
    test_article = {
        "title": "Bitcoin Mining Company Expands Operations", 
        "body": "The company announced a $50 million investment in new mining facilities...",
        "concepts": [{"label": {"eng": "Bitcoin"}}]
    }
    
    # Simulate the info extraction that would happen
    from utils import TextUtils
    info = TextUtils.extract_key_info(test_article)
    
    # Manually add what would be extracted to test the logic
    info["companies"] = ["TestMiningCorp"]
    info["financial_amounts"] = ["$50 million"]
    
    # Test the company-focused tweet creation
    result = TweetFormatter._create_company_focused_tweet(test_article, info)
    
    print(f"Company-focused tweet: {result}")
    
    # Should have proper format like "TestMiningCorp announces $50 million: Bitcoin Mining Company Expands Operations"
    assert "TestMiningCorp announces $50 million:" in result, "Should have proper 'announces' formatting"
    
    # Should not have raw concatenation
    assert "TestMiningCorp $50 million Bitcoin" not in result, "Should not have raw concatenation"
    
    print("✅ Company + financial amount formatting is correct")


def test_news_focused_tweet_formatting():
    """Test news-focused tweet formatting doesn't have similar issues."""
    
    test_article = {
        "title": "Major Bitcoin Mining Expansion Announced",
        "body": "New facilities will house 5000 miners producing 100 TH/s total capacity...",
        "concepts": [{"label": {"eng": "Bitcoin"}}]
    }
    
    # Simulate info extraction
    info = {
        "companies": [],
        "financial_amounts": ["$100 million"], 
        "technical_specs": ["5000 miners", "100 TH/s"]
    }
    
    result = TweetFormatter._create_news_focused_tweet(test_article, info)
    
    print(f"News-focused tweet: {result}")
    
    # Should have proper separator format
    assert " - " in result, "Should use proper separator for enhancements"
    
    # Should not have raw concatenation
    words = result.split()
    for word in words:
        if word == "$100":
            # Should be followed by "million" not random text
            word_index = words.index(word)
            if word_index < len(words) - 1:
                next_word = words[word_index + 1]
                assert next_word == "million" or next_word.startswith("million"), \
                    f"Financial amount should be properly formatted, not '{word} {next_word}'"
    
    print("✅ News-focused tweet formatting is correct")


def test_real_queued_article():
    """Test with actual queued article data to ensure it works in practice."""
    
    # Use the HIVE article from the queue that was causing issues
    hive_article = {
        "uri": "2025-09-842254438",
        "title": "HIVE Digital Technologies Reaches 2% of Global Bitcoin Network, Mining 9 BTC Daily and Surpassing 20 EH/s",
        "body": "San Antonio, Texas--(Newsfile Corp. - September 24, 2025) - HIVE Digital Technologies Ltd. (TSXV: HIVE) (NASDAQ: HIVE) (FSE: YO0) (the \"Company\" or \"HIVE\"), a diversified multinational digital infrastructure company, today announced it has exceeded 20 Exahash per second (\"EH/s\") of global Bitcoin mining capacity following the continued successful deployment of ASICs at its Phase 3 Valenzuela facility in Paraguay.",
        "url": "https://www.wallstreet-online.de/nachricht/19959542-hive-digital-technologies-reaches-2-of-global-bitcoin-network-mining-9-btc-daily-and-surpassing-20-eh-s",
        "source": {"title": "wallstreet:online"},
        "concepts": [
            {"label": {"eng": "Bitcoin network"}},
            {"label": {"eng": "Bitcoin"}},
            {"label": {"eng": "Mining"}}
        ]
    }
    
    # Test tweet generation
    result = TextUtils.create_tweet_text(hive_article)
    
    print(f"Real article tweet: {result}")
    print(f"Length: {len(result)}")
    
    # Should not be malformed
    assert not result.startswith("🎯 Bitmain 9 BTC HIVE"), "Should not have the original malformed pattern"
    assert len(result) <= BotConstants.TWEET_MAX_LENGTH, "Should fit Twitter limits"
    
    # Should be readable
    assert any(result.startswith(prefix) for prefix in BotConstants.TWEET_PREFIXES), "Should have emoji prefix"
    
    print("✅ Real article processes correctly")


if __name__ == "__main__":
    print("Testing tweet text malformation fixes...")
    print("=" * 60)
    
    test_company_focused_tweet_formatting()
    print()
    
    test_company_focused_tweet_with_financial_amount()
    print()
    
    test_news_focused_tweet_formatting() 
    print()
    
    test_real_queued_article()
    print()
    
    print("=" * 60)
    print("🎉 All tests passed! Tweet malformation bug is fixed.")