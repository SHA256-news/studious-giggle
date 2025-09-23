#!/usr/bin/env python3
"""
Test script to verify generic headline prevention
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import TextUtils

def test_clean_gemini_response():
    """Test the Gemini response cleaning directly"""
    print("Testing Gemini response cleaning...")
    
    # Mock a Gemini client's cleaning function
    class MockGeminiClient:
        def _clean_response_text(self, text: str) -> str:
            """Clean up Gemini response text to remove any debugging content and generic openings."""
            if not text:
                return text
                
            # Remove common debugging phrases that Gemini might output
            debugging_phrases = [
                "The article content was provided in the prompt, so",
                "Let's analyze the provided source",
                "I will use that",
                "Based on the article content",
                "Looking at the source article",
                "From the provided information",
                "Analyzing the article",
                "Here's the",
                "Here are the",
                "Based on the URL content",
                "Let me analyze"
            ]
            
            # Generic opening phrases to remove or replace
            generic_openings = [
                "The article states that ",
                "The article mentions that ",
                "According to the article, ",
                "The report states that ",
                "The news states that ",
                "It is reported that ",
                "The article discusses how ",
                "The piece explains that "
            ]
            
            # Remove lines that start with debugging phrases
            lines = text.split('\n')
            clean_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Skip lines that contain debugging phrases
                is_debugging = False
                for phrase in debugging_phrases:
                    if phrase.lower() in line.lower():
                        is_debugging = True
                        print(f"Filtering out debugging text: {line[:50]}...")
                        break
                        
                if not is_debugging:
                    clean_lines.append(line)
            
            # Join back and get the result
            result = '\n'.join(clean_lines).strip()
            
            # Remove generic openings from the final result
            for opening in generic_openings:
                if result.lower().startswith(opening.lower()):
                    result = result[len(opening):].strip()
                    # Capitalize the first letter after removing the opening
                    if result:
                        result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()
                    print(f"Removed generic opening: '{opening}'")
                    break
            
            return result
    
    test_cases = [
        {
            "name": "Generic 'The article states that' opening",
            "gemini_response": "The article states that CleanSpark secured $100M credit line",
            "expected": "CleanSpark secured $100M credit line"
        },
        {
            "name": "Generic 'According to the article' opening", 
            "gemini_response": "According to the article, Marathon Digital expands mining operations",
            "expected": "Marathon Digital expands mining operations"
        },
        {
            "name": "Generic 'It is reported that' opening",
            "gemini_response": "It is reported that Bitcoin mining regulations updated in EU",
            "expected": "Bitcoin mining regulations updated in EU"
        },
        {
            "name": "Good headline (no changes needed)",
            "gemini_response": "Riot Platforms reaches 12 EH/s hashrate milestone",
            "expected": "Riot Platforms reaches 12 EH/s hashrate milestone"
        }
    ]
    
    client = MockGeminiClient()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Input: {test_case['gemini_response']}")
        
        cleaned = client._clean_response_text(test_case['gemini_response'])
        
        print(f"Output: {cleaned}")
        print(f"Expected: {test_case['expected']}")
        
        if cleaned.strip() == test_case['expected'].strip():
            print("✅ PASSED: Generic opening properly handled")
        else:
            print("❌ FAILED: Generic opening not properly handled")

def test_generic_headline_prevention():
    """Test that generic openings are properly handled"""
    print("Testing generic headline prevention...")
    
    test_clean_gemini_response()
    
    # Test fallback tweet prefixes
    print(f"\n--- Testing Fallback Tweet Prefixes ---")
    from config import BotConstants
    
    print(f"Current prefixes: {BotConstants.TWEET_PREFIXES}")
    
    # Verify prefixes are emoji-based
    has_emoji = all(any(ord(char) > 127 for char in prefix) for prefix in BotConstants.TWEET_PREFIXES)
    if has_emoji:
        print("✅ PASSED: All prefixes use emojis instead of generic text")
    else:
        print("❌ FAILED: Some prefixes still use generic text")
    
    # Test with article that would trigger fallback
    print(f"\n--- Testing Article with Fallback ---")
    article = {
        "title": "Simple Bitcoin News",
        "body": "Basic news content",
        "url": "https://example.com/news"
        # No gemini_headline - should trigger enhanced text creation
    }
    
    hook_tweet = TextUtils.create_hook_tweet(article)
    print(f"Hook tweet: {hook_tweet}")
    
    # Check if it starts with generic phrases
    generic_starts = ["news:", "update:", "breaking:", "the article", "bitcoin mining news update"]
    has_generic_start = any(hook_tweet.lower().startswith(generic) for generic in generic_starts)
    
    if not has_generic_start:
        print("✅ PASSED: Hook tweet doesn't start with generic phrases")
    else:
        print("❌ FAILED: Hook tweet starts with generic phrase")

if __name__ == "__main__":
    test_generic_headline_prevention()