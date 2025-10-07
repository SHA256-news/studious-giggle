#!/usr/bin/env python3
"""
Bitcoin Mining News Bot - Clean Architecture Edition
Main entry point with dependency injection.
"""
import sys
import logging
from datetime import datetime
from typing import Optional

from src.config import BotConfig
from src.app import BitcoinMiningNewsBot
from src.adapters.eventregistry_adapter import EventRegistryAdapter
from src.adapters.gemini_adapter import GeminiAdapter
from src.adapters.twitter_adapter import TwitterAdapter
from src.adapters.json_storage import JSONStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_bot(config: BotConfig) -> Optional[BitcoinMiningNewsBot]:
    """
    Factory function to create bot with proper dependencies.
    
    Args:
        config: Bot configuration
        
    Returns:
        Configured bot instance or None if setup fails
    """
    try:
        # Create adapters
        news_provider = EventRegistryAdapter(api_key=config.eventregistry_api_key)
        storage = JSONStorage(filepath=config.storage_file)
        publisher = TwitterAdapter(
            api_key=config.twitter_api_key,
            api_secret=config.twitter_api_secret,
            access_token=config.twitter_access_token,
            access_token_secret=config.twitter_access_token_secret
        )
        
        # AI provider is optional
        ai_provider = None
        if config.gemini_api_key:
            try:
                ai_provider = GeminiAdapter(api_key=config.gemini_api_key)
                logger.info("AI provider (Gemini) initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AI provider: {e}")
        
        # Create bot
        bot = BitcoinMiningNewsBot(
            news_provider=news_provider,
            storage=storage,
            publisher=publisher,
            ai_provider=ai_provider,
            min_interval_minutes=config.min_interval_minutes
        )
        
        logger.info("Bot initialized successfully")
        return bot
        
    except Exception as e:
        logger.error(f"Failed to create bot: {e}")
        return None


def cmd_run(config: BotConfig) -> int:
    """Run the bot normally."""
    bot = create_bot(config)
    if not bot:
        logger.error("Failed to initialize bot")
        return 1
    
    try:
        logger.info("Starting bot run...")
        success = bot.run(
            keywords=config.bitcoin_keywords,
            max_articles=config.max_articles
        )
        
        if success:
            logger.info("Bot run completed successfully")
            return 0
        else:
            logger.info("Bot run completed (no articles posted)")
            return 0
            
    except Exception as e:
        logger.error(f"Bot run failed: {e}", exc_info=True)
        return 1


def cmd_diagnose(config: BotConfig) -> int:
    """Run diagnostics."""
    print("Bitcoin Mining News Bot - Diagnostics")
    print("=" * 50)
    print()
    
    # Check configuration
    print("Configuration:")
    validation_errors = config.validate()
    if validation_errors:
        print("  ❌ Configuration has errors:")
        for error in validation_errors:
            print(f"     - {error}")
        print()
        print("Please set the required environment variables:")
        print("  - TWITTER_API_KEY")
        print("  - TWITTER_API_SECRET")
        print("  - TWITTER_ACCESS_TOKEN")
        print("  - TWITTER_ACCESS_TOKEN_SECRET")
        print("  - EVENTREGISTRY_API_KEY")
        print("  - GEMINI_API_KEY")
        return 1
    else:
        print("  ✅ All required configuration present")
        print(f"  {config}")
    
    print()
    
    # Try to create bot
    bot = create_bot(config)
    if not bot:
        print("❌ Failed to initialize bot")
        return 1
    
    # Run diagnostics
    print("Bot Status:")
    diagnostics = bot.diagnose()
    
    print(f"  News Provider: {diagnostics.get('news_provider', 'unknown')}")
    print(f"  Storage: {diagnostics.get('storage', 'unknown')}")
    print(f"  Publisher Authenticated: {diagnostics.get('publisher_authenticated', 'unknown')}")
    print(f"  AI Provider: {diagnostics.get('ai_provider', 'unknown')}")
    print()
    print(f"  Queue Size: {diagnostics.get('queue_size', 0)} articles")
    print(f"  Posted Count: {diagnostics.get('posted_count', 0)} articles")
    
    last_run = diagnostics.get('last_run')
    if last_run:
        print(f"  Last Run: {last_run}")
    else:
        print("  Last Run: Never")
    
    print()
    print("✅ Diagnostics complete")
    return 0


