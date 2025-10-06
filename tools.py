#!/usr/bin/env python3
"""
Bitcoin Mining Bot - Essential Tools
=====================================
Streamlined tools for managing the Bitcoin Mining Bot.

This module provides essential utilities for bot management:
- Queue preview and management
- Diagnostic tools
- Live API testing
"""

import json
import sys
import os
import logging
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

# Configure logging for tools
logger = logging.getLogger('bitcoin_mining_bot.tools')


class BotTools:
    """Essential tools for bot management."""
    
    @staticmethod
    def test_live_apis() -> bool:
        """Test live EventRegistry and Gemini APIs to preview threads without posting.
        
        Returns:
            bool: True if test was successful, False otherwise
        """
        try:
            print("🧪 Testing Live APIs - Real Preview Mode")
            print("=" * 50)
            print("📡 This will call real EventRegistry and Gemini APIs")
            print("🚫 NO tweets will be posted to Twitter")
            print()
            
            # Initialize bot with safe mode (no Twitter posting)
            from core import BitcoinMiningBot, Config
            
            config = Config.from_env()
            missing_keys = config.validate()
            
            if 'EVENTREGISTRY_API_KEY' in missing_keys:
                print("❌ EventRegistry API key missing - cannot test article fetching")
                return False
                
            print("🔄 Initializing bot in SAFE MODE (no Twitter posting)...")
            bot = BitcoinMiningBot(config=config)
            
            # Test EventRegistry API
            print("📰 Fetching fresh articles from EventRegistry Stream API...")
            try:
                articles = bot.news.fetch_articles()
                print(f"✅ Found {len(articles)} Bitcoin mining articles")
                
                if not articles:
                    print("⚠️  No articles found. This could mean:")
                    print("   - No recent Bitcoin mining news in last 6 hours")
                    print("   - API filters are too restrictive")
                    print("   - EventRegistry API issue")
                    return True
                    
            except Exception as e:
                print(f"❌ EventRegistry API error: {e}")
                return False
            
            # Test Gemini API (if available)
            gemini_available = 'GEMINI_API_KEY' not in missing_keys
            if gemini_available:
                print("🤖 Testing Gemini AI integration...")
                try:
                    gemini_client = bot.gemini
                    if gemini_client:
                        print("✅ Gemini client initialized successfully")
                    else:
                        print("⚠️  Gemini client failed to initialize")
                        gemini_client = None
                        gemini_available = False
                except Exception as e:
                    print(f"⚠️  Gemini API warning: {e}")
                    gemini_client = None
                    gemini_available = False
            else:
                print("⚠️  Gemini API key missing - will show fallback threads")
                gemini_client = None
            
            # Preview threads for top articles
            print()
            print("🧵 THREAD PREVIEWS")
            print("=" * 50)
            
            for i, article in enumerate(articles[:3], 1):
                print(f"\n📰 ARTICLE #{i}")
                print(f"Title: {article.title}")
                print(f"Source: {article.source or 'Unknown'}")
                print(f"Published: {article.date_published}")
                print(f"URL: {article.url}")
                print()
                
                # Generate thread preview
                print("🧵 GENERATED THREAD:")
                print("-" * 30)
                
                try:
                    from core import TextProcessor
                    # Handle optional gemini_client properly
                    thread = TextProcessor.create_tweet_thread(article, gemini_client if gemini_available else None)
                    
                    if thread is None:
                        print("❌ Thread generation failed - no content available")
                    else:
                        for j, tweet in enumerate(thread, 1):
                            print(f"Tweet {j}: {tweet}")
                            print(f"Length: {len(tweet)} chars")
                            if j < len(thread):
                                print("-" * 20)
                        
                        print("-" * 30)
                        print(f"✅ Thread complete: {len(thread)} tweets total")
                    
                except Exception as e:
                    print(f"❌ Error generating thread: {e}")
                
                print("\n" + "="*50)
            
            print("\n✅ Live API test completed!")
            print("\n💡 To use this in production:")
            print("   1. Review the threads above")
            print("   2. Adjust prompts in core.py if needed")
            print("   3. Let GitHub Actions run normally")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during API testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def show_next_tweet():
        """Show the next tweet that would be posted."""
        print("🔮 Preview Next Tweet")
        print("=" * 30)
        
        try:
            # Load queued articles
            posted_articles = Storage.load_json("posted_articles.json", {"posted": [], "queue": []})
            queue = posted_articles.get("queue", [])
            
            if not queue:
                print("📭 No articles queued")
                print("💡 Run the bot to fetch fresh articles")
                return True
            
            # 🛡️ BUG FIX (Oct 6, 2025): ALWAYS check bounds before accessing queue[0]
            # NEVER access array indices without bounds checking - causes IndexError crashes
            # See /BUG-FIXES-OCTOBER-2025.md for details
            if len(queue) == 0:
                print("📭 No articles queued")
                print("💡 Run the bot to fetch fresh articles")
                return True
            
            next_article = queue[0]
            print(f"📰 Next Article:")
            print(f"   Title: {next_article.get('title', 'Unknown')}")
            
            # Safely handle source data access
            source_data = next_article.get('source', {})
            if isinstance(source_data, dict):
                source = source_data.get('title', 'Unknown')
            else:
                source = str(source_data) if source_data else 'Unknown'
            print(f"   Source: {source}")
            
            print(f"   URL: {next_article.get('url', 'No URL')}")
            
            # Generate tweet text
            tweet_text = TextUtils.create_tweet_text(next_article)
            print(f"\n🐦 Tweet Preview:")
            print(f"   Text: {tweet_text}")
            print(f"   Length: {len(tweet_text)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Error showing next tweet: {e}")
            return False
    
    @staticmethod
    def show_queue_simple():
        """Show simple queue view."""
        print("📋 Article Queue")
        print("=" * 25)
        
        try:
            posted_articles = Storage.load_json("posted_articles.json", {"posted": [], "queue": []})
            queue = posted_articles.get("queue", [])
            posted = posted_articles.get("posted", [])
            
            print(f"📊 Queue Stats:")
            print(f"   Queued: {len(queue)} articles")
            print(f"   Posted: {len(posted)} articles")
            
            if not queue:
                print("\n📭 No articles currently queued")
                return True
            
            print(f"\n📋 Queued Articles:")
            for i, article in enumerate(queue):
                title = article.get("title", "Unknown Title")
                source_data = article.get("source", {})
                
                if isinstance(source_data, dict):
                    source = source_data.get("title", "Unknown")
                else:
                    source = str(source_data) if source_data else "Unknown"
                
                print(f"\n{i+1}. {title[:70]}{'...' if len(title) > 70 else ''}")
                print(f"   Source: {source}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error showing queue: {e}")
            return False
    
    @staticmethod
    def clean_queue():
        """Interactive queue cleaning."""
        print("🧹 Clean Queue")
        print("=" * 20)
        
        try:
            posted_articles = Storage.load_json("posted_articles.json", {"posted": [], "queue": []})
            queue = posted_articles.get("queue", [])
            
            if not queue:
                print("📭 Queue is already empty")
                return
            
            print(f"📊 Found {len(queue)} queued articles")
            print("📋 Review and remove unwanted articles:")
            print()
            
            # Show articles with removal options
            removed_count = 0
            indices_to_remove = []
            
            for i, article in enumerate(queue):
                title = article.get("title", "Unknown Title")
                source_data = article.get("source", {})
                
                if isinstance(source_data, dict):
                    source = source_data.get("title", "Unknown")
                else:
                    source = str(source_data) if source_data else "Unknown"
                
                print(f"\n{i+1}. {title[:70]}{'...' if len(title) > 70 else ''}")
                print(f"   Source: {source}")
                
                try:
                    response = input("   Keep this article? (y/n/q to quit): ").strip().lower()
                    if response == 'q':
                        break
                    elif response == 'n':
                        indices_to_remove.append(i)
                        removed_count += 1
                except KeyboardInterrupt:
                    print("\n⏹️  Cleaning cancelled")
                    return
            
            # Remove articles (in reverse order to maintain indices)
            for i in reversed(indices_to_remove):
                try:
                    # Atomic bounds check and pop operation to prevent race conditions
                    if 0 <= i < len(queue):
                        removed_article = queue.pop(i)
                        if removed_article:
                            title = removed_article.get('title', 'Unknown') if isinstance(removed_article, dict) else 'Invalid data'
                            print(f"🗑️ Removed: {title[:50]}{'...' if len(str(title)) > 50 else ''}")
                    else:
                        logger.warning(f"⚠️ Invalid index {i} for queue of length {len(queue)}")
                except (IndexError, ValueError) as e:
                    # Comprehensive error handling for any queue modification issues
                    logger.warning(f"⚠️ Could not remove article at index {i}: {e}")
                    # Continue processing other indices even if one fails
                    continue
                except Exception as e:
                    # Catch any unexpected errors to prevent total failure
                    logger.error(f"❌ Unexpected error removing article at index {i}: {e}")
                    continue
            
            # Save cleaned queue
            if removed_count > 0:
                posted_articles["queue"] = queue
                try:
                    FileManager.save_posted_articles(posted_articles)
                    print(f"\n✅ Cleaned {removed_count} articles from queue")
                    print(f"📊 Remaining: {len(queue)} articles")
                except Exception as save_error:
                    print(f"❌ Error saving cleaned queue: {save_error}")
            else:
                print("\n📋 No articles removed")
                
        except Exception as e:
            print(f"❌ Error cleaning queue: {e}")
    
    @staticmethod
    def diagnose_bot():
        """Run comprehensive bot diagnostics."""
        print("🔍 Bot Diagnostics")
        print("=" * 25)
        
        all_passed = True
        
        # Test 1: Core imports
        try:
            test_config = Config()
            test_storage = Storage()
            print("✅ Core modules imported successfully")
        except Exception as e:
            print(f"❌ Core import failed: {e}")
            all_passed = False
        
        # Test 2: File structure
        try:
            required_files = ["core.py", "bot.py", "requirements.txt"]
            missing_files = [f for f in required_files if not os.path.exists(f)]
            
            if missing_files:
                print(f"⚠️ Missing files: {missing_files}")
                all_passed = False
            else:
                print("✅ Required files present")
        except Exception as e:
            print(f"❌ File structure check failed: {e}")
            all_passed = False
        
        # Test 3: Configuration
        try:
            config = Config.from_env()
            missing_keys = config.validate()
            
            if missing_keys:
                print(f"⚠️ Missing environment variables: {missing_keys}")
                print("💡 This is expected in development - set these for production")
            else:
                print("✅ All environment variables configured")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            all_passed = False
        
        # Test 4: Storage operations
        try:
            posted_data = Storage.load_json("posted_articles.json", {})
            print("✅ Storage operations working")
        except Exception as e:
            print(f"❌ Storage test failed: {e}")
            all_passed = False
        
        # Test 5: Bot initialization
        try:
            bot = BitcoinMiningBot()
            print("✅ Bot initialization successful")
        except Exception as e:
            print(f"❌ Bot initialization failed: {e}")
            all_passed = False
        
        # Test 6: Text processing
        try:
            test_article = Article(
                title="Test Bitcoin Mining Article",
                body="This is a test article about Bitcoin mining.",
                url="https://example.com/test",
                source="Test Source"
            )
            
            thread = TextProcessor.create_tweet_thread(test_article, None)
            if thread and len(thread) > 0:
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
    
    @staticmethod
    def show_posted_history(limit: int = 10) -> None:
        """Show recently posted articles history with full metadata."""
        try:
            posted_data = Storage.load_json("posted_articles.json", {})
            posted_history = posted_data.get("posted_articles_history", [])
            
            print("📰 Recently Posted Articles History")
            print("=" * 50)
            
            if not posted_history:
                print("❌ No posted articles history found")
                print("💡 History tracking was added recently - future posts will be recorded")
                return
            
            # Show most recent articles first
            recent_articles = list(reversed(posted_history))[-limit:]
            recent_articles.reverse()  # Most recent first
            
            for i, article in enumerate(recent_articles, 1):
                print(f"\n📝 #{i} - Posted Article")
                print(f"Title: {article.get('title', 'Unknown')}")
                print(f"Source: {article.get('source', 'Unknown')}")
                print(f"URL: {article.get('url', 'Unknown')}")
                
                # Format dates nicely
                date_posted = article.get('date_posted')
                if date_posted:
                    try:
                        posted_dt = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
                        print(f"Posted: {posted_dt.strftime('%Y-%m-%d %H:%M UTC')}")
                    except:
                        print(f"Posted: {date_posted}")
                
                date_published = article.get('date_published')
                if date_published:
                    try:
                        pub_dt = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
                        print(f"Published: {pub_dt.strftime('%Y-%m-%d %H:%M UTC')}")
                    except:
                        print(f"Published: {date_published}")
                
                # Show preview of article content
                preview = article.get('body_preview', '')
                if preview:
                    print(f"Preview: {preview}")
                
                print("-" * 40)
            
            print(f"\n📊 Total articles in history: {len(posted_history)}")
            print(f"📊 Total URLs tracked: {len(posted_data.get('posted_uris', []))}")
            
            if len(posted_history) > limit:
                print(f"💡 Showing latest {limit} articles. Use 'python tools.py history 20' for more")
            
        except Exception as e:
            print(f"❌ Error loading posted history: {e}")


