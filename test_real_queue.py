#!/usr/bin/env python3
"""
Test the fresh content prioritization with real queue data
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to Python path for imports  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import BitcoinMiningNewsBot
import unittest.mock as mock


def test_real_queue_staleness():
    """Test staleness detection with the real queue data"""
    print("🔍 Testing staleness with real queue data")
    print("=" * 60)
    
    # Load the real posted_articles.json
    with open("posted_articles.json", "r") as f:
        real_data = json.load(f)
    
    print(f"   Real queue has {len(real_data.get('queued_articles', []))} articles")
    
    with mock.patch('bot.APIClientManager'):
        bot = BitcoinMiningNewsBot()
        bot.posted_articles = real_data
        
        is_stale = bot._is_queue_stale()
        print(f"   Real queue staleness: {is_stale}")
        
        # Check individual article ages
        queued_articles = real_data.get("queued_articles", [])
        if queued_articles:
            print(f"   Sample article dates:")
            for i, article in enumerate(queued_articles[:3]):  # Check first 3
                date_str = article.get("dateTimePub", article.get("dateTime", "No date"))
                if date_str and date_str != "No date":
                    try:
                        article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        age_hours = (datetime.now() - article_date.replace(tzinfo=None)).total_seconds() / 3600
                        print(f"     Article {i+1}: {age_hours:.1f}h old ({date_str})")
                    except ValueError:
                        print(f"     Article {i+1}: Invalid date format ({date_str})")
                else:
                    print(f"     Article {i+1}: No date info")


def test_queue_cleaning():
    """Test what happens when we clean the real queue"""
    print("\n🔍 Testing queue cleaning with real data")
    print("=" * 60)
    
    # Load the real posted_articles.json  
    with open("posted_articles.json", "r") as f:
        real_data = json.load(f)
    
    original_count = len(real_data.get("queued_articles", []))
    print(f"   Original queue size: {original_count}")
    
    with mock.patch('bot.APIClientManager'):
        with mock.patch('utils.FileManager.save_posted_articles'):  # Don't actually save
            bot = BitcoinMiningNewsBot()
            bot.posted_articles = real_data.copy()  # Work on a copy
            
            bot._clean_stale_articles()
            
            new_count = len(bot.posted_articles.get("queued_articles", []))
            cleaned_count = original_count - new_count
            
            print(f"   After cleaning: {new_count} articles ({cleaned_count} removed)")
            
            if new_count > 0:
                print(f"   Remaining articles are fresh enough to post")
            else:
                print(f"   All articles were stale - bot would fetch fresh content")


if __name__ == "__main__":
    test_real_queue_staleness()
    test_queue_cleaning()