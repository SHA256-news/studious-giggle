#!/usr/bin/env python3
"""Debug script to examine URL placement in threads."""

from core import TextProcessor, Article

def test_url_placement():
    """Test where URLs end up in both Gemini and fallback modes."""
    
    # Create a test article
    article = Article(
        title="Bitcoin Mining Revenue Hits Record High in Q3 2024",
        body="Bitcoin mining companies reported unprecedented revenue growth...",
        url="https://example.com/bitcoin-mining-record-q3-2024",
        source="CryptoNews Daily"
    )
    
    print("🔍 TESTING URL PLACEMENT IN THREADS")
    print("=" * 50)
    
    # Test 1: Fallback mode (no Gemini)
    print("\n1️⃣ FALLBACK MODE (No Gemini):")
    print("-" * 30)
    
    fallback_thread = TextProcessor._create_simple_tweet(article)
    print(f"Thread length: {len(fallback_thread)} tweets")
    
    for i, tweet in enumerate(fallback_thread, 1):
        print(f"\nTweet {i}: {tweet}")
        print(f"Length: {len(tweet)} chars")
        
        # Check if this tweet contains URL
        if "https://" in tweet:
            print(f"🔗 URL FOUND in tweet {i}")
    
    print(f"\n❓ URL in last tweet? {'✅ YES' if 'https://' in fallback_thread[-1] else '❌ NO'}")
    
    # Test 2: Simulated Gemini mode (manual construction)
    print("\n\n2️⃣ GEMINI MODE (Simulated):")
    print("-" * 30)
    
    # Simulate what happens in Gemini mode
    gemini_thread = []
    
    # Simulate Gemini-generated headline and summary
    headline = "BREAKING: Bitcoin Mining Revenue Surges 45% to Record $2.1B"
    summary = "• Q3 2024 shows unprecedented growth\n• Major miners report 30-50% profit increases\n• Hash rate efficiency improvements drive gains"
    
    # Check if they fit together
    combined = f"{headline}\n\n{summary}"
    if len(combined) <= 280:
        gemini_thread.append(combined)
    else:
        gemini_thread.append(headline)
        if len(summary) <= 280:
            gemini_thread.append(summary)
        else:
            gemini_thread.append(summary[:277] + "...")
    
    # Add URL (as done in the code)
    if article.url:
        gemini_thread.append(article.url)
    
    print(f"Thread length: {len(gemini_thread)} tweets")
    
    for i, tweet in enumerate(gemini_thread, 1):
        print(f"\nTweet {i}: {tweet}")
        print(f"Length: {len(tweet)} chars")
        
        # Check if this tweet contains URL
        if "https://" in tweet:
            print(f"🔗 URL FOUND in tweet {i}")
    
    print(f"\n❓ URL in last tweet? {'✅ YES' if 'https://' in gemini_thread[-1] else '❌ NO'}")
    
    # Test 3: Test with actual TextProcessor.create_tweet_thread
    print("\n\n3️⃣ ACTUAL TextProcessor.create_tweet_thread (No Gemini):")
    print("-" * 50)
    
    actual_thread = TextProcessor.create_tweet_thread(article, gemini_client=None)
    print(f"Thread length: {len(actual_thread)} tweets")
    
    for i, tweet in enumerate(actual_thread, 1):
        print(f"\nTweet {i}: {tweet}")
        print(f"Length: {len(tweet)} chars")
        
        # Check if this tweet contains URL
        if "https://" in tweet:
            print(f"🔗 URL FOUND in tweet {i}")
    
    print(f"\n❓ URL in last tweet? {'✅ YES' if 'https://' in actual_thread[-1] else '❌ NO'}")
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print(f"   Fallback mode: URL in tweet {len(fallback_thread)} of {len(fallback_thread)}")
    print(f"   Gemini mode: URL in tweet {len(gemini_thread)} of {len(gemini_thread)}")
    print(f"   Actual method: URL in tweet {len(actual_thread)} of {len(actual_thread)}")

if __name__ == "__main__":
    test_url_placement()