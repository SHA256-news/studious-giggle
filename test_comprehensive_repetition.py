#!/usr/bin/env python3
"""
Comprehensive test script to validate the repetition fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_various_repetition_scenarios():
    """Test the fix with various scenarios"""
    print("Testing various repetition scenarios...")
    
    test_cases = [
        {
            "name": "CleanSpark Credit Line (Original Issue)",
            "article": {
                "title": "CleanSpark Secures $100M Credit Line from Coinbase Prime",
                "body": "CleanSpark has secured an additional $100 million credit line from Coinbase Prime, backed by its Bitcoin holdings. The credit is non-dilutive and the stock has increased by 33%.",
                "url": "https://example.com/cleanspark-news",
                "gemini_headline": "CleanSpark secured an additional $100 million credit line from Coinbase Prime, backed by its Bitcoin holdings",
                "gemini_summary": "Key highlights:\n• $100M Coinbase credit\n• BTC-backed non-dilutive\n• Stock up 33%"
            }
        },
        {
            "name": "Marathon Mining Expansion",
            "article": {
                "title": "Marathon Digital Expands Mining Operations with $50M Investment",
                "body": "Marathon Digital announced a $50 million investment in new mining facilities in Texas, expecting to add 500 miners by Q2.",
                "url": "https://example.com/marathon-news",
                "gemini_headline": "Marathon Digital announces $50M investment in Texas mining expansion",
                "gemini_summary": "Key highlights:\n• $50M facility investment\n• 500 new miners\n• Texas location\n• Q2 deployment target"
            }
        },
        {
            "name": "No Repetition Case",
            "article": {
                "title": "Bitcoin Mining Regulations Updated in EU",
                "body": "European Union updates regulations for Bitcoin mining operations with new energy efficiency requirements.",
                "url": "https://example.com/eu-regulations",
                "gemini_headline": "EU updates Bitcoin mining regulations with energy efficiency focus",
                "gemini_summary": "Key highlights:\n• New energy requirements\n• Compliance by Q3 2024\n• Affects all mining operations\n• Environmental impact focus"
            }
        },
        {
            "name": "Minimal Overlap Case",
            "article": {
                "title": "Riot Platforms Increases Hashrate to 12 EH/s",
                "body": "Riot Platforms achieved 12 EH/s hashrate milestone with new deployment of 1,000 miners.",
                "url": "https://example.com/riot-hashrate",
                "gemini_headline": "Riot Platforms reaches 12 EH/s hashrate milestone",
                "gemini_summary": "Key highlights:\n• 12 EH/s achievement\n• 1,000 new miners deployed\n• Production capacity increased\n• Q1 target exceeded"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        article = test_case["article"]
        
        # Create three-part thread
        hook_tweet, summary_tweet, url_tweet = TextUtils.create_three_part_thread(article)
        
        print(f"Tweet 1 (Hook): {hook_tweet}")
        print(f"Tweet 2 (Summary): {summary_tweet}")
        print(f"Tweet 3 (URL): {url_tweet}")
        
        # Check for repetition
        if summary_tweet:
            hook_lower = hook_tweet.lower()
            summary_lower = summary_tweet.lower()
            
            # Check for overlapping key terms
            repetitions = []
            
            # Check financial amounts
            import re
            hook_amounts = re.findall(r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|m|b))?', hook_lower)
            summary_amounts = re.findall(r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|m|b))?', summary_lower)
            
            for amount in hook_amounts:
                normalized_hook = amount.replace('$', '').replace(',', '').replace(' ', '')
                for s_amount in summary_amounts:
                    normalized_summary = s_amount.replace('$', '').replace(',', '').replace(' ', '')
                    if normalized_hook == normalized_summary:
                        repetitions.append(f"Amount: {amount}")
            
            # Check company names
            companies = ["cleanspark", "marathon", "riot", "coinbase", "microstrategy"]
            for company in companies:
                if company in hook_lower and company in summary_lower:
                    repetitions.append(f"Company: {company}")
            
            # Check technical specs
            hook_specs = re.findall(r'[\d,]+\s*(?:eh/s|th/s|mw|gw|miners?|rigs?)', hook_lower)
            summary_specs = re.findall(r'[\d,]+\s*(?:eh/s|th/s|mw|gw|miners?|rigs?)', summary_lower)
            
            for spec in hook_specs:
                if spec in summary_specs:
                    repetitions.append(f"Spec: {spec}")
            
            if repetitions:
                print(f"❌ REPETITION DETECTED: {', '.join(repetitions)}")
            else:
                print("✅ No repetition detected")
        else:
            print("ℹ️  No summary tweet generated (empty)")
        
        # Check for generic headlines
        if hook_tweet.lower().startswith(("the article", "new bitcoin", "bitcoin mining news")):
            print("❌ GENERIC HEADLINE: Hook tweet uses generic opening")
        else:
            print("✅ Hook tweet has specific, catchy headline")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print("✅ All test cases should show no repetition")
    print("✅ Hook tweets should be specific and catchy")
    print("✅ Summary tweets should complement, not repeat hook content")

if __name__ == "__main__":
    test_various_repetition_scenarios()