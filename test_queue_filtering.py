#!/usr/bin/env python3
"""
Test the enhanced content filtering on the actual queue
"""

import json
from crypto_filter import filter_bitcoin_only_articles

def test_actual_queue_filtering():
    """Test filtering on the actual queued articles"""
    print("🔍 Testing enhanced filtering on actual queue...")
    
    # Load actual queue
    with open('posted_articles.json', 'r') as f:
        data = json.load(f)
    
    queued_articles = data.get('queued_articles', [])
    print(f"Testing {len(queued_articles)} articles from actual queue:")
    
    for i, article in enumerate(queued_articles[:10], 1):
        title = article.get('title', 'NO TITLE')[:60]
        print(f"  {i}. {title}...")
    
    # Apply enhanced filtering
    filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(queued_articles)
    
    print(f"\n📤 Enhanced filter results:")
    print(f"   ✅ Articles that passed: {len(filtered_articles)}")
    print(f"   ❌ Articles filtered out: {excluded_count}")
    
    if excluded_count > 0:
        print(f"\n❌ Articles that will be filtered out:")
        for detail in excluded_details:
            title = detail['title']
            reason = detail.get('reason', 'Unknown')
            print(f"   • {title}")
            print(f"     Reason: {reason}")
    
    if len(filtered_articles) < len(queued_articles):
        print(f"\n🎯 FILTERING SUCCESS!")
        print(f"   The enhanced filter will clean up {excluded_count} invalid articles")
        print(f"   Only genuine Bitcoin mining articles will remain")
    else:
        print(f"\n✅ All articles in queue are valid Bitcoin mining content")
    
    return excluded_count

if __name__ == "__main__":
    excluded_count = test_actual_queue_filtering()
    if excluded_count > 0:
        print(f"\n🚀 Ready to clean up {excluded_count} invalid articles from queue!")
    else:
        print(f"\n✅ Queue is already clean!")