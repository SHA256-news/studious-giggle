#!/usr/bin/env python3
"""
Fetch News and Tweet Script
---------------------------
This script fetches Bitcoin mining news from EventRegistry and posts tweets,
but skips Gemini analysis (which is handled by a separate workflow).
"""

import sys
import os
import logging

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('fetch_and_tweet')

from bot import BitcoinMiningNewsBot, main as bot_main


def main():
    """Main entry point for fetch and tweet workflow"""
    # Check if this is a diagnostic run
    if "--diagnose" in sys.argv:
        return bot_main()
    
    try:
        # Initialize bot with Gemini analysis disabled for this workflow
        bot = BitcoinMiningNewsBot(skip_gemini_analysis=True)
        
        # Run the bot
        return bot.run()
        
    except ValueError as e:
        # Handle missing API keys gracefully in GitHub Actions
        if "environment variables" in str(e).lower():
            logger.error("="*80)
            logger.error("🔍 FETCH AND TWEET: Missing API Keys Detected")
            logger.error("="*80)
            logger.error("")
            logger.error("❌ ISSUE: Required API keys are not configured in GitHub repository secrets")
            logger.error("✅ SOLUTION: This workflow step should fail until API keys are properly set up")
            logger.error("")
            logger.error("🔧 TO FIX THIS:")
            logger.error("   1. Go to repository Settings > Secrets and variables > Actions")
            logger.error("   2. Add these repository secrets:")
            for var in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", 
                       "TWITTER_ACCESS_TOKEN_SECRET", "EVENTREGISTRY_API_KEY"]:
                logger.error(f"      - {var}")
            logger.error("")
            logger.error("💡 EXPECTED BEHAVIOR:")
            logger.error("   - This GitHub Action step should FAIL when API keys are missing")
            logger.error("   - This prevents false 'Success' status when no tweets are posted")
            logger.error("   - Once API keys are added, this step will succeed and post tweets")
            logger.error("")
            logger.error("📖 API Key Setup Guides:")
            logger.error("   - Twitter API: https://developer.twitter.com/")
            logger.error("   - EventRegistry API: https://newsapi.ai/dashboard")
            logger.error("="*80)
            
            # Exit with error code to make GitHub Action fail
            return 1
        else:
            # Re-raise other ValueError types
            raise


if __name__ == "__main__":
    exit(main())