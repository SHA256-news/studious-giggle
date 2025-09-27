#!/usr/bin/env python3
"""
Queue Management Utility
------------------------
Consolidated tool for managing, viewing, and analyzing the tweet queue.
Replaces: show_queue_simple.py, show_queued_tweets.py, show_next_tweet.py, 
         debug_queue.py, clean_queue.py, clean_queue_auto.py
"""

import json
import logging
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

from utils import TextUtils, FileManager
from crypto_filter import filter_bitcoin_only_articles, get_unwanted_crypto_found

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class QueueManager:
    """Comprehensive queue management functionality"""
    
    def __init__(self):
        """Initialize the queue manager"""
        self.posted_articles = FileManager.load_posted_articles()
        self.queued_articles = self.posted_articles.get("queued_articles", [])
    
    def show_simple_preview(self, count: int = 10) -> None:
        """Show a simple preview of queued tweets (replaces show_queue_simple.py)"""
        print("🐦 NEXT TWEETS IN QUEUE")
        print("=" * 60)
        
        if not self.queued_articles:
            print("📭 No articles currently in queue")
            return
        
        print(f"📊 {len(self.queued_articles)} articles queued\n")
        
        # Show first N tweets
        for i, article in enumerate(self.queued_articles[:count], 1):
            tweet_text = TextUtils.create_enhanced_tweet_text(article)
            source = article.get("source", {}).get("title", "Unknown")
            
            print(f"{i:2d}. {tweet_text}")
            print(f"    └─ {source} ({len(tweet_text)} chars)")
            print()
        
        if len(self.queued_articles) > count:
            print(f"... and {len(self.queued_articles) - count} more tweets in queue")
    
    def show_detailed_preview(self, index: int = 0) -> None:
        """Show detailed preview of a specific queued tweet (replaces show_queued_tweets.py)"""
        if not self.queued_articles:
            print("📭 No articles in queue")
            return
        
        if index >= len(self.queued_articles):
            print(f"❌ Index {index} out of range. Queue has {len(self.queued_articles)} articles.")
            return
        
        article = self.queued_articles[index]
        
        print(f"\n{'='*80}")
        print(f"📱 TWEET #{index + 1} IN QUEUE")
        print(f"{'='*80}")
        
        # Article metadata
        title = article.get("title", "Unknown Title")
        source = article.get("source", {}).get("title", "Unknown Source")
        date = article.get("date", "Unknown Date")
        url = article.get("url", "No URL")
        
        print(f"📰 Original Article:")
        print(f"   Title: {title}")
        print(f"   Source: {source}")
        print(f"   Date: {date}")
        print(f"   URL: {url[:60]}{'...' if len(url) > 60 else ''}")
        
        # Show tweet formatting
        hook_tweet = TextUtils.create_hook_tweet(article)
        link_tweet = TextUtils.create_link_tweet(article)
        
        print(f"\n🐦 Tweet Format:")
        print(f"   Hook: {hook_tweet} ({len(hook_tweet)} chars)")
        if link_tweet:
            print(f"   Link: {link_tweet} ({len(link_tweet)} chars)")
    
    def show_next_tweet(self) -> None:
        """Show preview of the very next tweet (replaces show_next_tweet.py)"""
        if not self.queued_articles:
            print("📭 No tweets in queue")
            print("\nTo add tweets to the queue:")
            print("  python bot.py")
            return
        
        next_article = self.queued_articles[0]
        
        print("📱 NEXT TWEET TO BE PUBLISHED")
        print("=" * 50)
        
        # Try to generate Gemini content if available
        enhanced_article = next_article.copy()
        try:
            from gemini_client import GeminiClient
            from config import GeminiConfig
            import os
            
            if os.getenv('GEMINI_API_KEY'):
                print("🤖 Generating Gemini AI content...")
                gemini_config = GeminiConfig.from_env()
                gemini_client = GeminiClient(gemini_config)
                
                tweet_headline = gemini_client.generate_tweet_headline(next_article)
                tweet_summary = gemini_client.generate_tweet_summary(next_article)
                combined_content = f"{tweet_headline}\n\n{tweet_summary}"
                
                enhanced_article["gemini_content"] = combined_content
                print("✅ Gemini content generated")
            else:
                print("⚠️  Gemini API key not available - using standard formatting")
        except Exception as e:
            print(f"⚠️  Gemini generation failed: {e}")
        
        # Show the formatted tweet
        tweet_text = TextUtils.create_enhanced_tweet_text(enhanced_article)
        print(f"\n🐦 Tweet Text ({len(tweet_text)} chars):")
        print(f"   {tweet_text}")
        
        # Show source info
        source = next_article.get("source", {}).get("title", "Unknown")
        print(f"\n📰 Source: {source}")
        
        # Show URL if available
        url = next_article.get("url", "")
        if url:
            print(f"🔗 URL: {url}")
    
    def analyze_crypto_content(self) -> None:
        """Analyze and report on cryptocurrency content (replaces clean_queue.py analysis)"""
        if not self.queued_articles:
            print("📭 No articles in queue to analyze")
            return
        
        print("🔍 CRYPTOCURRENCY CONTENT ANALYSIS")
        print("=" * 60)
        print(f"📊 Analyzing {len(self.queued_articles)} queued articles...")
        
        bitcoin_only = []
        non_bitcoin = []
        
        for article in self.queued_articles:
            unwanted_cryptos = get_unwanted_crypto_found(article)
            if unwanted_cryptos:
                non_bitcoin.append((article, unwanted_cryptos))
            else:
                bitcoin_only.append(article)
        
        print(f"\n✅ Bitcoin-only articles: {len(bitcoin_only)}")
        print(f"❌ Non-Bitcoin articles: {len(non_bitcoin)}")
        
        if non_bitcoin:
            print("\n🚨 ARTICLES WITH NON-BITCOIN CONTENT:")
            for i, (article, cryptos) in enumerate(non_bitcoin, 1):
                title = article.get("title", "Unknown")[:60]
                print(f"  {i}. {title}...")
                print(f"     └─ Contains: {', '.join(cryptos)}")
    
    def clean_crypto_content(self, backup: bool = True) -> None:
        """Remove non-Bitcoin content from queue (replaces clean_queue_auto.py)"""
        if not self.queued_articles:
            print("📭 No articles in queue to clean")
            return
        
        original_count = len(self.queued_articles)
        
        if backup:
            # Create backup
            backup_data = self.posted_articles.copy()
            backup_filename = f"posted_articles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"💾 Created backup: {backup_filename}")
        
        # Filter articles
        print("🔍 Filtering out non-Bitcoin cryptocurrency content...")
        bitcoin_only_articles = filter_bitcoin_only_articles(self.queued_articles)
        
        # Update the queue
        self.posted_articles["queued_articles"] = bitcoin_only_articles
        
        # Save the cleaned queue
        FileManager.save_posted_articles(self.posted_articles)
        
        removed_count = original_count - len(bitcoin_only_articles)
        print(f"✅ Cleaned queue: {removed_count} non-Bitcoin articles removed")
        print(f"📊 Queue size: {original_count} → {len(bitcoin_only_articles)} articles")
    
    def debug_queue_processing(self) -> None:
        """Debug queue processing logic (replaces debug_queue.py)"""
        print("🔍 QUEUE PROCESSING DEBUG INFO")
        print("=" * 60)
        
        print(f"📊 Queue Statistics:")
        print(f"   Total queued articles: {len(self.queued_articles)}")
        print(f"   Posted articles count: {len(self.posted_articles.get('posted_uris', []))}")
        
        if self.queued_articles:
            print(f"\n📝 Sample Queue Entry:")
            sample = self.queued_articles[0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"   {key}: {value}")
        
        # Check for potential issues
        issues = []
        for i, article in enumerate(self.queued_articles):
            if not article.get("uri"):
                issues.append(f"Article {i+1}: Missing URI")
            if not article.get("title"):
                issues.append(f"Article {i+1}: Missing title")
            if not article.get("url"):
                issues.append(f"Article {i+1}: Missing URL")
        
        if issues:
            print(f"\n⚠️  Potential Issues Found:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ No issues detected in queue")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Bitcoin Mining News Bot Queue Manager")
    parser.add_argument("action", choices=[
        "simple", "detailed", "next", "analyze", "clean", "debug"
    ], help="Action to perform")
    parser.add_argument("--index", type=int, default=0, 
                       help="Index for detailed view (default: 0)")
    parser.add_argument("--count", type=int, default=10,
                       help="Number of items to show for simple view (default: 10)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup when cleaning (not recommended)")
    
    args = parser.parse_args()
    
    manager = QueueManager()
    
    if args.action == "simple":
        manager.show_simple_preview(args.count)
    elif args.action == "detailed":
        manager.show_detailed_preview(args.index)
    elif args.action == "next":
        manager.show_next_tweet()
    elif args.action == "analyze":
        manager.analyze_crypto_content()
    elif args.action == "clean":
        manager.clean_crypto_content(backup=not args.no_backup)
    elif args.action == "debug":
        manager.debug_queue_processing()


if __name__ == "__main__":
    main()