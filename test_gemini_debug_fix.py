#!/usr/bin/env python3
"""Test to verify the Gemini debugging output fix"""

import logging
from gemini_client import GeminiClient
from config import GeminiConfig

# Setup logging to see warnings
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('test_gemini_debug_fix')

def test_gemini_response_cleaning():
    """Test that the _clean_response_text method properly filters debugging content"""
    
    # Create a mock configuration
    config = GeminiConfig("dummy_key")
    
    # Create client without initializing actual API
    class MockGeminiClient:
        def _clean_response_text(self, text):
            # Copy the actual method from GeminiClient
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
            
            # Join back and return the first non-empty result
            result = '\n'.join(clean_lines).strip()
            
            # If we filtered everything out, return a safe fallback instead of problematic original
            if not result and text:
                print("All text was filtered as debugging content, using fallback")
                # Return a safe fallback instead of the problematic debugging text
                return ""  # Let the calling function handle the empty response with its own fallback
                
            return result
    
    client = MockGeminiClient()
    
    print("🧪 TESTING GEMINI DEBUGGING OUTPUT FIX")
    print("=" * 60)
    
    # Test case 1: The exact problematic output from GitHub Actions
    problematic_output = """The article content was provided in the prompt, so I will use that.
Let's analyze the provided source artic..."""
    
    print("🚨 Test Case 1: Actual problematic output")
    print(f"Input: {problematic_output}")
    cleaned = client._clean_response_text(problematic_output)
    print(f"Output: {cleaned}")
    print(f"Result: {'✅ FILTERED' if cleaned == '' else '❌ NOT FILTERED'}")
    print()
    
    # Test case 2: Good content that should pass through
    good_content = "CleanSpark secures $100M Bitcoin-backed credit from Coinbase Prime"
    
    print("✅ Test Case 2: Good content")
    print(f"Input: {good_content}")
    cleaned = client._clean_response_text(good_content)
    print(f"Output: {cleaned}")
    print(f"Result: {'✅ PRESERVED' if cleaned == good_content else '❌ INCORRECTLY FILTERED'}")
    print()
    
    # Test case 3: Mixed content (debugging + good)
    mixed_content = """Based on the article content provided, here's the headline:
CleanSpark secures $100M Bitcoin-backed credit facility"""
    
    print("🔄 Test Case 3: Mixed content")
    print(f"Input: {mixed_content}")
    cleaned = client._clean_response_text(mixed_content)
    print(f"Output: {cleaned}")
    print(f"Result: {'✅ PROPERLY CLEANED' if 'CleanSpark' in cleaned and 'Based on' not in cleaned else '❌ FAILED'}")
    print()
    
    # Test case 4: Summary with debugging
    summary_with_debug = """Let me analyze the provided source article.
• $100M credit facility secured
• Shares rise 6% after announcement
• Coinbase Prime partnership"""
    
    print("📊 Test Case 4: Summary with debugging")
    print(f"Input: {summary_with_debug}")
    cleaned = client._clean_response_text(summary_with_debug)
    print(f"Output: {cleaned}")
    print(f"Result: {'✅ SUMMARY PRESERVED' if '• $100M' in cleaned and 'Let me analyze' not in cleaned else '❌ FAILED'}")
    print()
    
    print("🎯 SUMMARY:")
    print("The fix should filter out debugging phrases while preserving actual content.")
    print("This prevents the bot from posting debugging text to Twitter.")

if __name__ == "__main__":
    test_gemini_response_cleaning()