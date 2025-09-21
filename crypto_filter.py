"""
Cryptocurrency filtering module for Bitcoin Mining News Bot
Simplified version that filters out non-Bitcoin cryptocurrency mentions
"""

import re
import logging

logger = logging.getLogger('bitcoin_mining_bot')

# Essential unwanted crypto keywords (shortened list)
UNWANTED_CRYPTO_KEYWORDS = [
    # Major altcoins
    'ethereum', 'eth', 'binance coin', 'bnb', 'solana', 'sol', 'xrp', 'ripple',
    'dogecoin', 'doge', 'cardano', 'ada', 'litecoin', 'ltc', 'bitcoin cash', 'bch',
    'shiba inu', 'shib', 'polygon', 'matic', 'chainlink', 'link',
    
    # Stablecoins
    'tether', 'usdt', 'usd coin', 'usdc', 'dai', 'busd',
    
    # Generic terms
    'altcoin', 'altcoins', 'shitcoin', 'shitcoins', 'memecoin', 'memecoins'
]

def contains_unwanted_crypto(text):
    """
    Check if text contains mentions of non-Bitcoin cryptocurrencies
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if unwanted cryptocurrency found, False otherwise
    """
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Simple keyword matching
    for keyword in UNWANTED_CRYPTO_KEYWORDS:
        if keyword in text_lower:
            return True
            
    return False

def filter_bitcoin_only_articles(articles):
    """Filter articles to only include Bitcoin-related content"""
    if not articles:
        return []
    
    filtered_articles = []
    
    for article in articles:
        title = article.get("title", "") or ""
        body = article.get("body", "") or ""
        
        # Check if article mentions unwanted cryptos
        if contains_unwanted_crypto(title) or contains_unwanted_crypto(body):
            logger.info(f"Filtered out article mentioning non-Bitcoin crypto: {title[:50]}...")
            continue
        
        filtered_articles.append(article)
    
    logger.info(f"Crypto filtering: {len(articles)} -> {len(filtered_articles)} articles")
    return filtered_articles