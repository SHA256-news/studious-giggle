#!/usr/bin/env python3
"""
Cryptocurrency filtering module for Bitcoin Mining News Bot.
Filters out articles mentioning non-Bitcoin cryptocurrencies.
"""

import re
import logging

logger = logging.getLogger('bitcoin_mining_bot')

# Comprehensive list of unwanted cryptocurrencies and their tickers
UNWANTED_CRYPTO_KEYWORDS = [
    # Major altcoins by market cap
    'ethereum', 'eth',
    'binance coin', 'bnb', 
    'solana', 'sol',
    'xrp', 'ripple',
    'dogecoin', 'doge',
    'cardano', 'ada',
    'avalanche', 'avax',
    'polkadot', 'dot',
    'chainlink', 'link',
    'polygon', 'matic',
    'litecoin', 'ltc',
    'bitcoin cash', 'bch',
    'shiba inu', 'shib',
    'uniswap', 'uni',
    'tron', 'trx',
    'cosmos', 'atom',
    'ethereum classic', 'etc',
    'stellar', 'xlm',
    'algorand', 'algo',
    'vechain', 'vet',
    'filecoin', 'fil',
    'terra', 'luna',
    'fantom', 'ftm',
    'hedera', 'hbar',
    'near protocol', 'near',
    'cronos', 'cro',
    'apecoin', 'ape',
    'flow', 'flow',
    'decentraland', 'mana',
    'sandbox', 'sand',
    'axie infinity', 'axs',
    'theta', 'theta',
    'elrond', 'egld',
    'icp', 'internet computer',
    'tezos', 'xtz',
    'eos', 'eos',
    'aave', 'aave',
    'maker', 'mkr',
    'compound', 'comp',
    'yearn finance', 'yfi',
    'sushiswap', 'sushi',
    'curve', 'crv',
    'pancakeswap', 'cake',
    'ftx token', 'ftt',
    'huobi token', 'ht',
    'kucoin token', 'kcs',
    'okb', 'okb',
    'leo token', 'leo',
    
    # Privacy coins
    'monero', 'xmr',
    'zcash', 'zec',
    'dash', 'dash',
    'verge', 'xvg',
    'beam', 'beam',
    'grin', 'grin',
    
    # Meme coins
    'pepecoin', 'pepe',
    'floki', 'floki',
    'safemoon', 'safemoon',
    'babydoge', 'babydoge',
    
    # DeFi tokens
    'balancer', 'bal',
    'synthetix', 'snx',
    'bancor', 'bnt',
    'kyber', 'knc',
    '0x', 'zrx',
    
    # Gaming/NFT tokens
    'enjin', 'enj',
    'gala', 'gala',
    'chiliz', 'chz',
    'wax', 'waxp',
    
    # Infrastructure tokens
    'graph', 'grt',
    'livepeer', 'lpt',
    'render', 'rndr',
    'arweave', 'ar',
    'storj', 'storj',
    
    # Stablecoins
    'tether', 'usdt',
    'usd coin', 'usdc',
    'dai', 'dai',
    'busd', 'busd',
    'terra usd', 'ust',
    'frax', 'frax',
    
    # Exchange tokens
    'binance', 'bnb',
    'ftx', 'ftt',
    'crypto.com', 'cro',
    
    # Layer 2 and scaling (excluding Bitcoin's Lightning Network)
    'arbitrum', 'arb',
    'optimism', 'op',
    'immutable x', 'imx',
    
    # Other notable mentions
    'altcoin', 'altcoins',
    'shitcoin', 'shitcoins',
    'memecoin', 'memecoins',
    'defi token', 'defi tokens',
    'nft token', 'nft tokens',
    'governance token', 'governance tokens',
    'utility token', 'utility tokens',
    'multiple cryptocurrencies', 'multiple coins',
    'various cryptocurrencies', 'various coins',
    'all cryptocurrencies', 'all coins',
    'several altcoins', 'many altcoins',
]

# Convert to lowercase and create sets for efficient lookup
UNWANTED_CRYPTO_SET = set(keyword.lower() for keyword in UNWANTED_CRYPTO_KEYWORDS)

# Separate single words from phrases for optimized matching
SINGLE_WORDS = {keyword for keyword in UNWANTED_CRYPTO_SET if ' ' not in keyword}
PHRASES = {keyword for keyword in UNWANTED_CRYPTO_SET if ' ' in keyword}

# Pre-compile regex patterns for single words
SINGLE_WORD_PATTERNS = {
    word: re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    for word in SINGLE_WORDS
}


