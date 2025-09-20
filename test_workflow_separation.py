#!/usr/bin/env python3
"""
Test the new separate workflow functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_fetch_and_tweet_skips_gemini():
    """Test that fetch_and_tweet skips Gemini analysis"""
    print("Testing fetch_and_tweet without Gemini analysis...")
    
    from bot import BitcoinMiningNewsBot
    from unittest.mock import patch, MagicMock
    
    # Mock the API clients
    with patch('bot.APIClientManager') as mock_api_manager, \
         patch('bot.TweetPoster') as mock_tweet_poster:
        
        # Set up mocks
        mock_api_manager.return_value.get_twitter_client.return_value = MagicMock()
        mock_api_manager.return_value.get_eventregistry_client.return_value = MagicMock()
        mock_tweet_poster.return_value.post_to_twitter.return_value = "tweet_123"
        
        # Test regular bot (should try Gemini analysis)
        print("1. Testing regular bot (with Gemini analysis)...")
        bot_regular = BitcoinMiningNewsBot()
        assert not bot_regular.skip_gemini_analysis
        print("   ✅ Regular bot will attempt Gemini analysis")
        
        # Test fetch-and-tweet bot (should skip Gemini analysis)
        print("2. Testing fetch-and-tweet bot (skipping Gemini analysis)...")
        bot_no_gemini = BitcoinMiningNewsBot(skip_gemini_analysis=True)
        assert bot_no_gemini.skip_gemini_analysis
        print("   ✅ Fetch-and-tweet bot will skip Gemini analysis")
        
        # Test the _post_article method behavior
        mock_article = {
            'title': 'Test Article',
            'uri': 'test-uri-123',
            'body': 'Test content'
        }
        
        # Mock the analysis method to track if it's called
        analysis_called = False
        
        def track_analysis(article):
            nonlocal analysis_called
            analysis_called = True
        
        # Test regular bot calls analysis
        analysis_called = False
        bot_regular._analyze_and_save_report = track_analysis
        bot_regular._post_article(mock_article)
        assert analysis_called, "Regular bot should call Gemini analysis"
        print("   ✅ Regular bot called Gemini analysis")
        
        # Test fetch-and-tweet bot skips analysis
        analysis_called = False
        bot_no_gemini._analyze_and_save_report = track_analysis
        bot_no_gemini._post_article(mock_article)
        assert not analysis_called, "Fetch-and-tweet bot should skip Gemini analysis"
        print("   ✅ Fetch-and-tweet bot skipped Gemini analysis")
    
    print("✅ All tests passed!")


def test_generate_reports_script():
    """Test the generate_reports script"""
    print("\nTesting generate_reports script...")
    
    from generate_reports import GeminiReportGenerator
    
    # Test initialization without API key (should work but warn)
    generator = GeminiReportGenerator()
    assert generator.gemini_client is None
    print("   ✅ Generator handles missing API key gracefully")
    
    # Test getting recent articles
    articles = generator.get_recent_articles_needing_reports()
    print(f"   ✅ Found {len(articles)} articles needing reports")
    
    print("✅ Generate reports script works correctly!")


if __name__ == "__main__":
    test_fetch_and_tweet_skips_gemini()
    test_generate_reports_script()
    print("\n🎉 All workflow separation tests passed!")
    print("\nThe new setup provides:")
    print("1. fetch_and_tweet.py - Fetches EventRegistry news and posts to Twitter (no Gemini)")
    print("2. generate_reports.py - Creates Gemini AI analysis reports separately")
    print("3. Two GitHub Actions workflows running on different schedules")