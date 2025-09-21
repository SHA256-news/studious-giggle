#!/usr/bin/env python3
"""
Test script for the new Gemini summary functionality
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

from gemini_client import GeminiClient
from config import GeminiConfig
from bot import BitcoinMiningNewsBot


def test_gemini_client_has_summary_method():
    """Test that GeminiClient has the new generate_tweet_summary method"""
    print("Testing that GeminiClient has generate_tweet_summary method...")
    
    # Create a mock config
    config = mock.MagicMock(spec=GeminiConfig)
    
    # Create GeminiClient instance
    client = GeminiClient(config)
    
    # Check that the method exists
    assert hasattr(client, 'generate_tweet_summary'), "GeminiClient should have generate_tweet_summary method"
    assert callable(getattr(client, 'generate_tweet_summary')), "generate_tweet_summary should be callable"
    
    print("✅ GeminiClient has generate_tweet_summary method")


def test_gemini_methods_handle_errors_gracefully():
    """Test that both Gemini methods handle errors gracefully"""
    print("Testing error handling in Gemini methods...")
    
    # Create a mock config
    config = mock.MagicMock(spec=GeminiConfig)
    
    # Mock the client to raise an exception
    with mock.patch('gemini_client.genai.Client') as mock_client_class:
        mock_client = mock.MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        client = GeminiClient(config)
        
        test_article = {
            'title': 'Test Bitcoin Mining Article',
            'body': 'Test content about Bitcoin mining',
            'url': 'https://example.com/test'
        }
        
        # Test headline generation error handling
        headline = client.generate_tweet_headline(test_article)
        assert isinstance(headline, str), "Should return a string fallback"
        assert len(headline) > 0, "Should return non-empty fallback"
        print(f"✅ Headline fallback: {headline[:50]}...")
        
        # Test summary generation error handling
        summary = client.generate_tweet_summary(test_article)
        assert isinstance(summary, str), "Should return a string fallback"
        assert len(summary) > 0, "Should return non-empty fallback"
        assert "•" in summary, "Summary fallback should contain bullet points"
        print(f"✅ Summary fallback: {summary}")


def test_bot_calls_both_methods_when_gemini_enabled():
    """Test that BitcoinMiningNewsBot calls both headline and summary methods when Gemini is enabled"""
    print("Testing that bot calls both Gemini methods...")
    
    # Mock the API manager and clients
    with mock.patch('bot.APIClientManager') as mock_api_manager_class:
        mock_api_manager = mock.MagicMock()
        mock_api_manager_class.return_value = mock_api_manager
        
        # Mock the Gemini client
        mock_gemini_client = mock.MagicMock()
        mock_gemini_client.generate_tweet_headline.return_value = "Test Headline"
        mock_gemini_client.generate_tweet_summary.return_value = "• Point 1 • Point 2 • Point 3"
        mock_api_manager.get_gemini_client.return_value = mock_gemini_client
        
        # Mock the tweet poster
        mock_tweet_poster = mock.MagicMock()
        mock_tweet_poster.post_to_twitter.return_value = "tweet_123"
        
        # Create bot with Gemini analysis enabled
        bot = BitcoinMiningNewsBot(safe_mode=False, skip_gemini_analysis=False)
        bot.tweet_poster = mock_tweet_poster
        
        test_article = {
            'title': 'Test Bitcoin Mining Article',
            'body': 'Test content about Bitcoin mining',
            'uri': 'test_uri_123'
        }
        
        # Call _post_article
        result = bot._post_article(test_article)
        
        # Verify both methods were called
        mock_gemini_client.generate_tweet_headline.assert_called_once_with(test_article)
        mock_gemini_client.generate_tweet_summary.assert_called_once_with(test_article)
        
        # Verify the enhanced article was passed to tweet poster
        assert mock_tweet_poster.post_to_twitter.called, "Should call post_to_twitter"
        posted_article = mock_tweet_poster.post_to_twitter.call_args[0][0]
        assert 'gemini_headline' in posted_article, "Should have gemini_headline in enhanced article"
        assert 'gemini_summary' in posted_article, "Should have gemini_summary in enhanced article"
        
        assert result == True, "Should return True for successful posting"
        print("✅ Bot calls both headline and summary generation methods")


def test_bot_skips_gemini_when_disabled():
    """Test that BitcoinMiningNewsBot skips Gemini when skip_gemini_analysis=True"""
    print("Testing that bot skips Gemini when disabled...")
    
    # Mock the API manager
    with mock.patch('bot.APIClientManager') as mock_api_manager_class:
        mock_api_manager = mock.MagicMock()
        mock_api_manager_class.return_value = mock_api_manager
        
        # Mock the Gemini client (should not be called)
        mock_gemini_client = mock.MagicMock()
        mock_api_manager.get_gemini_client.return_value = mock_gemini_client
        
        # Mock the tweet poster
        mock_tweet_poster = mock.MagicMock()
        mock_tweet_poster.post_to_twitter.return_value = "tweet_123"
        
        # Create bot with Gemini analysis disabled
        bot = BitcoinMiningNewsBot(safe_mode=False, skip_gemini_analysis=True)
        bot.tweet_poster = mock_tweet_poster
        
        test_article = {
            'title': 'Test Bitcoin Mining Article',
            'body': 'Test content about Bitcoin mining',
            'uri': 'test_uri_123'
        }
        
        # Call _post_article
        result = bot._post_article(test_article)
        
        # Verify Gemini methods were NOT called
        mock_gemini_client.generate_tweet_headline.assert_not_called()
        mock_gemini_client.generate_tweet_summary.assert_not_called()
        
        # Verify the original article was passed to tweet poster
        assert mock_tweet_poster.post_to_twitter.called, "Should call post_to_twitter"
        posted_article = mock_tweet_poster.post_to_twitter.call_args[0][0]
        assert 'gemini_headline' not in posted_article, "Should not have gemini_headline when disabled"
        assert 'gemini_summary' not in posted_article, "Should not have gemini_summary when disabled"
        
        assert result == True, "Should return True for successful posting"
        print("✅ Bot skips Gemini when disabled")


def test_fetch_and_tweet_enables_gemini():
    """Test that fetch_and_tweet.py now enables Gemini analysis"""
    print("Testing that fetch_and_tweet.py enables Gemini analysis...")
    
    # Read the fetch_and_tweet.py file to check for skip_gemini_analysis setting
    fetch_and_tweet_path = Path(__file__).parent / "fetch_and_tweet.py"
    content = fetch_and_tweet_path.read_text()
    
    # Check that skip_gemini_analysis=True is NOT present
    assert "skip_gemini_analysis=True" not in content, "fetch_and_tweet.py should not disable Gemini analysis"
    
    # Check that skip_gemini_analysis=False is present (or not set, which defaults to False)
    if "skip_gemini_analysis=" in content:
        assert "skip_gemini_analysis=False" in content, "If set, skip_gemini_analysis should be False"
    
    print("✅ fetch_and_tweet.py enables Gemini analysis")


def main():
    """Run all tests"""
    print("🧪 Testing Gemini Summary Functionality")
    print("=" * 50)
    
    try:
        test_gemini_client_has_summary_method()
        test_gemini_methods_handle_errors_gracefully()
        test_bot_calls_both_methods_when_gemini_enabled()
        test_bot_skips_gemini_when_disabled()
        test_fetch_and_tweet_enables_gemini()
        
        print("\n" + "=" * 50)
        print("✅ All Gemini summary functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)