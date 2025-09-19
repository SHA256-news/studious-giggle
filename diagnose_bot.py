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

def check_rate_limit_cooldown():
    """Check if there's an active rate limit cooldown"""
    logger.info("\n=== CHECKING RATE LIMIT STATUS ===")
    
    try:
        with open("rate_limit_cooldown.json", "r") as f:
            cooldown_data = json.load(f)
            
        cooldown_until = cooldown_data.get("cooldown_until")
        if cooldown_until:
            from datetime import datetime
            cooldown_time = datetime.fromisoformat(cooldown_until.replace('Z', '+00:00'))
            current_time = datetime.now(cooldown_time.tzinfo)
            
            if current_time < cooldown_time:
                time_remaining = cooldown_time - current_time
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                
                logger.warning(f"⏰ ACTIVE RATE LIMIT COOLDOWN until {cooldown_until}")
                logger.warning(f"   Time remaining: {hours}h {minutes}m")
                logger.info("   This is why no tweets were posted despite a 'successful' run")
                logger.info("   The bot correctly avoided violating Twitter's 17 requests/24h limit")
                return True
            else:
                logger.info("✅ Rate limit cooldown has expired")
                return False
        else:
            logger.info("✅ No active rate limit cooldown")
            return False
            
    except FileNotFoundError:
        logger.info("✅ No rate limit cooldown file found (no active cooldown)")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking rate limit cooldown: {str(e)}")
        return False

def check_posted_articles():
    """Check the posted articles file"""
    logger.info("\n=== CHECKING POSTED ARTICLES FILE ===")
    
    try:
        with open("posted_articles.json", "r") as f:
            data = json.load(f)
            posted_count = len(data.get("posted_uris", []))
            queued_count = len(data.get("queued_articles", []))
            logger.info(f"✅ Found {posted_count} previously posted articles and {queued_count} queued articles")
            
            if posted_count > 0:
                logger.info("Recent posted articles:")
                for uri in data["posted_uris"][-5:]:  # Show last 5
                    logger.info(f"  - {uri}")
                    
            if queued_count > 0:
                logger.info("Queued articles:")
                for article in data["queued_articles"][:5]:  # Show first 5
                    title = article.get("title", "Unknown")[:50]
                    logger.info(f"  - {title}...")
            
            return data
    except FileNotFoundError:
        logger.warning("⚠️  posted_articles.json not found - will be created on first run")
        return {"posted_uris": [], "queued_articles": []}
    except json.JSONDecodeError:
        logger.error("❌ posted_articles.json is corrupted")
        return None

