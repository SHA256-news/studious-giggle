#!/usr/bin/env python3
"""
Simple Queue Preview
--------------------
Shows just the tweet text for queued articles in a clean, simple format.
"""

import json
from utils import TextUtils, FileManager


def main():
    """Show a simple preview of queued tweets"""
    print("🐦 NEXT TWEETS IN QUEUE")
    print("=" * 60)
    
    # Load queued articles
    posted_articles = FileManager.load_posted_articles()
    queued_articles = posted_articles.get("queued_articles", [])
    
    if not queued_articles:
        print("📭 No articles currently in queue")
        return
    
    print(f"📊 {len(queued_articles)} articles queued\n")
    
    # Show first 10 tweets
    for i, article in enumerate(queued_articles[:10], 1):
        tweet_text = TextUtils.create_enhanced_tweet_text(article)
        source = article.get("source", {}).get("title", "Unknown")
        
        print(f"{i:2d}. {tweet_text}")
        print(f"    └─ {source} ({len(tweet_text)} chars)")
        print()
    
    if len(queued_articles) > 10:
        print(f"... and {len(queued_articles) - 10} more tweets in queue")


if __name__ == "__main__":
    main()