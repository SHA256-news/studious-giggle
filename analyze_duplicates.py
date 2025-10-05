#!/usr/bin/env python3
"""Script to analyze posted_articles.json for duplicate RIOT URLs."""

import json

def analyze_duplicates():
    """Analyze the posted_articles.json file for duplicate RIOT entries."""
    
    print("🔍 ANALYZING DUPLICATE RIOT ARTICLES")
    print("=" * 50)
    
    # Load the posted_articles.json file
    try:
        with open("posted_articles.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading posted_articles.json: {e}")
        return
    
    # Target URL we're investigating
    target_url = "https://de.marketscreener.com/boerse-nachrichten/riot-platforms-produziert-445-bitcoins-im-september-2025-ce7d5bdfdd88ff21"
    
    print(f"🎯 Target URL: {target_url}")
    print()
    
    # Check if URL is in posted_uris array
    posted_uris = data.get("posted_uris", [])
    is_in_posted_uris = target_url in posted_uris
    
    print(f"📊 POSTED_URIS ANALYSIS:")
    print(f"   Total posted URIs: {len(posted_uris)}")
    print(f"   Target URL in posted_uris? {'✅ YES' if is_in_posted_uris else '❌ NO'}")
    
    if is_in_posted_uris:
        # Count occurrences in posted_uris
        uri_count = posted_uris.count(target_url)
        print(f"   Occurrences in posted_uris: {uri_count}")
        
        # Find positions
        positions = [i for i, uri in enumerate(posted_uris) if uri == target_url]
        print(f"   Positions: {positions}")
    
    print()
    
    # Check queued_articles array
    queued_articles = data.get("queued_articles", [])
    print(f"📊 QUEUED_ARTICLES ANALYSIS:")
    print(f"   Total queued articles: {len(queued_articles)}")
    
    # Find RIOT articles in queue
    riot_articles = []
    for i, article in enumerate(queued_articles):
        article_url = article.get("url", "")
        if target_url in article_url or "riot" in article.get("title", "").lower():
            riot_articles.append((i, article))
    
    print(f"   RIOT-related articles in queue: {len(riot_articles)}")
    
    if riot_articles:
        print(f"   RIOT articles details:")
        for i, (index, article) in enumerate(riot_articles):
            title = article.get("title", "Unknown")
            url = article.get("url", "Unknown")
            print(f"     {i+1}. Index {index}: {title[:80]}...")
            print(f"        URL: {url}")
            
            # Check if this specific URL matches our target
            if url == target_url:
                print(f"        🔥 EXACT MATCH FOUND!")
    
    print()
    
    # Summary of the bug
    print("🐛 BUG ANALYSIS:")
    print("=" * 30)
    
    if is_in_posted_uris and riot_articles:
        print("❌ DUPLICATE DETECTED!")
        print("   The URL is in posted_uris (meaning it was posted)")
        print("   BUT it's also in queued_articles (meaning it will be posted again)")
        print("   This indicates a failure in the deduplication logic!")
    elif not is_in_posted_uris and riot_articles:
        print("⚠️  POTENTIAL ISSUE:")
        print("   URL not in posted_uris yet but found in queue")
        print("   This might be normal if it hasn't been posted yet")
    elif is_in_posted_uris and not riot_articles:
        print("✅ EXPECTED BEHAVIOR:")
        print("   URL is in posted_uris and NOT in queue")
        print("   This is how it should work")
    else:
        print("📭 URL not found in either list")
    
    # Check for any RIOT-related duplicates in general
    print()
    print("🔍 GENERAL RIOT DUPLICATE CHECK:")
    print("=" * 40)
    
    all_riot_titles = []
    for article in queued_articles:
        title = article.get("title", "")
        if "riot" in title.lower() and "produziert" in title.lower():
            all_riot_titles.append(title)
    
    print(f"   Found {len(all_riot_titles)} RIOT production articles in queue:")
    for i, title in enumerate(all_riot_titles, 1):
        print(f"     {i}. {title}")
    
    # Check for exact title duplicates
    title_counts = {}
    for article in queued_articles:
        title = article.get("title", "")
        if title in title_counts:
            title_counts[title] += 1
        else:
            title_counts[title] = 1
    
    duplicates = {title: count for title, count in title_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n🚨 FOUND {len(duplicates)} DUPLICATE TITLES IN QUEUE:")
        for title, count in duplicates.items():
            print(f"   {count}x: {title}")
    else:
        print(f"\n✅ No duplicate titles found in queue")

if __name__ == "__main__":
    analyze_duplicates()