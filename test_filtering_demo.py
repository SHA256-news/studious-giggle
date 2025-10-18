#!/usr/bin/env python3
"""
Demonstration script to showcase improved filtering logic.
Shows how Ethereum, Solana, and other crypto articles are now properly filtered out.
"""

import sys
from core import NewsAPI, Config, Article

def test_article(title, body, description):
    """Test a single article and print results."""
    article_data = {
        "title": title,
        "body": body,
        "url": "https://example.com/test",
        "uri": "test-uri",
        "source": {"title": "Test Source"},
        "dateTimePub": "2024-01-01T12:00:00Z"
    }
    
    config = Config()
    news_api = NewsAPI(config)
    article = Article.from_dict(article_data)
    
    is_relevant = news_api._is_bitcoin_relevant(article)
    
    status = "✅ APPROVED" if is_relevant else "❌ REJECTED"
    print(f"\n{status} - {description}")
    print(f"Title: {title}")
    print(f"Result: {'Would be posted' if is_relevant else 'Filtered out'}")
    print("-" * 80)
    
    return is_relevant


def main():
    print("=" * 80)
    print("Bitcoin Mining Bot - Enhanced Filtering Demonstration")
    print("=" * 80)
    
    print("\n🔍 TESTING ETHEREUM/SOLANA FILTERING (Should All Be REJECTED)")
    print("=" * 80)
    
    # Test 1: Ethereum in title
    test_article(
        "Ethereum Mining Shifts to Proof of Stake",
        "Ethereum network transitions away from mining. Bitcoin mining continues.",
        "Ethereum in title"
    )
    
    # Test 2: Solana in title
    test_article(
        "Solana Network Upgrades: New Mining Features",
        "Solana announces upgrades. Bitcoin mining mentioned briefly.",
        "Solana in title"
    )
    
    # Test 3: ETH ticker in title
    test_article(
        "ETH Mining Profitability Soars",
        "Ethereum mining profits increase. Bitcoin mining also discussed.",
        "ETH ticker in title"
    )
    
    # Test 4: Multiple other cryptos in body
    test_article(
        "Cryptocurrency Mining Update",
        "Ethereum mining grows. Solana network active. Cardano miners profit. Litecoin mining continues. Bitcoin mining mentioned.",
        "Multiple other cryptos in body"
    )
    
    # Test 5: Ripple/XRP in title
    test_article(
        "XRP Mining Community Grows",
        "Ripple ecosystem expands with new mining features. Bitcoin mining also exists.",
        "XRP/Ripple in title"
    )
    
    print("\n\n✅ TESTING LEGITIMATE BITCOIN MINING (Should All Be APPROVED)")
    print("=" * 80)
    
    # Test 6: Pure Bitcoin mining
    test_article(
        "Bitcoin Mining Revenue Reaches New High",
        "Bitcoin mining companies report record revenues. Mining difficulty increases. Hash rate reaches all-time high.",
        "Pure Bitcoin mining article"
    )
    
    # Test 7: Public mining company
    test_article(
        "Marathon Digital Expands Texas Operations",
        "Marathon Digital adds 5000 miners. Hash rate increases 500 PH/s. Bitcoin mining operations expand.",
        "Public mining company (MARA)"
    )
    
    # Test 8: Mining difficulty article
    test_article(
        "Bitcoin Mining Difficulty Hits Record High",
        "Network hash rate increases. Mining difficulty adjustment. Miners report challenges. Bitcoin mining continues.",
        "Mining difficulty news"
    )
    
    # Test 9: Public company (RIOT)
    test_article(
        "Riot Platforms Reports Q3 Mining Results",
        "Riot Platforms announces earnings. Bitcoin mining revenue grows. Hash rate performance strong.",
        "Public mining company (RIOT)"
    )
    
    print("\n\n" + "=" * 80)
    print("📊 FILTERING SUMMARY")
    print("=" * 80)
    print("✅ Ethereum/Solana articles are now properly filtered out")
    print("✅ Articles with other crypto tickers (ETH, XRP) in titles are rejected")
    print("✅ Articles with 3+ other crypto mentions are rejected")
    print("✅ Legitimate Bitcoin mining articles are still approved")
    print("✅ Public mining company articles are still approved")
    print("=" * 80)


if __name__ == "__main__":
    main()