def contains_unwanted_crypto(text):
    """
    Check if text contains mentions of non-Bitcoin cryptocurrencies.
    
    Args:
        text (str): Text to check (title, body, etc.)
        
    Returns:
        bool: True if unwanted cryptocurrency found, False otherwise
    """
    if not text:
        return False
        
    text_lower = text.lower()
    
    # Check phrases first (faster string containment)
    for phrase in PHRASES:
        if phrase in text_lower:
            return True
    
    # Check single words with pre-compiled patterns
    for word, pattern in SINGLE_WORD_PATTERNS.items():
        if pattern.search(text):
            return True
            
    return False


def get_unwanted_crypto_found(text):
    """
    Get list of unwanted cryptocurrencies found in text.
    Useful for debugging/logging.
    
    Args:
        text (str): Text to check
        
    Returns:
        list: List of unwanted cryptocurrencies found
    """
    if not text:
        return []
        
    text_lower = text.lower()
    found = []
    
    # Check phrases first 
    for phrase in PHRASES:
        if phrase in text_lower:
            found.append(phrase)
    
    # Check single words with pre-compiled patterns
    for word, pattern in SINGLE_WORD_PATTERNS.items():
        if pattern.search(text):
            found.append(word)
            
    return found


def filter_bitcoin_only_articles(articles):
    """
    Filter articles to only include Bitcoin mining related content.
    Removes articles that mention other cryptocurrencies.
    
    Args:
        articles (list): List of article dictionaries
        
    Returns:
        tuple: (filtered_articles, excluded_count, excluded_details)
    """
    if not articles:
        return [], 0, []
    
    # Import here to avoid circular imports
    try:
        from utils import RuntimeLogger
        RuntimeLogger.initialize_runtime_logs()
    except ImportError:
        pass  # Runtime logging not available
    
    filtered_articles = []
    excluded_details = []
    
    for article in articles:
        title = article.get('title', '')
        body = article.get('body', '')
        url = article.get('url', '')
        
        # Check title and body for unwanted cryptocurrencies
        title_cryptos = get_unwanted_crypto_found(title)
        body_cryptos = get_unwanted_crypto_found(body)
        
        if title_cryptos or body_cryptos:
            # Article mentions non-Bitcoin cryptocurrencies - exclude it
            excluded_details.append({
                'title': title[:100] + '...' if len(title) > 100 else title,
                'url': url,
                'found_in_title': title_cryptos,
                'found_in_body': body_cryptos[:5]  # Limit to first 5 found in body
            })
            
            # Log blocked content
            try:
                from utils import RuntimeLogger
                reason = f"Contains non-Bitcoin cryptocurrencies: {', '.join(title_cryptos + body_cryptos[:3])}"
                RuntimeLogger.log_blocked_content("article", title, reason)
            except ImportError:
                pass  # Runtime logging not available
            
            logger.info(f"Filtering out non-Bitcoin article: {title[:50]}... (mentions: {', '.join(title_cryptos + body_cryptos[:3])})")
        else:
            # Article appears to be Bitcoin-only - include it
            filtered_articles.append(article)
    
    excluded_count = len(excluded_details)
    
    if excluded_count > 0:
        logger.info(f"Filtered out {excluded_count} non-Bitcoin mining articles from {len(articles)} total articles")
    
    return filtered_articles, excluded_count, excluded_details


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Bitcoin mining facility opens in Texas",  # Should pass
        "Ethereum mining gets harder with proof of stake", # Should fail
        "XRP mining drives unprecedented returns", # Should fail  
        "Dogecoin and Bitcoin mining comparison", # Should fail
        "Cloud mining supports Bitcoin, ETH, and Litecoin", # Should fail
        "BTC mining hashrate reaches new high", # Should pass
        "Best cryptocurrency mining apps of 2025", # Should pass (generic crypto but not specific altcoins)
        "Bitcoin mining energy consumption study", # Should pass
        "Multiple cryptocurrencies mining platform", # Should fail
        "Mine Bitcoin and several altcoins", # Should fail
    ]
    
    print("Testing cryptocurrency filter:")
    for test in test_cases:
        is_unwanted = contains_unwanted_crypto(test)
        found_cryptos = get_unwanted_crypto_found(test)
        status = "❌ FILTER OUT" if is_unwanted else "✅ ALLOW"
        print(f"{status}: {test}")
        if found_cryptos:
            print(f"    Found: {', '.join(found_cryptos)}")
        print()