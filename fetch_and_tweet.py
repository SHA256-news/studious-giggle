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
    
    # Initialize bot with Gemini analysis disabled
    bot = BitcoinMiningNewsBot(skip_gemini_analysis=True)
    
    # Run the bot
    return bot.run()


if __name__ == "__main__":
    exit(main())