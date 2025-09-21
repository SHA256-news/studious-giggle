#!/usr/bin/env python3

"""Test the fixed tweet generation"""

from utils import TextUtils

def test_tweet_generation():
    """Test tweet generation with the rail boss article"""
    
    # Test the problematic Rail Boss article
    rail_boss_article = {
        "title": "Rail Boss 'Stole Electricity from Russian Railways to Mine Crypto'",
        "body": "Power chiefs stole electricity from the state-owned Russian Railways to operate private crypto mining rigs, prosecutors in St. Petersburg have claimed. Prosecutors say the duo stole nearly 1 billion rubles (over $12 million) worth of power from their employer to power crypto mining rigs.",
        "url": "https://cryptonews.com/news/rail-boss-stole-electricity-from-russian-railways-network-to-mine-crypto/"
    }
    
    print("🧪 TESTING TWEET GENERATION FIXES")
    print("=" * 60)
    print(f"📰 Article: {rail_boss_article['title']}")
    print()
    
    # Test key info extraction
    info = TextUtils.extract_key_info(rail_boss_article)
    print("🔍 EXTRACTED INFO:")
    print(f"   Companies: {info['companies']}")
    print(f"   Financial: {info['financial_amounts']}")
    print(f"   Locations: {info['locations']}")
    print()
    
    # Test enhanced tweet creation
    enhanced_tweet = TextUtils.create_enhanced_tweet_text(rail_boss_article)
    print("🚀 ENHANCED TWEET:")
    print(f"   {enhanced_tweet}")
    print(f"   Characters: {len(enhanced_tweet)}")
    print()
    
    # Test original tweet creation
    original_tweet = TextUtils.create_original_tweet_text(rail_boss_article)
    print("📜 ORIGINAL TWEET:")
    print(f"   {original_tweet}")
    print(f"   Characters: {len(original_tweet)}")
    print()
    
    # Test a legitimate business article
    business_article = {
        "title": "CleanSpark Expands Bitcoin Mining Operations with $50 Million Investment",
        "body": "CleanSpark Inc. announced a major expansion of their Bitcoin mining operations with a $50 million investment in new mining facilities. The expansion will add 2,200 mining rigs to their operations.",
        "url": "https://example.com/cleanspark-expansion"
    }
    
    print("🏢 TESTING BUSINESS ARTICLE:")
    print(f"📰 Article: {business_article['title']}")
    print()
    
    business_info = TextUtils.extract_key_info(business_article)
    print("🔍 EXTRACTED INFO:")
    print(f"   Companies: {business_info['companies']}")
    print(f"   Financial: {business_info['financial_amounts']}")
    print()
    
    business_tweet = TextUtils.create_enhanced_tweet_text(business_article)
    print("🚀 ENHANCED TWEET:")
    print(f"   {business_tweet}")
    print(f"   Characters: {len(business_tweet)}")
    print()
    
    print("✅ Tweet generation test complete!")

if __name__ == "__main__":
    test_tweet_generation()