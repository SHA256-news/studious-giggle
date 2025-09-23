#!/usr/bin/env python3
"""Test to reproduce the specific Gemini output issue"""

import os
import logging
from gemini_client import GeminiClient
from config import GeminiConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_gemini')

def test_actual_gemini_output():
    """Test the actual Gemini output to see what's happening"""
    
    # Create a mock configuration - Gemini won't work without API key but we can test the prompt structure
    config = GeminiConfig("dummy_key")
    
    # Simulate the CleanSpark article that was problematic
    article = {
        "title": "CleanSpark (CLSK) Shares Rise After Getting $100M Bitcoin-Backed Credit Facility",
        "body": "CleanSpark Inc. (NASDAQ: CLSK) shares jumped over 5% in after-hours trading on Monday after the Bitcoin mining company announced securing a $100 million Bitcoin-backed credit facility from Coinbase Prime.",
        "url": "https://www.benzinga.com/markets/cryptocurrency/24/09/40827937/cleanspark-clsk-shares-rise-after-getting-100m-bitcoin-backed-credit-facility"
    }
    
    print("🔍 TESTING GEMINI OUTPUT ISSUE")
    print("=" * 60)
    print(f"Article: {article['title']}")
    print()
    
    # Test if we have a Gemini API key
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("❌ No GEMINI_API_KEY found - testing prompt structure only")
        
        # Test prompt creation
        client = GeminiClient(config)
        headline_prompt = client._create_tweet_headline_prompt(article['title'], article['body'], article['url'])
        summary_prompt = client._create_tweet_summary_prompt(article['title'], article['body'], article['url'])
        
        print("📝 HEADLINE PROMPT:")
        print("-" * 40)
        print(headline_prompt)
        print()
        
        print("📝 SUMMARY PROMPT:")
        print("-" * 40)
        print(summary_prompt)
        print()
        
        print("🚨 ISSUE ANALYSIS:")
        print("The prompts look correct, but the issue is likely in the thinking_config")
        print("and URL context that's causing Gemini to return debugging output.")
        print()
        print("In the logs we saw:")
        print("'The article content was provided in the prompt, so I will use that.'")
        print("'Let's analyze the provided source artic...'")
        print()
        print("This suggests Gemini is in 'thinking' mode instead of output mode.")
        
    else:
        print("✅ GEMINI_API_KEY found - testing actual API calls")
        
        try:
            client = GeminiClient(config)
            
            print("🔄 Testing headline generation...")
            headline = client.generate_tweet_headline(article)
            print(f"Headline: {headline}")
            print(f"Length: {len(headline)}")
            print()
            
            print("🔄 Testing summary generation...")
            summary = client.generate_tweet_summary(article)
            print(f"Summary: {summary}")
            print(f"Length: {len(summary)}")
            print()
            
        except Exception as e:
            print(f"❌ Error testing Gemini: {e}")

if __name__ == "__main__":
    test_actual_gemini_output()