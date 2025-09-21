"""
Test Gemini headline integration for tweet creation
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from unittest import mock

# Add parent directory to sys.path so we can import modules
sys.path.append(str(Path(__file__).resolve().parents[0]))

# Mock external dependencies before importing our modules
if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

if "eventregistry" not in sys.modules:
    sys.modules["eventregistry"] = mock.MagicMock()

# Mock google.genai before importing
google_module = mock.MagicMock()
google_genai_module = mock.MagicMock()
google_types_module = mock.MagicMock()
google_module.genai = google_genai_module
google_genai_module.types = google_types_module

sys.modules.setdefault("google", google_module)
sys.modules.setdefault("google.genai", google_genai_module)
sys.modules.setdefault("google.genai.types", google_types_module)

from utils import TextUtils

def test_gemini_headline_preferred_over_original_title():
    """Test that Gemini headline is used instead of original title in tweet creation"""
    article = {
        "title": "Original boring news title about Bitcoin mining",
        "gemini_headline": "🚀 Major Bitcoin Mining Revolution Unfolds",
        "body": "Some article body content here",
        "url": "https://example.com/article"
    }
    
    tweet_text = TextUtils.create_enhanced_tweet_text(article)
    print(f"Debug - tweet_text: '{tweet_text}'")
    
    # Should contain elements from Gemini headline (allowing for abbreviations)
    assert "🚀 Major" in tweet_text
    assert "Revolution Unfolds" in tweet_text
    assert "Original boring news title" not in tweet_text
    print(f"✅ Gemini headline used: {tweet_text}")


def test_fallback_to_original_title_when_no_gemini_headline():
    """Test that original title is used when no Gemini headline is available"""
    article = {
        "title": "Original Bitcoin mining news title",
        "body": "Some article body content here",
        "url": "https://example.com/article"
    }
    
    tweet_text = TextUtils.create_enhanced_tweet_text(article)
    print(f"Debug - fallback tweet_text: '{tweet_text}'")
    
    # Should contain elements from original title (allowing for processing)
    assert "Original" in tweet_text
    assert "BTC mining" in tweet_text or "Bitcoin mining" in tweet_text
    print(f"✅ Original title used as fallback: {tweet_text}")


def test_original_tweet_text_uses_gemini_headline():
    """Test that the original tweet text method also uses Gemini headline"""
    article = {
        "title": "Original news title",
        "gemini_headline": "Enhanced Gemini headline about Bitcoin",
        "body": "Some content",
        "url": "https://example.com/article"
    }
    
    tweet_text = TextUtils.create_original_tweet_text(article)
    print(f"Debug - original method tweet_text: '{tweet_text}'")
    
    # Should contain Gemini headline elements
    assert "Enhanced Gemini headline" in tweet_text
    assert "Original news title" not in tweet_text
    print(f"✅ Original method uses Gemini headline: {tweet_text}")


def test_empty_gemini_headline_falls_back_to_title():
    """Test that empty Gemini headline falls back to original title"""
    article = {
        "title": "Original Bitcoin mining title",
        "gemini_headline": "",  # Empty Gemini headline
        "body": "Some content"
    }
    
    tweet_text = TextUtils.create_enhanced_tweet_text(article)
    print(f"Debug - empty gemini tweet_text: '{tweet_text}'")
    
    # Should use original title since Gemini headline is empty
    assert "Original" in tweet_text
    assert "BTC mining" in tweet_text or "Bitcoin mining" in tweet_text
    print(f"✅ Empty Gemini headline falls back to original: {tweet_text}")


def test_none_gemini_headline_falls_back_to_title():
    """Test that None Gemini headline falls back to original title"""
    article = {
        "title": "Original Bitcoin mining title",
        "gemini_headline": None,  # None Gemini headline
        "body": "Some content"
    }
    
    tweet_text = TextUtils.create_enhanced_tweet_text(article)
    print(f"Debug - none gemini tweet_text: '{tweet_text}'")
    
    # Should use original title since Gemini headline is None
    assert "Original" in tweet_text
    assert "BTC mining" in tweet_text or "Bitcoin mining" in tweet_text
    print(f"✅ None Gemini headline falls back to original: {tweet_text}")


if __name__ == "__main__":
    print("Testing Gemini headline integration in tweet creation...")
    
    test_gemini_headline_preferred_over_original_title()
    test_fallback_to_original_title_when_no_gemini_headline()
    test_original_tweet_text_uses_gemini_headline()
    test_empty_gemini_headline_falls_back_to_title()
    test_none_gemini_headline_falls_back_to_title()
    
    print("\n🎉 All Gemini headline integration tests passed!")