def main():
    """Main CLI interface for bot tools."""
    if len(sys.argv) < 2:
        print("🛠️ Bitcoin Mining Bot Tools")
        print("=" * 30)
        print("Available commands:")
        print("  preview    - Show next tweet to be posted")
        print("  queue      - Show simple queue view") 
        print("  clean      - Clean unwanted articles from queue")
        print("  history    - Show recently posted articles (default: 10)")
        print("  diagnose   - Run bot diagnostics")
        print("  test       - Test live APIs (EventRegistry + Gemini)")
        print("\nUsage: python tools.py <command> [args]")
        print("Examples:")
        print("  python tools.py history 20   # Show last 20 posted articles")
        return
    
    # Safe access to sys.argv[1] since we've checked length above
    command = sys.argv[1].lower()
    
    if command == "preview":
        BotTools.show_next_tweet()
    elif command == "queue":
        BotTools.show_queue_simple()
    elif command == "clean":
        BotTools.clean_queue()
    elif command == "history":
        # Parse optional limit argument
        limit = 10  # default
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
                if limit <= 0:
                    print("❌ Limit must be a positive number")
                    return
            except ValueError:
                print("❌ Invalid limit number")
                return
        BotTools.show_posted_history(limit)
    elif command == "diagnose":
        BotTools.diagnose_bot()
    elif command == "test":
        BotTools.test_live_apis()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available: preview, queue, clean, history, diagnose, test")


if __name__ == "__main__":
    main()