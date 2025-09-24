#!/usr/bin/env python3
"""
Test to demonstrate the critical bugs mentioned in the problem statement:
1. Non-mining content being posted (Luxembourg teens cancer research)
2. Tweets truncated instead of proper multi-tweet threads
3. Content filtering is broken for non-Bitcoin mining content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_filter import filter_bitcoin_only_articles
from create_summary import create_twitter_thread

def test_critical_content_filtering_bug():
    """Test that demonstrates the critical content filtering bug"""
    print("🔍 Testing critical content filtering bugs...")
    
    # Example from actual queue - non-mining content that's passing through
    problematic_articles = [
        {
            "title": "From Classroom To Breakthrough: Luxembourg Teens Awarded EUCYS Prize for Cancer Research",
            "body": "A team of young Luxembourg scientists has been awarded a special prize for their wearable device for cancer research. This breakthrough innovation was recognized at the European Union Contest for Young Scientists.",
            "url": "https://example.com/luxembourg-teens-cancer"
        },
        {
            "title": "Square Financial Services Grant News",
            "body": "Square Financial Services announces a new grant program for small businesses. This $50M initiative will support entrepreneurs across multiple industries.",
            "url": "https://example.com/square-grant"
        },
        {
            "title": "Bitcoin Mining Facility Expansion in Texas",
            "body": "A new Bitcoin mining facility is expanding operations in Texas, adding 5,000 new ASIC miners to increase hashrate capacity.",
            "url": "https://example.com/bitcoin-mining-texas"
        }
    ]
    
    print(f"Testing with {len(problematic_articles)} articles:")
    for i, article in enumerate(problematic_articles, 1):
        print(f"  {i}. {article['title'][:60]}...")
    
    # Apply current filtering
    filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(problematic_articles)
    
    print(f"\n📤 Current filter results:")
    print(f"   ✅ Articles passed: {len(filtered_articles)}")
    print(f"   ❌ Articles filtered: {excluded_count}")
    
    print(f"\n🚨 CRITICAL BUG DEMONSTRATED:")
    for article in filtered_articles:
        title = article['title']
        # Check if this is actually Bitcoin mining content
        is_actually_mining = is_actual_bitcoin_mining_content(title, article.get('body', ''))
        status = "✅ VALID" if is_actually_mining else "❌ INVALID"
        print(f"   {status}: {title[:60]}...")
    
    # Count invalid articles that passed through
    invalid_passed = sum(1 for article in filtered_articles 
                        if not is_actual_bitcoin_mining_content(article['title'], article.get('body', '')))
    
    print(f"\n📊 BUG SUMMARY:")
    print(f"   • Non-mining articles that passed filter: {invalid_passed}")
    print(f"   • This demonstrates the critical content filtering bug!")
    
    return invalid_passed > 0

def test_thread_creation_vs_truncation():
    """Test that tweets are properly threaded vs truncated"""
    print("\n🧵 Testing thread creation vs truncation bug...")
    
    # Create a long article that should generate a multi-tweet thread
    long_article = {
        "title": "Major Bitcoin Mining Operation Expands with $100M Investment",
        "summary": "Key highlights: A major Bitcoin mining company announced a $100 million expansion of their operations. The company will add 10,000 new ASIC miners to their facilities across Texas and Wyoming. This expansion is expected to increase their hashrate by 50% and make them one of the largest Bitcoin mining operations in North America.",
        "body": "This is a comprehensive Bitcoin mining expansion story with lots of details about the mining operations, energy usage, hashrate improvements, and future plans for the company. The expansion includes renewable energy sources and advanced cooling systems for the mining equipment.",
        "tags": ["bitcoin", "mining", "investment"],
        "url": "https://example.com/bitcoin-mining-expansion"
    }
    
    # Generate Twitter thread
    tweets = create_twitter_thread(long_article, max_tweets=10)
    
    print(f"Generated {len(tweets)} tweets:")
    for i, tweet in enumerate(tweets, 1):
        print(f"   Tweet {i} ({len(tweet)} chars): {tweet[:50]}...")
        if len(tweet) > 280:
            print(f"      🚨 TRUNCATION BUG: Tweet {i} exceeds 280 characters!")
            return True
    
    # Check if content is properly distributed vs truncated
    total_original_content = len(long_article['title']) + len(long_article.get('summary', ''))
    total_tweet_content = sum(len(tweet) for tweet in tweets)
    
    print(f"\n📊 Thread Analysis:")
    print(f"   • Original content: {total_original_content} characters")
    print(f"   • Thread content: {total_tweet_content} characters")
    print(f"   • Tweets generated: {len(tweets)}")
    
    if len(tweets) == 1 and total_original_content > 280:
        print(f"   🚨 TRUNCATION BUG: Long content forced into single tweet!")
        return True
    elif len(tweets) > 1:
        print(f"   ✅ Proper threading: Content split across multiple tweets")
        return False
    else:
        print(f"   ✅ Single tweet appropriate for content length")
        return False

def is_actual_bitcoin_mining_content(title: str, body: str) -> bool:
    """
    Check if content is actually about Bitcoin mining.
    This is what the filtering SHOULD do but currently doesn't.
    """
    text = (title + " " + body).lower()
    
    # Must contain Bitcoin reference
    bitcoin_terms = ["bitcoin", "btc"]
    has_bitcoin = any(term in text for term in bitcoin_terms)
    
    # Must contain mining reference  
    mining_terms = ["mining", "miner", "miners", "hashrate", "hash rate", "difficulty", "asic"]
    has_mining = any(term in text for term in mining_terms)
    
    # Should not be about unrelated topics
    unrelated_terms = ["cancer", "medical", "healthcare", "teens", "students", "classroom", 
                      "education", "school", "university", "grant", "prize", "award", 
                      "financial services", "banking"]
    has_unrelated = any(term in text for term in unrelated_terms)
    
    return has_bitcoin and has_mining and not has_unrelated

if __name__ == "__main__":
    print("🧪 CRITICAL BUGS TEST SUITE")
    print("=" * 60)
    
    # Test 1: Content filtering bug
    content_bug = test_critical_content_filtering_bug()
    
    # Test 2: Thread creation vs truncation bug  
    thread_bug = test_thread_creation_vs_truncation()
    
    print(f"\n{'=' * 60}")
    print("📋 TEST RESULTS:")
    print(f"   🚨 Content filtering bug: {'CONFIRMED' if content_bug else 'NOT FOUND'}")
    print(f"   🚨 Thread truncation bug: {'CONFIRMED' if thread_bug else 'NOT FOUND'}")
    
    if content_bug or thread_bug:
        print(f"\n❌ CRITICAL BUGS CONFIRMED - Need fixes!")
        sys.exit(1)
    else:
        print(f"\n✅ No critical bugs found")
        sys.exit(0)