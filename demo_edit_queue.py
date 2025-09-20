#!/usr/bin/env python3
"""
Demo: Edit Queue Titles
-----------------------
This demonstrates the title editing functionality without requiring user interaction.
Shows how the edit_queue_titles.py script works.
"""

import json
import logging
from utils import TextUtils, FileManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def demo_title_editing():
    """Demonstrate the title editing functionality"""
    print("🎭 DEMO: Queue Title Editing Functionality")
    print("=" * 80)
    
    # Load current queue
    posted_articles = FileManager.load_posted_articles()
    queued_articles = posted_articles.get("queued_articles", [])
    
    if not queued_articles:
        print("📭 No articles in queue for demo")
        return
    
    print(f"📊 Found {len(queued_articles)} articles in queue")
    
    # Show first few articles and their current tweets
    print("\n📋 CURRENT QUEUE (first 3 articles):")
    print("-" * 60)
    
    for i, article in enumerate(queued_articles[:3], 1):
        title = article.get("title", "Unknown Title")
        source = article.get("source", {}).get("title", "Unknown Source")
        
        try:
            current_tweet = TextUtils.create_enhanced_tweet_text(article)
        except Exception:
            current_tweet = "Error generating tweet"
        
        print(f"\n{i}. Original Title: {title}")
        print(f"   Source: {source}")
        print(f"   Current Tweet: {current_tweet}")
        print(f"   Characters: {len(current_tweet)}/280")
    
    # Demonstrate editing the first article
    if len(queued_articles) > 0:
        print(f"\n✏️  DEMO: Editing Article #1")
        print("=" * 50)
        
        first_article = queued_articles[0]
        original_title = first_article.get("title", "")
        
        print(f"Original title: {original_title}")
        
        # Simulate editing with a shorter, more focused title
        if "Cleanspark" in original_title:
            demo_new_title = "CleanSpark Options Activity Shows Bullish Sentiment"
        elif "Rail Boss" in original_title:
            demo_new_title = "Russian Railway Officials Arrested for Crypto Mining Theft"
        elif "Bhutan" in original_title:
            demo_new_title = "Bhutan Government Transfers 343 Bitcoin to New Wallet"
        else:
            demo_new_title = "Bitcoin Mining News Update"
        
        print(f"Demo new title: {demo_new_title}")
        
        # Show tweet comparison
        try:
            original_tweet = TextUtils.create_enhanced_tweet_text(first_article)
            
            # Create a copy with the new title
            demo_article = first_article.copy()
            demo_article["title"] = demo_new_title
            new_tweet = TextUtils.create_enhanced_tweet_text(demo_article)
            
            print(f"\n📱 TWEET COMPARISON:")
            print(f"   Original: {original_tweet}")
            print(f"   Characters: {len(original_tweet)}/280")
            print(f"   New:      {new_tweet}")
            print(f"   Characters: {len(new_tweet)}/280")
            
            # Character savings
            char_diff = len(original_tweet) - len(new_tweet)
            if char_diff > 0:
                print(f"   💡 Saved {char_diff} characters!")
            elif char_diff < 0:
                print(f"   ⚠️  Used {abs(char_diff)} more characters")
            else:
                print(f"   📝 Same character count")
                
        except Exception as e:
            print(f"   ❌ Error generating demo tweets: {e}")
    
    print(f"\n🛠️  HOW TO USE THE EDITOR:")
    print("=" * 50)
    print("1. Run: python edit_queue_titles.py")
    print("2. Choose Interactive Mode or Batch Mode")
    print("3. Select articles to edit by number")
    print("4. Enter new titles and preview the tweets")
    print("5. Save changes when satisfied")
    
    print(f"\n✨ FEATURES:")
    print("• Edit any article title in the queue")
    print("• Real-time tweet preview with character count")
    print("• Validation for title length and tweet limits") 
    print("• Interactive or batch editing modes")
    print("• Safe: changes are saved only when you confirm")
    print("• Original article content remains unchanged")
    
    print(f"\n📚 USE CASES:")
    print("• Make titles more engaging for Twitter")
    print("• Fix typos or formatting issues")
    print("• Customize content for your audience")
    print("• Ensure tweets stay within character limits")
    print("• Remove unnecessary words or technical jargon")


if __name__ == "__main__":
    demo_title_editing()