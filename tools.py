#!/usr/bin/env python3
"""
Bitcoin Mining Bot - Essential Tools
=====================================
Streamlined tools for managing the Bitcoin Mining Bot.

This module provides essential utilities for bot management:
- Queue preview and management
- Diagnostic tools
- Simple maintenance scripts
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import from the refactored core
try:
    from core import Storage, TextProcessor, Article
    from bot import FileManager, TextUtils
except ImportError:
    print("❌ Error: Cannot import core modules. Make sure core.py and bot.py exist.")
    sys.exit(1)


class BotTools:
    """Essential tools for bot management."""
    
    @staticmethod
    def show_next_tweet():
        """Show preview of the next tweet that will be posted."""
        print("📱 Next Tweet Preview")
        print("=" * 40)
        
        # Load queued articles
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        
        if not queued_articles:
            print("📭 No tweets in queue")
            print("\nTo add tweets to the queue:")
            print("  python bot.py")
            return
        
        # Show the next article
        next_article = queued_articles[0]
        title = next_article.get("title", "Unknown Title")
        url = next_article.get("url", "")
        source = next_article.get("source", {}).get("title", "Unknown Source") if isinstance(next_article.get("source"), dict) else str(next_article.get("source", "Unknown Source"))
        
        # Generate tweet text
        tweet_text = TextUtils.create_tweet_text(next_article)
        char_count = len(tweet_text)
        
        print(f"📰 Article: {title}")
        print(f"🔗 Source: {source}")
        print(f"📊 Characters: {char_count}/280")
        print(f"📝 Tweet text:")
        print("-" * 40)
        print(tweet_text)
        print("-" * 40)
        
        if url:
            print(f"🌐 URL: {url}")
        
        queue_size = len(queued_articles)
        if queue_size > 1:
            print(f"\n📋 Queue: {queue_size} articles total")
    
    @staticmethod
    def show_queue_simple():
        """Show a simple list of queued articles."""
        print("📋 Simple Queue View")
        print("=" * 40)
        
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        
        if not queued_articles:
            print("📭 Queue is empty")
            return
        
        for i, article in enumerate(queued_articles, 1):
            title = article.get("title", "Unknown Title")
            source = article.get("source", {}).get("title", "Unknown") if isinstance(article.get("source"), dict) else "Unknown"
            print(f"{i:2d}. {title[:60]}..." if len(title) > 60 else f"{i:2d}. {title}")
            print(f"    📰 {source}")
            if i != len(queued_articles):
                print()
    
    @staticmethod
    def clean_queue():
        """Interactive queue cleaning tool."""
        print("🧹 Queue Cleaning Tool")
        print("=" * 40)
        
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        
        if not queued_articles:
            print("📭 Queue is empty - nothing to clean")
            return
        
        print(f"Found {len(queued_articles)} articles in queue")
        
        # Show articles and ask for removal
        articles_to_remove = []
        for i, article in enumerate(queued_articles):
            title = article.get("title", "Unknown Title")
            source = article.get("source", {}).get("title", "Unknown") if isinstance(article.get("source"), dict) else "Unknown"
            
            print(f"\n{i+1}. {title}")
            print(f"   Source: {source}")
            
            try:
                response = input("   Remove this article? (y/N): ").strip().lower()
                if response == 'y':
                    articles_to_remove.append(i)
                    print("   ✅ Marked for removal")
            except KeyboardInterrupt:
                print("\n\n🛑 Cleaning cancelled")
                return
        
        # Remove marked articles (in reverse order to maintain indices)
        if articles_to_remove:
            for i in reversed(articles_to_remove):
                removed_article = queued_articles.pop(i)
                print(f"🗑️ Removed: {removed_article.get('title', 'Unknown')[:50]}...")
            
            # Save updated data
            posted_articles["queued_articles"] = queued_articles
            FileManager.save_posted_articles(posted_articles)
            
            print(f"\n✅ Cleaned {len(articles_to_remove)} articles from queue")
            print(f"📊 {len(queued_articles)} articles remaining")
        else:
            print("\n📋 No articles removed")
    
    @staticmethod
    def diagnose_bot():
        """Run comprehensive bot diagnostics."""
        print("🔍 Bitcoin Mining Bot Diagnostics")
        print("=" * 50)
        
        # Test imports
        try:
            from bot import BitcoinMiningNewsBotLegacy
            print("✅ Bot modules import successfully")
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
        
        # Test bot initialization
        try:
            bot = BitcoinMiningNewsBotLegacy(safe_mode=True)
            print("✅ Bot initializes successfully")
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
        
        # Run bot diagnostics
        print("\n🏃 Running bot diagnostics...")
        success = bot.run()
        
        if success:
            print("✅ Diagnostics completed successfully")
        else:
            print("❌ Diagnostics found issues (expected without API keys)")
        
        return True


def main():
    """Main CLI interface for bot tools."""
    if len(sys.argv) < 2:
        print("🛠️ Bitcoin Mining Bot Tools")
        print("=" * 30)
        print("Available commands:")
        print("  preview    - Show next tweet preview")
        print("  queue      - Show simple queue view") 
        print("  clean      - Clean unwanted articles from queue")
        print("  diagnose   - Run bot diagnostics")
        print("\nUsage: python tools.py <command>")
        return
    
    command = sys.argv[1].lower()
    
    if command == "preview":
        BotTools.show_next_tweet()
    elif command == "queue":
        BotTools.show_queue_simple()
    elif command == "clean":
        BotTools.clean_queue()
    elif command == "diagnose":
        BotTools.diagnose_bot()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available: preview, queue, clean, diagnose")


if __name__ == "__main__":
    main()