#!/usr/bin/env python3
"""
Clean queued articles automatically to remove non-Bitcoin cryptocurrency content.
"""

import json
import logging
from crypto_filter import filter_bitcoin_only_articles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('queue_cleaner')

def clean_queued_articles_auto():
    """Automatically clean queued articles to remove non-Bitcoin content"""
    try:
        with open('posted_articles.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error("posted_articles.json not found")
        return
    
    original_queued = data.get('queued_articles', [])
    logger.info(f"Original queue: {len(original_queued)} articles")
    
    # Filter to Bitcoin-only articles
    bitcoin_only, excluded_count, excluded_details = filter_bitcoin_only_articles(original_queued)
    
    if excluded_count == 0:
        logger.info("No non-Bitcoin articles found. Queue is already clean!")
        return
    
    # Create backup
    backup_filename = 'posted_articles_backup.json'
    with open(backup_filename, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Created backup: {backup_filename}")
    
    # Update the data with cleaned queue
    data['queued_articles'] = bitcoin_only
    
    # Write the cleaned data back
    with open('posted_articles.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ Queue cleaned successfully!")
    logger.info(f"  Removed: {excluded_count} non-Bitcoin articles")
    logger.info(f"  Remaining: {len(bitcoin_only)} Bitcoin-only articles")
    
    # Show some of the removed articles
    if excluded_details:
        logger.info(f"Examples of removed articles:")
        for detail in excluded_details[:5]:
            found = detail['found_in_title'] + detail['found_in_body']
            logger.info(f"  - {detail['title'][:50]}... (mentioned: {', '.join(found[:3])})")
    
    return excluded_count

if __name__ == "__main__":
    print("Cleaning queued articles automatically...")
    removed_count = clean_queued_articles_auto()
    print(f"Done! Removed {removed_count} non-Bitcoin articles.")