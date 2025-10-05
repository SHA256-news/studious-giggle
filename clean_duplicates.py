#!/usr/bin/env python3
"""Script to clean duplicate articles from posted_articles.json queue."""

import json
from collections import defaultdict

def clean_duplicates():
    """Remove duplicate articles from the queued_articles array."""
    
    print("🧹 CLEANING DUPLICATE ARTICLES FROM QUEUE")
    print("=" * 50)
    
    # Load the posted_articles.json file
    try:
        with open("posted_articles.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading posted_articles.json: {e}")
        return
    
    queued_articles = data.get("queued_articles", [])
    original_count = len(queued_articles)
    
    print(f"📊 Original queue size: {original_count} articles")
    
    # Track URLs and keep only the first occurrence of each URL
    seen_urls = set()
    cleaned_articles = []
    duplicates_removed = 0
    
    for article in queued_articles:
        url = article.get("url", "")
        
        if url in seen_urls:
            duplicates_removed += 1
            title = article.get("title", "Unknown")
            print(f"🗑️  Removing duplicate: {title[:60]}...")
        else:
            seen_urls.add(url)
            cleaned_articles.append(article)
    
    # Update the data structure
    data["queued_articles"] = cleaned_articles
    
    print(f"\n📊 CLEANUP RESULTS:")
    print(f"   Original articles: {original_count}")
    print(f"   Duplicates removed: {duplicates_removed}")
    print(f"   Clean articles: {len(cleaned_articles)}")
    print(f"   Space saved: {duplicates_removed / original_count * 100:.1f}%")
    
    # Show some examples of removed duplicates
    if duplicates_removed > 0:
        print(f"\n🔍 DUPLICATE ANALYSIS:")
        
        # Count occurrences of each title to show the worst offenders
        title_counts = defaultdict(int)
        for article in queued_articles:  # Use original list to count duplicates
            title = article.get("title", "Unknown")
            title_counts[title] += 1
        
        # Show top duplicates
        worst_duplicates = sorted(title_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   Top duplicate titles:")
        for title, count in worst_duplicates:
            if count > 1:
                print(f"     {count}x: {title[:70]}...")
    
    # Save the cleaned data
    try:
        with open("posted_articles.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Successfully cleaned posted_articles.json")
        print(f"💾 Saved {len(cleaned_articles)} unique articles to queue")
    except Exception as e:
        print(f"❌ Error saving cleaned data: {e}")

if __name__ == "__main__":
    clean_duplicates()