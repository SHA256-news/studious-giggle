#!/usr/bin/env python3
"""
Diagnostic script for Bitcoin Mining News Bot
Helps identify why no tweets were posted
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('bot_diagnostics')

def check_environment_variables():
    """Check if all required environment variables are set"""
    logger.info("=== CHECKING ENVIRONMENT VARIABLES ===")
    
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET', 
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'EVENTREGISTRY_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if not value:
            missing_vars.append(var)
            logger.error(f"❌ {var}: NOT SET")
        else:
            # Show first/last few characters for security
            masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            logger.info(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    else:
        logger.info("All required environment variables are set")
        return True

def check_posted_articles():
    """Check the posted articles file"""
    logger.info("\n=== CHECKING POSTED ARTICLES FILE ===")
    
    try:
        with open("posted_articles.json", "r") as f:
            data = json.load(f)
            posted_count = len(data.get("posted_uris", []))
            logger.info(f"✅ Found {posted_count} previously posted articles")
            
            if posted_count > 0:
                logger.info("Recent posted articles:")
                for uri in data["posted_uris"][-5:]:  # Show last 5
                    logger.info(f"  - {uri}")
            
            return data
    except FileNotFoundError:
        logger.warning("⚠️  posted_articles.json not found - will be created on first run")
        return {"posted_uris": []}
    except json.JSONDecodeError:
        logger.error("❌ posted_articles.json is corrupted")
        return None

def test_twitter_connection():
    """Test Twitter API connection"""
    logger.info("\n=== TESTING TWITTER CONNECTION ===")
    
    try:
        import tweepy
        
        client = tweepy.Client(
            consumer_key=os.environ.get("TWITTER_API_KEY"),
            consumer_secret=os.environ.get("TWITTER_API_SECRET"),
            access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Try to get user info
        me = client.get_me()
        if me.data:
            logger.info(f"✅ Twitter connection successful - authenticated as: {me.data.username}")
            return True
        else:
            logger.error("❌ Twitter authentication failed - no user data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Twitter connection failed: {str(e)}")
        return False

def test_eventregistry_connection():
    """Test EventRegistry API connection"""
    logger.info("\n=== TESTING EVENTREGISTRY CONNECTION ===")
    
    try:
        from eventregistry import EventRegistry
        
        api_key = os.environ.get("EVENTREGISTRY_API_KEY")
        if not api_key:
            logger.error("❌ EVENTREGISTRY_API_KEY not set")
            return False
            
        er = EventRegistry(apiKey=api_key)
        
        # Try to get a simple concept
        try:
            bitcoin_uri = er.getConceptUri("Bitcoin")
            if bitcoin_uri:
                logger.info(f"✅ EventRegistry connection successful - Bitcoin concept URI: {bitcoin_uri}")
                return True
            else:
                logger.error("❌ EventRegistry connection failed - could not get Bitcoin concept")
                return False
        except Exception as e:
            logger.error(f"❌ EventRegistry API call failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ EventRegistry connection failed: {str(e)}")
        return False

def test_article_fetching():
    """Test fetching articles"""
    logger.info("\n=== TESTING ARTICLE FETCHING ===")
    
    try:
        from bot import BitcoinMiningNewsBot
        bot = BitcoinMiningNewsBot()
        
        logger.info("Attempting to fetch articles...")
        articles = bot.fetch_bitcoin_mining_articles(max_articles=5)
        
        if articles:
            logger.info(f"✅ Successfully fetched {len(articles)} articles")
            logger.info("Sample articles:")
            for i, article in enumerate(articles[:3]):
                title = article.get('title', 'No title')
                uri = article.get('uri', 'No URI')
                url = article.get('url', 'No URL')
                logger.info(f"  {i+1}. {title[:50]}... (URI: {uri}, URL: {url})")
            return articles
        else:
            logger.error("❌ No articles fetched")
            return []
            
    except Exception as e:
        logger.error(f"❌ Article fetching failed: {str(e)}")
        return []

def analyze_why_no_posts(articles, posted_articles):
    """Analyze why no posts were made"""
    logger.info("\n=== ANALYZING WHY NO TWEETS POSTED ===")
    
    if not articles:
        logger.error("🔍 ROOT CAUSE: No articles were fetched from EventRegistry")
        logger.info("   - Check EventRegistry API key")
        logger.info("   - Check internet connectivity")
        logger.info("   - Check if EventRegistry service is operational")
        return
    
    posted_uris = posted_articles.get("posted_uris", [])
    new_articles = []
    already_posted = []
    
    for article in articles:
        uri = article.get("uri")
        if not uri:
            logger.warning(f"   - Article with no URI: {article.get('title', 'Unknown')[:30]}...")
            continue
            
        if uri in posted_uris:
            already_posted.append(article)
        else:
            new_articles.append(article)
    
    logger.info(f"📊 Article Analysis:")
    logger.info(f"   - Total articles fetched: {len(articles)}")
    logger.info(f"   - New articles available: {len(new_articles)}")
    logger.info(f"   - Already posted articles: {len(already_posted)}")
    
    if len(new_articles) == 0:
        logger.warning("🔍 ROOT CAUSE: All fetched articles were already posted")
        logger.info("   - This is normal if the bot runs frequently")
        logger.info("   - Check if articles are from the last 24 hours")
        
        # Show some recently posted articles
        if already_posted:
            logger.info("   Recently posted articles:")
            for article in already_posted[:3]:
                logger.info(f"     - {article.get('title', 'Unknown')[:50]}...")
    else:
        logger.warning("🔍 ROOT CAUSE: New articles available but posting failed")
        logger.info("   - Check Twitter API credentials")
        logger.info("   - Check for rate limiting")
        logger.info("   - Check bot posting logic")
        
        logger.info("   New articles that should have been posted:")
        for article in new_articles[:3]:
            logger.info(f"     - {article.get('title', 'Unknown')[:50]}...")

def main():
    """Run comprehensive diagnostics"""
    logger.info("🔍 Bitcoin Mining News Bot Diagnostics")
    logger.info("=" * 50)
    
    # Check environment
    env_ok = check_environment_variables()
    
    # Check posted articles
    posted_articles = check_posted_articles()
    
    # Only proceed with API tests if environment is set up
    if env_ok:
        # Test connections
        twitter_ok = test_twitter_connection()
        eventregistry_ok = test_eventregistry_connection()
        
        if twitter_ok and eventregistry_ok:
            # Test article fetching
            articles = test_article_fetching()
            
            # Analyze why no posts
            if posted_articles:
                analyze_why_no_posts(articles, posted_articles)
        else:
            logger.error("🔍 ROOT CAUSE: API connection failures prevent posting")
    else:
        logger.error("🔍 ROOT CAUSE: Missing environment variables prevent bot operation")
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ Diagnostics complete!")
    
    if not env_ok:
        logger.info("\n💡 SOLUTION: Set up the required environment variables:")
        logger.info("   - TWITTER_API_KEY")
        logger.info("   - TWITTER_API_SECRET")
        logger.info("   - TWITTER_ACCESS_TOKEN")
        logger.info("   - TWITTER_ACCESS_TOKEN_SECRET")
        logger.info("   - EVENTREGISTRY_API_KEY")

if __name__ == "__main__":
    main()