def cmd_preview(config: BotConfig) -> int:
    """Preview next article in queue."""
    try:
        storage = JSONStorage(filepath=config.storage_file)
        queue = storage.load_queue()
        
        if not queue:
            print("Queue is empty - no articles to preview")
            return 0
        
        article = queue[0]
        
        print("Next Article in Queue:")
        print("=" * 50)
        print(f"Title: {article.title}")
        print(f"Source: {article.source}")
        print(f"URL: {article.url}")
        if article.published_at:
            print(f"Published: {article.published_at.strftime('%Y-%m-%d %H:%M UTC')}")
        print()
        print(f"Total in queue: {len(queue)} articles")
        
        return 0
        
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        return 1


def cmd_clean(config: BotConfig) -> int:
    """Clear the article queue."""
    try:
        storage = JSONStorage(filepath=config.storage_file)
        queue = storage.load_queue()
        
        if not queue:
            print("Queue is already empty")
            return 0
        
        print(f"Queue currently has {len(queue)} articles")
        response = input("Clear queue? (yes/no): ").strip().lower()
        
        if response == 'yes':
            storage.clear_queue()
            print("✅ Queue cleared")
            return 0
        else:
            print("❌ Cancelled")
            return 0
            
    except Exception as e:
        logger.error(f"Clean failed: {e}")
        return 1


def cmd_history(config: BotConfig, limit: int = 10) -> int:
    """Show posted articles history."""
    try:
        storage = JSONStorage(filepath=config.storage_file)
        posted = storage.load_posted_articles()
        
        if not posted:
            print("No posted articles in history")
            return 0
        
        # Show most recent first
        recent = list(reversed(posted))[:limit]
        
        print(f"Recently Posted Articles (last {len(recent)}):")
        print("=" * 50)
        
        for i, post in enumerate(recent, 1):
            print(f"{i}. {post.article.title}")
            print(f"   Source: {post.article.source}")
            print(f"   Posted: {post.posted_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Tweets: {len(post.tweet_ids)}")
            print()
        
        return 0
        
    except Exception as e:
        logger.error(f"History failed: {e}")
        return 1


def show_help():
    """Show usage information."""
    print("""
Bitcoin Mining News Bot

Usage:
  python main.py [command] [options]

Commands:
  run         Run the bot (fetch and post articles)
  diagnose    Check configuration and bot status
  preview     Preview next article in queue
  clean       Clear the article queue
  history     Show recently posted articles
  help        Show this help message

Examples:
  python main.py run
  python main.py diagnose
  python main.py preview
  python main.py history
  python main.py clean

Environment Variables Required:
  TWITTER_API_KEY
  TWITTER_API_SECRET
  TWITTER_ACCESS_TOKEN
  TWITTER_ACCESS_TOKEN_SECRET
  EVENTREGISTRY_API_KEY
  GEMINI_API_KEY
""")


def main():
    """Main entry point."""
    # Parse command
    if len(sys.argv) < 2:
        command = "run"
    else:
        command = sys.argv[1].lower()
    
    if command in ['help', '--help', '-h']:
        show_help()
        return 0
    
    # Load configuration
    try:
        config = BotConfig.from_env()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    # Route to command handler
    if command == "run":
        return cmd_run(config)
    elif command == "diagnose":
        return cmd_diagnose(config)
    elif command == "preview":
        return cmd_preview(config)
    elif command == "clean":
        return cmd_clean(config)
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        return cmd_history(config, limit)
    else:
        print(f"Unknown command: {command}")
        show_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
