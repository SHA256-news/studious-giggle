#!/usr/bin/env python3
"""
Clean the queue using enhanced Bitcoin mining content filtering
"""

import json
import shutil
from crypto_filter import filter_bitcoin_only_articles

def clean_queue_with_enhanced_filtering():
    """Clean the queue using the enhanced filtering"""
    print("🧹 Cleaning queue with enhanced Bitcoin mining filtering...")
    
    # Backup original file
    shutil.copy('posted_articles.json', 'posted_articles_backup_pre_clean.json')
    print("✅ Created backup: posted_articles_backup_pre_clean.json")
    
    # Load current data
    with open('posted_articles.json', 'r') as f:
        data = json.load(f)
    
    queued_articles = data.get('queued_articles', [])
    original_count = len(queued_articles)
    
    print(f"📊 Original queue: {original_count} articles")
    
    if original_count == 0:
        print("✅ Queue is already empty - nothing to clean")
        return
    
    # Apply enhanced filtering
    filtered_articles, excluded_count, excluded_details = filter_bitcoin_only_articles(queued_articles)
    
    print(f"📊 After enhanced filtering: {len(filtered_articles)} valid articles, {excluded_count} filtered out")
    
    if excluded_count > 0:
        print(f"\n🗑️  Removed articles:")
        for i, detail in enumerate(excluded_details, 1):
            title = detail['title']
            reason = detail.get('reason', 'Unknown')
            print(f"   {i}. {title}")
            print(f"      Reason: {reason}")
        
        # Update the queue
        data['queued_articles'] = filtered_articles
        
        # Save updated data
        with open('posted_articles.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Queue cleaned successfully!")
        print(f"   • Removed: {excluded_count} non-Bitcoin mining articles")
        print(f"   • Kept: {len(filtered_articles)} genuine Bitcoin mining articles")
        print(f"   • Backup saved as: posted_articles_backup_pre_clean.json")
    else:
        print(f"\n✅ All articles in queue are already valid Bitcoin mining content")
    
    return excluded_count

if __name__ == "__main__":
    excluded_count = clean_queue_with_enhanced_filtering()
    
    if excluded_count > 0:
        print(f"\n🎉 SUCCESS: Queue cleaned!")
        print(f"   The bot will now only post genuine Bitcoin mining news")
    else:
        print(f"\n👍 Queue was already clean - no changes needed")