#!/usr/bin/env python3
"""
Demo: Show Next Tweet Preview WITH Gemini
-----------------------------------------
Demonstrates what the preview looks like when Gemini AI is configured.
"""

import sys
from utils import TextUtils, FileManager


def demo_with_gemini():
    """Demo showing what the output looks like with Gemini AI enabled"""
    try:
        # Load queued articles
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        
        if not queued_articles:
            print("📭 No tweets in queue for demo")
            return
        
        # Get the next article (first in queue)
        next_article = queued_articles[0]
        
        # Simulate Gemini content generation
        enhanced_article = next_article.copy()
        
        print("🤖 Generating Gemini AI content...")
        
        # Simulate realistic Gemini output
        tweet_headline = "Russian Energy Ministry Confirms No Additional Crypto Mining Restrictions"
        tweet_summary = "• No new regional bans planned • Power grid handling current load • Miners offering tax revenue"
        
        # Combine like the bot does
        combined_content = f"{tweet_headline}\n\n{tweet_summary}"
        
        if len(combined_content) <= 280:
            enhanced_article['gemini_headline'] = combined_content
            enhanced_article['gemini_summary'] = tweet_summary
            print(f"✅ Generated Gemini content ({len(combined_content)} chars)")
        else:
            enhanced_article['gemini_headline'] = tweet_headline
            enhanced_article['gemini_summary'] = tweet_summary
            print(f"✅ Generated Gemini content (headline only, combined too long: {len(combined_content)} chars)")
        
        # Generate the tweet text using the enhanced article
        enhanced_tweet_text = TextUtils.create_tweet_text(enhanced_article)
        original_tweet_text = TextUtils.create_tweet_text(next_article)
        
        # Show the preview
        print("\n🐦 NEXT TWEET PREVIEW (WITH GEMINI AI)")
        print("=" * 70)
        print()
        print(f"📰 Article: {next_article.get('title', 'Unknown Title')}")
        print(f"📅 Source: {next_article.get('source', {}).get('title', 'Unknown')}")
        print()
        
        print("🚀 THIS WILL BE POSTED (WITH GEMINI AI):")
        print("┌" + "─" * 68 + "┐")
        # Split long tweets into multiple lines for display
        if len(enhanced_tweet_text) > 65:
            lines = []
            current_line = ""
            words = enhanced_tweet_text.split()
            for word in words:
                if len(current_line + " " + word) <= 65:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                print(f"│ {line:<66} │")
        else:
            print(f"│ {enhanced_tweet_text:<66} │")
        print("└" + "─" * 68 + "┘")
        print(f"   Characters: {len(enhanced_tweet_text)}/280")
        
        # Show the 3-point summary
        print(f"\n📋 3-POINT SUMMARY:")
        print(f"   {tweet_summary}")
        
        print(f"\n📜 FALLBACK VERSION (if Gemini fails):")
        print(f"   {original_tweet_text}")
        print(f"   Characters: {len(original_tweet_text)}/280")
        
        # Check if it's a thread (2-part tweet)
        try:
            hook_tweet, link_tweet = TextUtils.create_thread_texts(enhanced_article)
            if hook_tweet and link_tweet and hook_tweet != link_tweet:
                print("\n📝 THREAD FORMAT (2 tweets):")
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
        sys.exit(1)


if __name__ == "__main__":
    demo_with_gemini()