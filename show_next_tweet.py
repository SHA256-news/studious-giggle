#!/usr/bin/env python3
"""
Show Next Tweet Preview
-----------------------
Shows exactly what the very next tweet will look like when published.
Simple, focused output for the next tweet in the queue.
"""

import sys
from utils import TextUtils, FileManager


def show_next_tweet():
    """Show preview of the very next tweet that will be published"""
    try:
        # Load queued articles
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        
        if not queued_articles:
            print("📭 No tweets in queue")
            print("\nTo add tweets to the queue:")
            print("  python bot.py")
            return
        
        # Get the next article (first in queue)
        next_article = queued_articles[0]
        
        # Generate the tweet text using the same method the bot uses
        tweet_text = TextUtils.create_tweet_text(next_article)
        
        # Show the preview
        print("🐦 NEXT TWEET PREVIEW")
        print("=" * 50)
        print()
        print(f"📰 Article: {next_article.get('title', 'Unknown Title')}")
        print(f"📅 Source: {next_article.get('source', {}).get('title', 'Unknown')}")
        print()
        print("🚀 THIS WILL BE POSTED:")
        # Adjust box width based on tweet length
        box_width = max(50, len(tweet_text) + 4)
        print("┌" + "─" * (box_width - 2) + "┐")
        print(f"│ {tweet_text} │")
        print("└" + "─" * (box_width - 2) + "┘")
        print(f"   Characters: {len(tweet_text)}/280")
        print()
        
        # Check if it's a thread (2-part tweet)
        try:
            hook_tweet, link_tweet = TextUtils.create_thread_texts(next_article)
            if hook_tweet and link_tweet and hook_tweet != link_tweet:
                print("📝 THREAD FORMAT (2 tweets):")
                print()
                print("Tweet 1 (Hook):")
                print(f"  {hook_tweet}")
                print(f"  Characters: {len(hook_tweet)}/280")
                print()
                print("Tweet 2 (Link):")
                print(f"  {link_tweet}")
                print(f"  Characters: {len(link_tweet)}/280")
                print()
        except Exception:
            # Single tweet format (not a thread)
            pass
        
        # Show URL if available
        url = next_article.get('url', next_article.get('uri', ''))
        if url:
            print(f"🔗 Article URL: {url}")
        
        print()
        print("⏰ This tweet will be posted automatically by the bot")
        print("   according to its 90-minute schedule and rate limits.")
        
    except Exception as e:
        print(f"❌ Error loading next tweet: {e}")
        print("\nTry running: python diagnose_bot.py")
        sys.exit(1)


if __name__ == "__main__":
    show_next_tweet()