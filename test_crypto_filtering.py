#!/usr/bin/env python3
"""
Test cryptocurrency filtering functionality for Bitcoin Mining News Bot
"""

import unittest.mock as mock
from crypto_filter import filter_bitcoin_only_articles, contains_unwanted_crypto


def test_crypto_filter_basic():
    """Test basic cryptocurrency filtering functionality"""
    print("Testing basic cryptocurrency filtering...")
    
    # Test articles - mix of Bitcoin-only and multi-crypto
    test_articles = [
        {
            "title": "Bitcoin Mining Facility Opens in Texas",
            "body": "A new Bitcoin mining facility has opened in Texas with 50 MW capacity.",
            "url": "https://example.com/btc-texas",
            "uri": "test-btc-1"
        },
        {
            "title": "Ethereum Mining Gets Harder with Proof of Stake",
            "body": "Ethereum miners are struggling as the network transitions to PoS.",
            "url": "https://example.com/eth-pos",
            "uri": "test-eth-1"
        },
        {
            "title": "XRP Mining Drives Unprecedented Returns",
            "body": "Come Mining platform shows XRP mining profitability rising.",
            "url": "https://example.com/xrp-mining",
            "uri": "test-xrp-1"
        },
        {
            "title": "Bitcoin Hashrate Reaches New All-Time High",
            "body": "Bitcoin network hashrate has reached a new peak at 500 EH/s.",
            "url": "https://example.com/btc-hashrate",
            "uri": "test-btc-2"
        },
        {
            "title": "Cloud Mining Apps Support Bitcoin, ETH, and Litecoin",
            "body": "New cloud mining platform supports multiple cryptocurrencies including Bitcoin, Ethereum, and Litecoin.",
            "url": "https://example.com/multi-crypto",
            "uri": "test-multi-1"
        }
    ]
    
    # Filter the articles
    filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(test_articles)
    
    # Should keep only Bitcoin-only articles (2 out of 5)
    assert len(filtered_articles) == 2, f"Expected 2 Bitcoin-only articles, got {len(filtered_articles)}"
    assert excluded_count == 3, f"Expected 3 excluded articles, got {excluded_count}"
    
    # Check that the correct articles were kept
    kept_titles = [article['title'] for article in filtered_articles]
    assert "Bitcoin Mining Facility Opens in Texas" in kept_titles
    assert "Bitcoin Hashrate Reaches New All-Time High" in kept_titles
    
    # Check that the correct articles were excluded
    excluded_titles = [detail['title'] for detail in excluded_details]
    assert any("Ethereum" in title for title in excluded_titles)
    assert any("XRP" in title for title in excluded_titles)
    assert any("ETH" in title for title in excluded_titles)
    
    print("✓ Basic cryptocurrency filtering test passed")
    return True


def test_individual_crypto_detection():
    """Test individual cryptocurrency detection"""
    print("Testing individual cryptocurrency detection...")
    
    test_cases = [
        ("Bitcoin mining facility opens", False),  # Should pass
        ("Ethereum mining gets harder", True),     # Should fail - Ethereum
        ("XRP mining unprecedented returns", True), # Should fail - XRP
        ("BTC hashrate reaches new high", False),  # Should pass - BTC is Bitcoin
        ("Multiple cryptocurrencies platform", True), # Should fail - generic multi-crypto
        ("Mine Bitcoin and several altcoins", True),  # Should fail - altcoins
        ("Dogecoin mining comparison", True),      # Should fail - Dogecoin
        ("Bitcoin Lightning Network update", False), # Should pass - Lightning is Bitcoin L2
        ("Cloud mining supports ETH and LTC", True), # Should fail - ETH, LTC
    ]
    
    for text, should_be_filtered in test_cases:
        is_filtered = contains_unwanted_crypto(text)
        if is_filtered != should_be_filtered:
            print(f"❌ FAILED: '{text}' - Expected filtered={should_be_filtered}, got {is_filtered}")
            return False
        else:
            status = "❌ FILTERED" if is_filtered else "✅ ALLOWED"
            print(f"  {status}: {text}")
    
    print("✓ Individual cryptocurrency detection test passed")
    return True


def test_edge_cases():
    """Test edge cases in cryptocurrency filtering"""
    print("Testing edge cases...")
    
    # Test None/empty inputs
    filtered, excluded_count, excluded_details = filter_bitcoin_only_articles([])
    assert len(filtered) == 0 and excluded_count == 0
    
    # Test articles with missing fields
    articles_with_missing_fields = [
        {"title": "Bitcoin Mining News", "body": None, "url": "https://example.com"},
        {"title": None, "body": "Bitcoin mining facility", "url": "https://example.com"},
        {"body": "Bitcoin mining", "url": "https://example.com"},  # Missing title
    ]
    
    filtered, excluded_count, excluded_details = filter_bitcoin_only_articles(articles_with_missing_fields)
    assert len(filtered) == 3, "Should handle missing fields gracefully"
    
    # Test case sensitivity
    assert contains_unwanted_crypto("ETHEREUM mining") == True
    assert contains_unwanted_crypto("ethereum MINING") == True
    assert contains_unwanted_crypto("EtHeReUm mining") == True
    
    print("✓ Edge cases test passed")
    return True


def test_bitcoin_variants_allowed():
    """Test that Bitcoin variants are correctly allowed"""
    print("Testing Bitcoin variants are allowed...")
    
    bitcoin_variants = [
        "Bitcoin mining",
        "BTC mining", 
        "bitcoin miner",
        "Bitcoin miners",
        "Bitcoin hashrate",
        "Bitcoin difficulty",
        "Bitcoin network",
        "Bitcoin blockchain",
        "Bitcoin mining pool",
        "Bitcoin mining farm",
        "Bitcoin mining hardware",
        "Bitcoin mining software",
        "Bitcoin mining rig",
        "Proof of Work Bitcoin",
        "Bitcoin SHA-256",
    ]
    
    for variant in bitcoin_variants:
        if contains_unwanted_crypto(variant):
            print(f"❌ FAILED: '{variant}' should be allowed but was filtered")
            return False
        else:
            print(f"  ✅ ALLOWED: {variant}")
    
    print("✓ Bitcoin variants test passed")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("CRYPTOCURRENCY FILTERING TESTS")
    print("=" * 60)
    
    success = True
    success &= test_crypto_filter_basic()
    success &= test_individual_crypto_detection() 
    success &= test_edge_cases()
    success &= test_bitcoin_variants_allowed()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL CRYPTOCURRENCY FILTERING TESTS PASSED!")
        print("The bot will now only tweet about Bitcoin mining news.")
    else:
        print("❌ SOME TESTS FAILED!")
        exit(1)
    print("=" * 60)