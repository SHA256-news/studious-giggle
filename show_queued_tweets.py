#!/usr/bin/env python3
"""
Show Next Tweets in Queue
-------------------------
This script displays how the next tweets in the queue will read when they are posted.
It processes the queued articles from posted_articles.json and shows the formatted tweet text.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import the tweet creation utilities
from utils import TextUtils, FileManager
from config import BotConstants


def load_queued_articles() -> List[Dict[str, Any]]:
    """Load queued articles from posted_articles.json"""
    try:
        posted_articles = FileManager.load_posted_articles()
        queued_articles = posted_articles.get("queued_articles", [])
        logger.info(f"Loaded {len(queued_articles)} queued articles")
        return queued_articles
    except Exception as e:
        logger.error(f"Error loading queued articles: {e}")
        return []


def show_tweet_preview(article: Dict[str, Any], index: int) -> None:
    """Show how a single article will look as a tweet"""
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
    print(f"   URL: {url[:BotConstants.URL_PREVIEW_LENGTH]}{'...' if len(url) > BotConstants.URL_PREVIEW_LENGTH else ''}")
    
    # Generate both tweet formats for comparison
    try:
        enhanced_tweet = TextUtils.create_enhanced_tweet_text(article)
        original_tweet = TextUtils.create_original_tweet_text(article)
        
        print(f"\n🚀 HOW THIS WILL APPEAR ON TWITTER:")
        print(f"┌─ Enhanced Format (Default) ────────────────────────────────────┐")
        print(f"│ {enhanced_tweet:<62} │")
        print(f"└─ Characters: {len(enhanced_tweet):<52} ┘")
        
        print(f"\n📜 Original Format (Fallback):")
        print(f"   {original_tweet}")
        print(f"   Characters: {len(original_tweet)}")
        
        # Show key information extracted
        info = TextUtils.extract_key_info(article)
        extracted_features = []
        
        if info.get("companies"):
            extracted_features.append(f"Companies: {', '.join(info['companies'][:2])}")
        if info.get("financial_amounts"):
            extracted_features.append(f"Financial: {', '.join(info['financial_amounts'][:2])}")
        if info.get("technical_specs"):
            extracted_features.append(f"Technical: {', '.join(info['technical_specs'][:2])}")
        if info.get("locations"):
            extracted_features.append(f"Locations: {', '.join(info['locations'][:2])}")
        
        # Add concepts with clear fallback for better readability in logs
        concepts = info.get("concepts", [])
        concepts_str = ', '.join(concepts) if concepts else 'none'
        extracted_features.append(f"Concepts: {concepts_str}")
            
        if extracted_features:
            print(f"\n📊 Key Information Extracted:")
            for feature in extracted_features:
                print(f"   • {feature}")
        
        # Show tweet engagement potential
        relevance = article.get("relevance", 0)
        sentiment = article.get("sentiment", 0)
        
        print(f"\n📈 Article Metrics:")
        print(f"   • Relevance Score: {relevance}/100")
        print(f"   • Sentiment: {sentiment:.2f} "
              f"({'Positive' if sentiment > 0.1 else 'Negative' if sentiment < -0.1 else 'Neutral'})")
        
    except Exception as e:
        logger.error(f"Error generating tweet preview for article {index + 1}: {e}")
        print(f"\n❌ Error generating tweet preview: {e}")


def show_queue_summary(queued_articles: List[Dict[str, Any]]) -> None:
    """Show a summary of the entire queue"""
    print(f"\n{'🎯 TWITTER QUEUE SUMMARY':<80}")
    print(f"{'='*80}")
    
    if not queued_articles:
        print("📭 No articles currently in queue")
        return
        
    print(f"📊 Total Articles in Queue: {len(queued_articles)}")
    print(f"📅 Queue Processing Timeline:")
    
    # Estimate posting timeline (assuming 90-minute intervals)
    current_time = datetime.now()
    posting_interval_minutes = 90
    
    for i, article in enumerate(queued_articles[:5]):  # Show first 5
        posting_time = current_time.timestamp() + (i * posting_interval_minutes * 60)
        posting_datetime = datetime.fromtimestamp(posting_time)
        
        title = article.get("title", "Unknown Title")[:50] + "..." if len(article.get("title", "")) > 50 else article.get("title", "Unknown Title")
        source = article.get("source", {}).get("title", "Unknown")
        
        print(f"   {i+1}. {posting_datetime.strftime('%Y-%m-%d %H:%M')} - {title} ({source})")
    
    if len(queued_articles) > 5:
        print(f"   ... and {len(queued_articles) - 5} more articles")
    
    # Show source distribution
    sources = {}
    for article in queued_articles:
        source = article.get("source", {}).get("title", "Unknown")
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📰 Sources in Queue:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   • {source}: {count} article{'s' if count != 1 else ''}")


def main():
    """Main function to show queued tweets"""
    print("🐦 TWITTER BOT QUEUE PREVIEW")
    print("=" * 80)
    print("This shows how the next tweets in your queue will appear on Twitter")
    print("=" * 80)
    
    # Load queued articles
    queued_articles = load_queued_articles()
    
    if not queued_articles:
        print("\n📭 No articles currently in the queue!")
        print("\nTo add articles to the queue:")
        print("1. Run the bot normally: python bot.py")
        print("2. The bot will fetch new articles and queue them")
        print("3. Run this script again to see the preview")
        return
    
    # Show queue summary first
    show_queue_summary(queued_articles)
    
    # Ask user how many tweets to preview
    try:
        max_preview = min(len(queued_articles), 10)  # Limit to 10 for readability
        print(f"\n🔍 Showing preview of next {max_preview} tweets:")
        
        # Show each tweet preview
        for i, article in enumerate(queued_articles[:max_preview]):
            show_tweet_preview(article, i)
        
        if len(queued_articles) > max_preview:
            print(f"\n📋 Note: {len(queued_articles) - max_preview} additional articles are queued")
            print("   Run this script again to see them after these are posted")
            
    except KeyboardInterrupt:
        print("\n\n👋 Preview cancelled by user")
    except Exception as e:
        logger.error(f"Error during preview: {e}")
        print(f"\n❌ Error during preview: {e}")
    
    print(f"\n{'='*80}")
    print("📱 Ready to tweet! The bot will post these automatically every 90 minutes")
    print("🕐 Next posting time depends on the bot's schedule and rate limits")
    print("=" * 80)


if __name__ == "__main__":
    main()