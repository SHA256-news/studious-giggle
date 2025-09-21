#!/usr/bin/env python3
"""
Fetch News and Tweet Script
---------------------------
This script fetches Bitcoin mining news from EventRegistry and posts tweets,
but skips Gemini analysis (which is handled by a separate workflow).
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import BitcoinMiningNewsBot, main as bot_main


def main():
    """Main entry point for fetch and tweet workflow"""
    # Check if this is a diagnostic run
    if "--diagnose" in sys.argv:
        return bot_main()
    
    try:
        # Initialize bot with Gemini analysis enabled
        bot = BitcoinMiningNewsBot(skip_gemini_analysis=False)
        
        # Run the bot
        return bot.run()
        
    except ValueError as e:
        # Handle missing API keys gracefully in GitHub Actions
        if "environment variables" in str(e).lower():
            print("="*80)
            print("🔍 FETCH AND TWEET: Missing API Keys Detected")
            print("="*80)
            print("")
            print("❌ ISSUE: Required API keys are not configured in GitHub repository secrets")
            print("✅ SOLUTION: This workflow step should fail until API keys are properly set up")
            print("")
            print("🔧 TO FIX THIS:")
            print("   1. Go to repository Settings > Secrets and variables > Actions")
            print("   2. Add these repository secrets:")
            for var in ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", 
                       "TWITTER_ACCESS_TOKEN_SECRET", "EVENTREGISTRY_API_KEY"]:
                print(f"      - {var}")
            print("")
            print("💡 EXPECTED BEHAVIOR:")
            print("   - This GitHub Action step should FAIL when API keys are missing")
            print("   - This prevents false 'Success' status when no tweets are posted")
            print("   - Once API keys are added, this step will succeed and post tweets")
            print("")
            print("📖 API Key Setup Guides:")
            print("   - Twitter API: https://developer.twitter.com/")
            print("   - EventRegistry API: https://newsapi.ai/dashboard")
            print("="*80)
            
            # Exit with error code to make GitHub Action fail
            return 1
        else:
            # Re-raise other ValueError types
            raise


if __name__ == "__main__":
    exit(main())