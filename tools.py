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
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the refactored core with error handling
try:
    from core import Storage, TextProcessor, Article, Config, BitcoinMiningBot
    from bot import FileManager, TextUtils, BitcoinMiningNewsBotLegacy
except ImportError as e:
    print(f"❌ Error: Cannot import core modules: {e}")
    print("💡 Make sure you're running this from the project root directory")
    print("💡 Required files: core.py and bot.py")
    sys.exit(1)


class BotTools:
    """Essential tools for bot management."""
    
    @staticmethod
    def show_next_tweet() -> bool:
        """Show preview of the next tweet that will be posted.
        
        Returns:
            bool: True if preview was shown successfully, False otherwise
        """
        try:
            print("📱 Next Tweet Preview")
            print("=" * 40)
            
            # Load queued articles with error handling
            try:
                posted_articles = FileManager.load_posted_articles()
                queued_articles = posted_articles.get("queued_articles", [])
            except Exception as e:
                print(f"❌ Error loading posted articles: {e}")
                return False
            
            if not queued_articles:
                print("📭 No tweets in queue")
                print("\nTo add tweets to the queue:")
                print("  python bot.py")
                return True
            
            # Validate next article data
            next_article = queued_articles[0]
            if not isinstance(next_article, dict):
                print("❌ Invalid article data format")
                return False
            
            # Extract article information safely
            title = next_article.get("title", "Unknown Title")
            url = next_article.get("url", next_article.get("uri", ""))
            source_data = next_article.get("source", {})
            
            if isinstance(source_data, dict):
                source = source_data.get("title", "Unknown Source")
            else:
                source = str(source_data) if source_data else "Unknown Source"
            
            # Generate tweet text with error handling
            try:
                tweet_text = TextUtils.create_tweet_text(next_article)
                char_count = len(tweet_text)
            except Exception as e:
                print(f"❌ Error generating tweet text: {e}")
                return False
            
            # Display preview
            print(f"📰 Article: {title[:80]}{'...' if len(title) > 80 else ''}")
            print(f"🔗 Source: {source}")
            print(f"📊 Characters: {char_count}/280")
            
            if char_count > 280:
                print("⚠️  WARNING: Tweet exceeds 280 character limit!")
            
            print(f"📝 Tweet text:")
            print("-" * 40)
            print(tweet_text)
            print("-" * 40)
            
            if url:
                print(f"🌐 URL: {url}")
            
            queue_size = len(queued_articles)
            if queue_size > 1:
                print(f"\n📋 Queue: {queue_size} articles total")
                
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error in show_next_tweet: {e}")
            return False
    
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
    def clean_queue() -> bool:
        """Interactive queue cleaning tool.
        
        Returns:
            bool: True if cleaning completed successfully, False otherwise
        """
        try:
            print("🧹 Queue Cleaning Tool")
            print("=" * 40)
            
            # Load data with error handling
            try:
                posted_articles = FileManager.load_posted_articles()
                queued_articles = posted_articles.get("queued_articles", [])
            except Exception as e:
                print(f"❌ Error loading queue data: {e}")
                return False
            
            if not queued_articles:
                print("📭 Queue is empty - nothing to clean")
                return True
            
            print(f"Found {len(queued_articles)} articles in queue")
            print("\n💡 Press Ctrl+C to cancel at any time")
            
            # Show articles and ask for removal
            articles_to_remove: List[int] = []
            for i, article in enumerate(queued_articles):
                if not isinstance(article, dict):
                    print(f"\n{i+1}. ❌ Invalid article data (will be auto-removed)")
                    articles_to_remove.append(i)
                    continue
                    
                title = article.get("title", "Unknown Title")
                source_data = article.get("source", {})
                
                if isinstance(source_data, dict):
                    source = source_data.get("title", "Unknown")
                else:
                    source = str(source_data) if source_data else "Unknown"
                
                print(f"\n{i+1}. {title[:70]}{'...' if len(title) > 70 else ''}")
                print(f"   Source: {source}")
                
                try:
                    response = input("   Remove this article? (y/N): ").strip().lower()
                    if response in ['y', 'yes']:
                        articles_to_remove.append(i)
                        print("   ✅ Marked for removal")
                    elif response in ['q', 'quit']:
                        print("\n🛑 Cleaning cancelled by user")
                        return True
                except (KeyboardInterrupt, EOFError):
                    print("\n\n🛑 Cleaning cancelled")
                    return True
            
            # Remove marked articles (in reverse order to maintain indices)
            if articles_to_remove:
                removed_count = 0
                for i in reversed(articles_to_remove):
                    try:
                        removed_article = queued_articles.pop(i)
                        title = removed_article.get('title', 'Unknown') if isinstance(removed_article, dict) else 'Invalid data'
                        print(f"🗑️ Removed: {title[:50]}{'...' if len(str(title)) > 50 else ''}")
                        removed_count += 1
                    except (IndexError, TypeError) as e:
                        print(f"⚠️ Failed to remove article {i}: {e}")
                
                # Save updated data with error handling
                try:
                    posted_articles["queued_articles"] = queued_articles
                    FileManager.save_posted_articles(posted_articles)
                    
                    print(f"\n✅ Successfully cleaned {removed_count} articles from queue")
                    print(f"📊 {len(queued_articles)} articles remaining")
                except Exception as e:
                    print(f"❌ Error saving cleaned queue: {e}")
                    return False
            else:
                print("\n📋 No articles were removed")
                
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error during queue cleaning: {e}")
            return False
    
    @staticmethod
    def diagnose_bot() -> bool:
        """Run comprehensive bot diagnostics.
        
        Returns:
            bool: True if all diagnostics pass, False if issues found
        """
        print("🔍 Bitcoin Mining Bot Diagnostics")
        print("=" * 50)
        
        all_passed = True
        
        # Test 1: Import validation
        try:
            # Test core imports
            test_config = Config()
            test_storage = Storage()
            print("✅ Core module imports successfully")
            
            # Test bot imports
            from bot import BitcoinMiningNewsBotLegacy
            print("✅ Bot modules import successfully")
        except Exception as e:
            print(f"❌ Import error: {e}")
            all_passed = False
            return False
        
        # Test 2: Configuration validation
        try:
            config = Config.from_env()
            missing_vars = config.validate()
            
            if missing_vars:
                print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
                print("💡 This is expected in development - set these as GitHub secrets for production")
            else:
                print("✅ All environment variables configured")
        except Exception as e:
            print(f"❌ Configuration validation error: {e}")
            all_passed = False
        
        # Test 3: File system access
        try:
            # Test reading posted articles
            posted_data = Storage.load_json("posted_articles.json", {})
            print("✅ Posted articles file accessible")
            
            # Test writing (create temp file)
            test_data = {"test": "diagnostics", "timestamp": datetime.now().isoformat()}
            temp_file = "diagnostic_test.json"
            
            if Storage.save_json(temp_file, test_data):
                # Clean up test file
                try:
                    Path(temp_file).unlink(missing_ok=True)
                    print("✅ File write/read operations work correctly")
                except Exception:
                    print("⚠️ File cleanup failed (non-critical)")
            else:
                print("❌ File write operations failed")
                all_passed = False
                
        except Exception as e:
            print(f"❌ File system test failed: {e}")
            all_passed = False
        
        # Test 4: Bot instantiation
        try:
            bot = BitcoinMiningNewsBotLegacy(safe_mode=True)
            print("✅ Bot initializes successfully in safe mode")
        except Exception as e:
            print(f"❌ Bot initialization error: {e}")
            all_passed = False
            return False
        
        # Test 5: Run bot diagnostics
        print("\n🏃 Running internal bot diagnostics...")
        try:
            diagnostic_success = bot.run()
            if diagnostic_success:
                print("✅ Internal diagnostics completed successfully")
            else:
                print("⚠️ Internal diagnostics found issues (expected without API keys)")
        except Exception as e:
            print(f"❌ Internal diagnostics failed: {e}")
            all_passed = False
        
        # Test 6: Text processing
        try:
            test_article = {
                "title": "Test Bitcoin Mining Article",
                "body": "This is a test article about Bitcoin mining.",
                "url": "https://example.com/test",
                "source": {"title": "Test Source"}
            }
            
            tweet_text = TextUtils.create_tweet_text(test_article)
            if tweet_text and len(tweet_text) <= 280:
                print("✅ Text processing works correctly")
            else:
                print("⚠️ Text processing may have issues")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Text processing test failed: {e}")
            all_passed = False
        
        # Summary
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 ALL DIAGNOSTICS PASSED!")
            print("✅ Bot is ready for operation (pending API key configuration)")
        else:
            print("⚠️ SOME DIAGNOSTICS FAILED!")
            print("💡 Please review the issues above before running the bot")
        
        return all_passed


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