def check_image_library():
    """Check image library status"""
    logger.info("\n=== CHECKING IMAGE LIBRARY STATUS ===")
    
    try:
        # Check if image functionality is available
        from image_library import ImageLibrary
        from image_selector import ImageSelector
        
        library = ImageLibrary()
        
        # Count available images
        bitcoin_images = library.get_bitcoin_images()
        
        available_entities = 0
        total_entities = 0
        entity_breakdown = {}
        
        for entity_type, entities in library.entity_mapping.items():
            entity_count = len(entities)
            total_entities += entity_count
            
            available_count = 0
            for entity_name, entity_config in entities.items():
                local_path = entity_config.get("local_path")
                if local_path and os.path.exists(local_path):
                    available_count += 1
            
            available_entities += available_count
            entity_breakdown[entity_type] = {"available": available_count, "total": entity_count}
        
        total_available = len(bitcoin_images) + available_entities
        total_configured = len(library.library_config.get("default_bitcoin_images", [])) + total_entities
        
        logger.info(f"📊 Image Library Summary:")
        logger.info(f"   🏆 Total available images: {total_available}/{total_configured}")
        logger.info(f"   🔸 Bitcoin images: {len(bitcoin_images)}/{len(library.library_config.get('default_bitcoin_images', []))}")
        logger.info(f"   🗺️  Entity images: {available_entities}/{total_entities}")
        
        for entity_type, counts in entity_breakdown.items():
            if counts["total"] > 0:
                logger.info(f"     - {entity_type}: {counts['available']}/{counts['total']}")
        
        # Check for recent maintenance
        if os.path.exists("image_maintenance_report.json"):
            try:
                with open("image_maintenance_report.json", 'r') as f:
                    report = json.load(f)
                    
                if report.get("broken_urls"):
                    logger.warning(f"   ⚠️  {len(report['broken_urls'])} broken URLs detected")
                    logger.warning("   Run 'python maintain_image_library.py' to update")
                else:
                    logger.info("   ✅ No broken URLs detected in last maintenance")
                    
            except Exception:
                pass
        else:
            logger.info("   ℹ️  No maintenance report found (run 'python maintain_image_library.py')")
        
        # Test image selection
        try:
            selector = ImageSelector()
            test_images = selector.select_images_for_headline("Bitcoin mining in Texas reaches new heights")
            if test_images:
                logger.info(f"   ✅ Image selection working - found {len(test_images)} images for test headline")
            else:
                logger.warning("   ⚠️  Image selection returned no images for test headline")
        except Exception as e:
            logger.warning(f"   ⚠️  Image selection test failed: {str(e)}")
        
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️  Image functionality not available: {str(e)}")
        logger.info("   Bot will work without images (text-only tweets)")
        return False
    except Exception as e:
        logger.error(f"❌ Image library check failed: {str(e)}")
        return False

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
    logger.info(f"   - Queued articles: {len(posted_articles.get('queued_articles', []))}")
    
    if len(new_articles) == 0:
        queued_count = len(posted_articles.get("queued_articles", []))
        if queued_count > 0:
            logger.info("🔍 ROOT CAUSE: No new articles found, but bot should post from queue")
            logger.info(f"   - {queued_count} articles are available in the queue")
            logger.info("   - Bot should automatically post from queue when no new articles are found")
        else:
            logger.warning("🔍 ROOT CAUSE: All fetched articles were already posted and no queued articles")
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
    
    # Check rate limit cooldown first (most common cause of "successful but no tweets")
    rate_limited = check_rate_limit_cooldown()
    
    # Check posted articles
    posted_articles = check_posted_articles()
    
    # Check image library status
    image_library_ok = check_image_library()
    
    # Determine root cause and provide appropriate messaging
    if rate_limited:
        logger.error("🔍 ROOT CAUSE: Active rate limit cooldown prevents posting")
        logger.info("   The bot is working correctly by respecting Twitter's API limits")
        logger.info("   Tweets will resume automatically when the cooldown expires")
        if posted_articles and posted_articles.get("queued_articles"):
            queued_count = len(posted_articles["queued_articles"])
            logger.info(f"   {queued_count} articles are queued and will be posted after cooldown")
    elif not env_ok:
        logger.error("🔍 ROOT CAUSE: Missing environment variables prevent bot operation")
    else:
        # Only proceed with API tests if environment is set up and no active rate limit
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
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ Diagnostics complete!")
    
    # Provide solutions based on the root cause
    if rate_limited:
        logger.info("\n💡 EXPLANATION: Why no tweets were posted:")
        logger.info("   - The GitHub Action ran successfully (no errors)")
        logger.info("   - The bot found articles and tried to post them")
        logger.info("   - Twitter's rate limit was reached (17 requests per 24 hours)")
        logger.info("   - The bot entered cooldown to avoid violating Twitter's terms")
        logger.info("   - This is normal and expected behavior for rate limiting")
        logger.info("   - The bot will automatically resume posting when cooldown expires")
        if not env_ok:
            logger.info("\n⚠️  NOTE: API keys are also missing in this local environment")
            logger.info("   However, they are configured in GitHub Actions (hence the successful runs)")
    elif not env_ok:
        logger.info("\n💡 SOLUTION: Set up the required environment variables:")
        logger.info("   - TWITTER_API_KEY")
        logger.info("   - TWITTER_API_SECRET")
        logger.info("   - TWITTER_ACCESS_TOKEN")
        logger.info("   - TWITTER_ACCESS_TOKEN_SECRET")
        logger.info("   - EVENTREGISTRY_API_KEY")

if __name__ == "__main__":
    main()