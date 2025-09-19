#!/usr/bin/env python3
"""
Analyze and clean existing queued articles to remove non-Bitcoin cryptocurrency content.
"""

import json
import logging
from crypto_filter import filter_bitcoin_only_articles, get_unwanted_crypto_found

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('queue_cleaner')

def analyze_queued_articles():
    """Analyze current queued articles for non-Bitcoin content"""
    try:
        with open('posted_articles.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error("posted_articles.json not found")
        return
    
    queued_articles = data.get('queued_articles', [])
    logger.info(f"Analyzing {len(queued_articles)} queued articles...")
    
    bitcoin_only = []
    non_bitcoin = []
    
    for i, article in enumerate(queued_articles):
        title = article.get('title', '')
        body = article.get('body', '')
        
        title_cryptos = get_unwanted_crypto_found(title)
        body_cryptos = get_unwanted_crypto_found(body)
        
        if title_cryptos or body_cryptos:
            non_bitcoin.append({
                'index': i,
                'title': title[:100] + '...' if len(title) > 100 else title,
                'found_in_title': title_cryptos,
                'found_in_body': body_cryptos[:5],  # Limit to first 5
                'url': article.get('url', '')
            })
        else:
            bitcoin_only.append(article)
    
    logger.info(f"Results:")
    logger.info(f"  ✅ Bitcoin-only articles: {len(bitcoin_only)}")
    logger.info(f"  ❌ Non-Bitcoin articles: {len(non_bitcoin)}")
    
    if non_bitcoin:
        logger.info(f"\nNon-Bitcoin articles found:")
        for item in non_bitcoin[:10]:  # Show first 10
            found = item['found_in_title'] + item['found_in_body']
            logger.info(f"  - {item['title']}")
            logger.info(f"    Found: {', '.join(found[:5])}")
            logger.info(f"    URL: {item['url']}")
            logger.info("")
    
    return bitcoin_only, non_bitcoin, data

def clean_queued_articles(backup=True):
    """Clean queued articles to remove non-Bitcoin content"""
    bitcoin_only, non_bitcoin, original_data = analyze_queued_articles()
    
    if not non_bitcoin:
        logger.info("No non-Bitcoin articles found. Queue is already clean!")
        return
    
    # Create backup if requested
    if backup:
        backup_filename = 'posted_articles_backup.json'
        with open(backup_filename, 'w') as f:
            json.dump(original_data, f, indent=2)
        logger.info(f"Created backup: {backup_filename}")
    
    # Update the data with cleaned queue
    original_data['queued_articles'] = bitcoin_only
    
    # Write the cleaned data back
    with open('posted_articles.json', 'w') as f:
        json.dump(original_data, f, indent=2)
    
    logger.info(f"✅ Cleaned queue!")
    logger.info(f"  Removed: {len(non_bitcoin)} non-Bitcoin articles")
    logger.info(f"  Remaining: {len(bitcoin_only)} Bitcoin-only articles")
    
    return len(non_bitcoin)

if __name__ == "__main__":
    print("=" * 60)
    print("ANALYZING QUEUED ARTICLES FOR NON-BITCOIN CONTENT")
    print("=" * 60)
    
    # First analyze
    analyze_queued_articles()
    
    # Ask for confirmation before cleaning
    print("\n" + "=" * 60)
    response = input("Do you want to clean the queue (remove non-Bitcoin articles)? [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        removed_count = clean_queued_articles(backup=True)
        print(f"\n✅ Successfully removed {removed_count} non-Bitcoin articles from queue")
        print("📁 Backup created as 'posted_articles_backup.json'")
    else:
        print("❌ Queue cleaning cancelled")
    
    print("=" * 60)