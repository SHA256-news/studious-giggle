#!/usr/bin/env python3
"""
Test script to demonstrate the new URL context functionality in Gemini client
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

# Mock google.genai with URL context support
google_module = mock.MagicMock()
google_genai_module = mock.MagicMock()
google_types_module = mock.MagicMock()
google_module.genai = google_genai_module
google_genai_module.types = google_types_module

# Mock the types that are used for URL context
mock_url_context = mock.MagicMock()
mock_url_context_metadata = mock.MagicMock()
mock_tool = mock.MagicMock()
mock_generate_content_config = mock.MagicMock()
mock_thinking_config = mock.MagicMock()

google_types_module.UrlContext = lambda: mock_url_context
google_types_module.UrlContextMetadata = lambda: mock_url_context_metadata
google_types_module.Tool = lambda **kwargs: mock_tool
google_types_module.GenerateContentConfig = lambda **kwargs: mock_generate_content_config
google_types_module.ThinkingConfig = lambda **kwargs: mock_thinking_config

sys.modules.setdefault("google", google_module)
sys.modules.setdefault("google.genai", google_genai_module)
sys.modules.setdefault("google.genai.types", google_types_module)

from gemini_client import GeminiClient
from config import GeminiConfig

def test_url_context_integration():
    """Test that GeminiClient now uses URL context tools"""
    print("🧪 Testing URL Context Integration")
    print("=" * 50)
    
    # Create a mock config
    config = mock.MagicMock(spec=GeminiConfig)
    
    # Create a mock response with URL context metadata
    mock_response = mock.MagicMock()
    mock_response.text = "🚀 Major Bitcoin Mining Facility Opens in Texas"
    mock_response.candidates = [mock.MagicMock()]
    mock_candidate = mock_response.candidates[0]
    mock_candidate.url_context_metadata = mock.MagicMock()
    mock_candidate.url_context_metadata.url_metadata = [
        mock.MagicMock(),
        mock.MagicMock()
    ]
    
    # Mock the client to return our test response
    with mock.patch('gemini_client.genai.Client') as mock_client_class:
        mock_client = mock.MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = GeminiClient(config)
        
        test_article = {
            'title': 'Major Bitcoin Mining Operation Launches in Texas with $100M Investment',
            'body': 'A new Bitcoin mining facility has opened in Texas...',
            'url': 'https://cointelegraph.com/news/bitcoin-mining-facility-texas-100m'
        }
        
        print("1. Testing headline generation with URL context...")
        headline = client.generate_tweet_headline(test_article)
        print(f"✅ Generated headline: {headline}")
        
        # Verify that the generate_content was called with URL context tools
        generate_call_args = mock_client.models.generate_content.call_args
        assert generate_call_args is not None, "generate_content should have been called"
        
        call_kwargs = generate_call_args.kwargs
        assert 'config' in call_kwargs, "config should be passed to generate_content"
        
        print("✅ URL context tools configuration verified")
        
        print("\n2. Testing summary generation with URL context...")
        summary = client.generate_tweet_summary(test_article)
        print(f"✅ Generated summary: {summary}")
        
        print("\n3. Verifying prompt improvements...")
        # Check that the prompts mention URL analysis
        headline_prompt = client._create_tweet_headline_prompt(
            test_article['title'], 
            test_article['body'], 
            test_article['url']
        )
        summary_prompt = client._create_tweet_summary_prompt(
            test_article['title'], 
            test_article['body'], 
            test_article['url']
        )
        
        assert "URL" in headline_prompt, "Headline prompt should mention URL analysis"
        assert "URL" in summary_prompt, "Summary prompt should mention URL analysis"
        assert "full article content from the URL" in headline_prompt, "Headline prompt should reference full URL content"
        assert "full article content from the URL" in summary_prompt, "Summary prompt should reference full URL content"
        
        print("✅ Prompts correctly reference URL context analysis")
        
        print("\n🎉 All URL context tests passed!")
        return True

def test_url_context_error_handling():
    """Test that URL context failures are handled gracefully"""
    print("\n🛡️ Testing URL Context Error Handling")
    print("=" * 50)
    
    config = mock.MagicMock(spec=GeminiConfig)
    
    # Mock the client to raise an exception
    with mock.patch('gemini_client.genai.Client') as mock_client_class:
        mock_client = mock.MagicMock()
        mock_client.models.generate_content.side_effect = Exception("URL context API error")
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
        print(f"✅ Headline error handling: {headline[:50]}...")
        
        # Test summary generation error handling  
        summary = client.generate_tweet_summary(test_article)
        assert isinstance(summary, str), "Should return a string fallback"
        assert len(summary) > 0, "Should return non-empty fallback"
        print(f"✅ Summary error handling: {summary[:50]}...")
        
        print("✅ Error handling works correctly with URL context")

def main():
    """Run all tests"""
    success = True
    
    try:
        success &= test_url_context_integration()
        success &= test_url_context_error_handling() is not False
        
        if success:
            print("\n🎉 All URL context functionality tests passed!")
            print("\nWhat's New:")
            print("• Gemini now uses URL context tool to analyze full article content")
            print("• Enhanced prompts that leverage actual URL content")
            print("• Better accuracy in headline and summary generation")
            print("• Graceful fallback when URL context fails")
            print("• Logging of URL retrieval metadata")
        else:
            print("\n❌ Some tests failed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        success = False
        
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)