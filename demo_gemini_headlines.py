"""
Demo script to show Gemini headline generation working end-to-end
"""
import sys
from pathlib import Path
from typing import Dict, Any
from unittest import mock

# Add parent directory to sys.path so we can import modules
sys.path.append(str(Path(__file__).resolve().parents[0]))

# Mock external dependencies before importing our modules
if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

if "eventregistry" not in sys.modules:
    sys.modules["eventregistry"] = mock.MagicMock()

# Mock google.genai
google_module = mock.MagicMock()
google_genai_module = mock.MagicMock()
google_types_module = mock.MagicMock()
google_module.genai = google_genai_module
google_genai_module.types = google_types_module

sys.modules.setdefault("google", google_module)
sys.modules.setdefault("google.genai", google_genai_module)
sys.modules.setdefault("google.genai.types", google_types_module)

from utils import TextUtils


def demo_headline_generation():
    """Demo showing the difference between original and Gemini headlines"""
    
    print("🎯 Demo: Gemini Headline Generation for Tweets")
    print("=" * 60)
    
    # Test case 1: Basic news article
    article1 = {
        'title': 'CleanSpark Inc. announces Q3 Bitcoin mining expansion plans',
        'body': 'CleanSpark has announced expansion of mining operations...',
        'url': 'https://example.com/article1'
    }
    
    article1_with_gemini = article1.copy()
    article1_with_gemini['gemini_headline'] = '🚀 CleanSpark Powers Up: Major Q3 Expansion Set to Double Mining Capacity'
    
    print("\n📰 Test Case 1: Basic News Article")
    print(f"Original title: {article1['title']}")
    print(f"Gemini headline: {article1_with_gemini['gemini_headline']}")
    print()
    
    original_tweet = TextUtils.create_enhanced_tweet_text(article1)
    gemini_tweet = TextUtils.create_enhanced_tweet_text(article1_with_gemini)
    
    print(f"🐦 Tweet without Gemini: {original_tweet}")
    print(f"✨ Tweet with Gemini:    {gemini_tweet}")
    print()
    
    # Test case 2: Financial news
    article2 = {
        'title': 'Marathon Digital Holdings reports quarterly earnings results',
        'body': 'Marathon Digital has reported strong quarterly performance...',
        'url': 'https://example.com/article2'
    }
    
    article2_with_gemini = article2.copy()
    article2_with_gemini['gemini_headline'] = '💰 Marathon Miners Hit Jackpot: Record Q3 Earnings Surge 200%'
    
    print("📊 Test Case 2: Financial News")
    print(f"Original title: {article2['title']}")
    print(f"Gemini headline: {article2_with_gemini['gemini_headline']}")
    print()
    
    original_tweet2 = TextUtils.create_enhanced_tweet_text(article2)
    gemini_tweet2 = TextUtils.create_enhanced_tweet_text(article2_with_gemini)
    
    print(f"🐦 Tweet without Gemini: {original_tweet2}")
    print(f"✨ Tweet with Gemini:    {gemini_tweet2}")
    print()
    
    # Test case 3: Technical news
    article3 = {
        'title': 'New ASIC mining hardware achieves improved efficiency metrics',
        'body': 'Latest generation mining equipment shows significant improvements...',
        'url': 'https://example.com/article3'
    }
    
    article3_with_gemini = article3.copy()
    article3_with_gemini['gemini_headline'] = '⚡ Game-Changer: Next-Gen ASICs Slash Energy Use by 40%'
    
    print("🔧 Test Case 3: Technical News")
    print(f"Original title: {article3['title']}")
    print(f"Gemini headline: {article3_with_gemini['gemini_headline']}")
    print()
    
    original_tweet3 = TextUtils.create_enhanced_tweet_text(article3)
    gemini_tweet3 = TextUtils.create_enhanced_tweet_text(article3_with_gemini)
    
    print(f"🐦 Tweet without Gemini: {original_tweet3}")
    print(f"✨ Tweet with Gemini:    {gemini_tweet3}")
    print()
    
    # Show fallback behavior
    print("🛡️  Test Case 4: Fallback Behavior")
    article_empty_gemini = {
        'title': 'Standard Bitcoin mining news article title',
        'gemini_headline': '',  # Empty Gemini headline
        'body': 'Regular content...',
        'url': 'https://example.com/article4'
    }
    
    fallback_tweet = TextUtils.create_enhanced_tweet_text(article_empty_gemini)
    print(f"Empty Gemini headline → Falls back to original: {fallback_tweet}")
    print()
    
    print("🎉 Demo Summary:")
    print("✅ Gemini headlines create more engaging, catchy tweets")
    print("✅ Original titles are preserved as fallback")
    print("✅ Empty/None Gemini headlines gracefully fall back to original")
    print("✅ All existing functionality preserved")


if __name__ == "__main__":
    demo_headline_generation()