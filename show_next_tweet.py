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
        
        # Try to generate Gemini content like the bot does
        enhanced_article = next_article.copy()
        gemini_content_available = False
        
        try:
            # Try to import and initialize Gemini client directly
            from gemini_client import GeminiClient
            from config import GeminiConfig
            import os
            
            if os.getenv('GEMINI_API_KEY'):
                gemini_config = GeminiConfig.from_env()
                gemini_client = GeminiClient(gemini_config)
                
                print("🤖 Generating Gemini AI content...")
                
                # Generate headline and summary like the bot does
                tweet_headline = gemini_client.generate_tweet_headline(next_article)
                tweet_summary = gemini_client.generate_tweet_summary(next_article)
                
                # Combine like the bot does
                combined_content = f"{tweet_headline}\n\n{tweet_summary}"
                
                if len(combined_content) <= 280:
                    enhanced_article['gemini_headline'] = combined_content
                    enhanced_article['gemini_summary'] = tweet_summary
                    gemini_content_available = True
                    print(f"✅ Generated Gemini content ({len(combined_content)} chars)")
                else:
                    enhanced_article['gemini_headline'] = tweet_headline
                    enhanced_article['gemini_summary'] = tweet_summary
                    gemini_content_available = True
                    print(f"✅ Generated Gemini content (headline only, combined too long: {len(combined_content)} chars)")
            else:
                print("⚠️  GEMINI_API_KEY not found in environment")
                print("💡 To see 3-point summaries, configure GEMINI_API_KEY in GitHub secrets")
                print("   The bot will then generate AI-enhanced headlines and bullet point summaries")
                    
        except Exception as e:
            print(f"⚠️  Gemini AI not available: {e}")
            print("💡 When GEMINI_API_KEY is configured, this preview will show:")
            print("   • AI-generated engaging headlines")
            print("   • 3-point bullet summaries")
            print("   • Combined content optimization")
            print("📝 Currently showing fallback format without AI enhancement")
        
        # Generate the tweet text using the same method the bot uses
        original_tweet_text = TextUtils.create_tweet_text(next_article)
        enhanced_tweet_text = TextUtils.create_tweet_text(enhanced_article) if gemini_content_available else original_tweet_text
        
        # Show the preview
        print("\n🐦 NEXT TWEET PREVIEW")
        print("=" * 70)
        print()
        print(f"📰 Article: {next_article.get('title', 'Unknown Title')}")
        print(f"📅 Source: {next_article.get('source', {}).get('title', 'Unknown')}")
        print()
        
        if gemini_content_available:
            print("🚀 THIS WILL BE POSTED (WITH GEMINI AI):")
            # Show the enhanced version
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
            
            # Show the 3-point summary if available
            if enhanced_article.get('gemini_summary'):
                print(f"\n📋 3-POINT SUMMARY:")
                print(f"   {enhanced_article['gemini_summary']}")
            
            print(f"\n📜 FALLBACK VERSION (if Gemini fails):")
            print(f"   {original_tweet_text}")
            print(f"   Characters: {len(original_tweet_text)}/280")
        else:
            print("🚀 THIS WILL BE POSTED:")
            # Adjust box width based on tweet length
            box_width = max(50, len(original_tweet_text) + 4)
            print("┌" + "─" * (box_width - 2) + "┐")
            print(f"│ {original_tweet_text} │")
            print("└" + "─" * (box_width - 2) + "┘")
            print(f"   Characters: {len(original_tweet_text)}/280")
        
        print()
        
        # Check if it's a thread (show new 3-part format)
        try:
            article_for_thread = enhanced_article if gemini_content_available else next_article
            hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article_for_thread)
            
            # Determine how many tweets in the thread
            tweet_count = 1  # Hook always exists
            if summary_tweet:
                tweet_count += 1
            if url_tweet:
                tweet_count += 1
            
            if tweet_count > 1:
                print(f"📝 THREAD FORMAT ({tweet_count} tweets):")
                print()
                print("Tweet 1 (Hook):")
                print(f"  {hook_tweet}")
                print(f"  Characters: {len(hook_tweet)}/280")
                print()
                
                if summary_tweet:
                    print("Tweet 2 (Summary):")
                    print(f"  {summary_tweet}")
                    print(f"  Characters: {len(summary_tweet)}/280")
                    print()
                
                if url_tweet:
                    tweet_num = 3 if summary_tweet else 2
                    print(f"Tweet {tweet_num} (URL):")
                    print(f"  {url_tweet}")
                    print(f"  Characters: {len(url_tweet)}/280")
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