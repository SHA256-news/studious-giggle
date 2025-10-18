#!/usr/bin/env python3
"""
Tests for Article Fetch Logic and Enhanced Deduplication
Tests the fixes for re-fetching old articles and re-publishing duplicates.
"""

import sys
import os
import json
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core import BitcoinMiningBot, Config, Article, Storage, NewsAPI, ContentSimilarity
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


class TestFetchAndDeduplication:
    """Tests for improved fetch logic and deduplication."""

    def test_fetch_articles_with_start_datetime(self):
        """Test that fetch_articles accepts and uses start_datetime parameter."""
        config = Config()
        config.eventregistry_api_key = "test_key"
        news_api = NewsAPI(config)
        
        # Mock the EventRegistry client
        mock_client = Mock()
        mock_query_iter = Mock()
        
        with patch('eventregistry.EventRegistry', return_value=mock_client):
            with patch('eventregistry.QueryArticlesIter', return_value=mock_query_iter) as mock_query_class:
                # Mock the query execution to return empty list
                mock_query_iter.execQuery.return_value = []
                
                # Test with explicit start_datetime
                test_datetime = datetime.now(timezone.utc) - timedelta(hours=2)
                articles = news_api.fetch_articles(max_articles=10, start_datetime=test_datetime)
                
                # Verify QueryArticlesIter was called with our start_datetime
                assert mock_query_class.called
                call_kwargs = mock_query_class.call_args[1]
                assert 'dateStart' in call_kwargs
                assert call_kwargs['dateStart'] == test_datetime
                
                print("  ✅ test_fetch_articles_with_start_datetime")

    def test_fetch_articles_default_behavior(self):
        """Test that fetch_articles defaults to article_lookback_days when start_datetime not provided."""
        config = Config()
        config.eventregistry_api_key = "test_key"
        config.article_lookback_days = 1
        news_api = NewsAPI(config)
        
        # Mock the EventRegistry client
        mock_client = Mock()
        mock_query_iter = Mock()
        
        with patch('eventregistry.EventRegistry', return_value=mock_client):
            with patch('eventregistry.QueryArticlesIter', return_value=mock_query_iter) as mock_query_class:
                # Mock the query execution to return empty list
                mock_query_iter.execQuery.return_value = []
                
                # Test without start_datetime (should use default)
                articles = news_api.fetch_articles(max_articles=10)
                
                # Verify QueryArticlesIter was called with dateStart
                assert mock_query_class.called
                call_kwargs = mock_query_class.call_args[1]
                assert 'dateStart' in call_kwargs
                # Should be approximately 1 day ago
                expected_datetime = datetime.now(timezone.utc) - timedelta(days=1)
                time_diff = abs((call_kwargs['dateStart'] - expected_datetime).total_seconds())
                assert time_diff < 60  # Within 1 minute is close enough
                
                print("  ✅ test_fetch_articles_default_behavior")

    def test_bot_uses_last_run_time_for_fetch(self):
        """Test that bot uses last_run_time from storage when fetching articles."""
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            last_run = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            json.dump({
                "posted_uris": ["http://example.com/old"],
                "queued_articles": [],
                "posted_articles_history": [],
                "last_run_time": last_run
            }, f)
        
        try:
            config = Config()
            config.posted_articles_file = temp_file
            config.twitter_api_key = "test"
            config.twitter_api_secret = "test"
            config.twitter_access_token = "test"
            config.twitter_access_token_secret = "test"
            config.eventregistry_api_key = "test"
            config.gemini_api_key = "test"
            
            bot = BitcoinMiningBot(config=config)
            
            # Mock the news API to capture the call
            with patch.object(bot.news, 'fetch_articles', return_value=[]) as mock_fetch:
                # Mock Twitter and Gemini clients to avoid actual API calls
                with patch.object(bot, '_twitter', Mock()):
                    with patch.object(bot, '_gemini', Mock()):
                        bot.run()
                
                # Verify fetch_articles was called with start_datetime
                assert mock_fetch.called
                call_args = mock_fetch.call_args
                
                # Check if start_datetime was passed
                if 'start_datetime' in call_args[1]:
                    start_dt = call_args[1]['start_datetime']
                    assert start_dt is not None
                    # Should be approximately the last_run_time we set
                    expected_dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
                    if expected_dt.tzinfo is None:
                        expected_dt = expected_dt.replace(tzinfo=timezone.utc)
                    time_diff = abs((start_dt - expected_dt).total_seconds())
                    assert time_diff < 1  # Should be exact
            
            print("  ✅ test_bot_uses_last_run_time_for_fetch")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_deduplication_against_posted_history(self):
        """Test that new articles are checked against posted_articles_history for duplicates."""
        # Create temporary file with posted history
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            json.dump({
                "posted_uris": ["http://example.com/article1"],
                "queued_articles": [],
                "posted_articles_history": [
                    {
                        "url": "http://example.com/article1",
                        "title": "Marathon Digital Holdings Expands Bitcoin Mining Operations in Texas",
                        "source": "Test Source",
                        "date_published": "2024-01-01T12:00:00Z",
                        "date_posted": "2024-01-01T13:00:00Z",
                        "body_preview": "Marathon Digital Holdings announced a major expansion of its Bitcoin mining operations in West Texas. The company will deploy 10,000 new ASIC miners at its facility in Garden City, increasing its total hashrate capacity by 50%. The expansion is expected to be completed by Q4 2024."
                    }
                ],
                "last_run_time": datetime.now(timezone.utc).isoformat()
            }, f)
        
        try:
            config = Config()
            config.posted_articles_file = temp_file
            config.twitter_api_key = "test"
            config.twitter_api_secret = "test"
            config.twitter_access_token = "test"
            config.twitter_access_token_secret = "test"
            config.eventregistry_api_key = "test"
            config.gemini_api_key = "test"
            
            bot = BitcoinMiningBot(config=config)
            
            # Create a very similar article (different URL but similar content)
            similar_article_data = {
                "title": "Marathon Digital Holdings Expands Bitcoin Mining Operations in Texas",
                "body": "Marathon Digital Holdings announced a major expansion of its Bitcoin mining operations in West Texas. The company will deploy 10,000 new ASIC miners at its facility in Garden City, increasing its total hashrate capacity significantly. The expansion is expected to be completed by the end of 2024.",
                "url": "http://different-source.com/article2",
                "uri": "http://different-source.com/article2",
                "source": {"title": "Different Source"},
                "dateTimePub": "2024-01-01T14:00:00Z"
            }
            similar_article = Article.from_dict(similar_article_data)
            
            # Mock fetch_articles to return our similar article
            with patch.object(bot.news, 'fetch_articles', return_value=[similar_article]):
                # Mock Twitter and Gemini to avoid actual API calls
                with patch.object(bot, '_twitter', Mock()):
                    with patch.object(bot, '_gemini', Mock()):
                        # Mock the posting method to track if it was called
                        with patch.object(bot, '_post_article', return_value=True) as mock_post:
                            bot.run()
                            
                            # The similar article should be filtered out as duplicate
                            # So _post_article should NOT be called
                            assert not mock_post.called, "Similar article should have been filtered as duplicate"
            
            print("  ✅ test_deduplication_against_posted_history")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_deduplication_against_queued_articles(self):
        """Test that deduplication still works against queued articles."""
        # Create temporary file with queued article
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            json.dump({
                "posted_uris": [],
                "queued_articles": [
                    {
                        "title": "CleanSpark Reports Record Bitcoin Mining Revenue in Q3",
                        "body": "CleanSpark Inc announced record Bitcoin mining revenue for the third quarter. The company mined 1,800 Bitcoin during the quarter, a 40% increase from Q2. CleanSpark's hashrate now exceeds 16 EH/s following recent expansions.",
                        "url": "http://example.com/queued",
                        "source": {"title": "Test Source"},
                        "dateTimePub": "2024-01-01T12:00:00Z"
                    }
                ],
                "posted_articles_history": [],
                "last_run_time": datetime.now(timezone.utc).isoformat()
            }, f)
        
        try:
            config = Config()
            config.posted_articles_file = temp_file
            config.twitter_api_key = "test"
            config.twitter_api_secret = "test"
            config.twitter_access_token = "test"
            config.twitter_access_token_secret = "test"
            config.eventregistry_api_key = "test"
            config.gemini_api_key = "test"
            
            bot = BitcoinMiningBot(config=config)
            
            # Create a similar article (different URL but similar content)
            similar_article_data = {
                "title": "CleanSpark Reports Record Bitcoin Mining Revenue in Q3",
                "body": "CleanSpark Inc announced record Bitcoin mining revenue for the third quarter. The company mined 1,800 Bitcoin during the quarter, representing a 40% increase compared to Q2. CleanSpark's hashrate now exceeds 16 EH/s after recent expansions.",
                "url": "http://different.com/article",
                "uri": "http://different.com/article",
                "source": {"title": "Different Source"},
                "dateTimePub": "2024-01-01T13:00:00Z"
            }
            similar_article = Article.from_dict(similar_article_data)
            
            # Mock fetch_articles to return our similar article
            with patch.object(bot.news, 'fetch_articles', return_value=[similar_article]):
                # Mock Twitter and Gemini
                with patch.object(bot, '_twitter', Mock()):
                    with patch.object(bot, '_gemini', Mock()):
                        # Track if the new article gets added to queue
                        initial_queue_length = len(bot.posted_data.get("queued_articles", []))
                        
                        # Mock the posting method to simulate successful post of queued article
                        # This will post the queued article, not the new similar one
                        with patch.object(bot, '_post_article', return_value=True) as mock_post:
                            bot.run()
                            
                            # The queued article should be posted (not the new similar one)
                            # The new similar article should be filtered as duplicate
                            final_queue_length = len(bot.posted_data.get("queued_articles", []))
                            
                            # Queue should be empty after posting the queued article
                            # and the new similar article should NOT be added
                            assert final_queue_length == 0, f"Queue should be empty but has {final_queue_length} articles"
            
            print("  ✅ test_deduplication_against_queued_articles")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_url_deduplication_still_works(self):
        """Test that URL-based deduplication still works (exact URL match)."""
        # Create temporary file with posted URL
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            json.dump({
                "posted_uris": ["http://example.com/exact-match"],
                "queued_articles": [],
                "posted_articles_history": [
                    {
                        "url": "http://example.com/exact-match",
                        "title": "Original Article",
                        "source": "Test Source",
                        "date_published": "2024-01-01T12:00:00Z",
                        "date_posted": "2024-01-01T13:00:00Z",
                        "body_preview": "Some content"
                    }
                ],
                "last_run_time": datetime.now(timezone.utc).isoformat()
            }, f)
        
        try:
            config = Config()
            config.posted_articles_file = temp_file
            config.twitter_api_key = "test"
            config.twitter_api_secret = "test"
            config.twitter_access_token = "test"
            config.twitter_access_token_secret = "test"
            config.eventregistry_api_key = "test"
            config.gemini_api_key = "test"
            
            bot = BitcoinMiningBot(config=config)
            
            # Create article with exact same URL
            duplicate_url_article_data = {
                "title": "Completely Different Title",
                "body": "Completely different content about something else",
                "url": "http://example.com/exact-match",
                "uri": "http://example.com/exact-match",
                "source": {"title": "Test Source"},
                "dateTimePub": "2024-01-01T14:00:00Z"
            }
            duplicate_article = Article.from_dict(duplicate_url_article_data)
            
            # Mock fetch_articles to return our duplicate URL article
            with patch.object(bot.news, 'fetch_articles', return_value=[duplicate_article]):
                with patch.object(bot, '_twitter', Mock()):
                    with patch.object(bot, '_gemini', Mock()):
                        with patch.object(bot, '_post_article', return_value=True) as mock_post:
                            bot.run()
                            
                            # Should be filtered by URL match before content check
                            assert not mock_post.called, "Article with duplicate URL should be filtered"
            
            print("  ✅ test_url_deduplication_still_works")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_new_unique_article_not_filtered(self):
        """Test that genuinely new articles are not filtered out."""
        # Create temporary file with different article
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            json.dump({
                "posted_uris": ["http://example.com/old-article"],
                "queued_articles": [],
                "posted_articles_history": [
                    {
                        "url": "http://example.com/old-article",
                        "title": "Old News About Mining Difficulty",
                        "source": "Test Source",
                        "date_published": "2024-01-01T12:00:00Z",
                        "date_posted": "2024-01-01T13:00:00Z",
                        "body_preview": "Bitcoin mining difficulty reached a new all-time high this week..."
                    }
                ],
                "last_run_time": datetime.now(timezone.utc).isoformat()
            }, f)
        
        try:
            config = Config()
            config.posted_articles_file = temp_file
            config.twitter_api_key = "test"
            config.twitter_api_secret = "test"
            config.twitter_access_token = "test"
            config.twitter_access_token_secret = "test"
            config.eventregistry_api_key = "test"
            config.gemini_api_key = "test"
            
            bot = BitcoinMiningBot(config=config)
            
            # Create completely different article
            new_article_data = {
                "title": "CleanSpark Announces New Mining Facility in Georgia",
                "body": "CleanSpark Inc., a leading Bitcoin mining company, announced plans to open a new mining facility in Georgia with 100MW capacity...",
                "url": "http://example.com/new-article",
                "uri": "http://example.com/new-article",
                "source": {"title": "Test Source"},
                "dateTimePub": "2024-01-02T12:00:00Z"
            }
            new_article = Article.from_dict(new_article_data)
            
            # Mock fetch_articles to return our new article
            with patch.object(bot.news, 'fetch_articles', return_value=[new_article]):
                with patch.object(bot, '_twitter', Mock()):
                    # Mock Gemini to return thread tweets
                    mock_gemini = Mock()
                    with patch.object(bot, '_gemini', mock_gemini):
                        # Mock TextProcessor to return valid thread
                        with patch('core.TextProcessor.create_tweet_thread', return_value=["Tweet 1", "Tweet 2"]):
                            with patch.object(bot, '_post_article', return_value=True) as mock_post:
                                bot.run()
                                
                                # New unique article should be posted
                                assert mock_post.called, "New unique article should not be filtered"
            
            print("  ✅ test_new_unique_article_not_filtered")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def run_tests():
    """Run all tests."""
    print("\n🧪 Running Fetch and Deduplication Tests")
    print("=" * 50)
    
    test = TestFetchAndDeduplication()
    tests = [
        test.test_fetch_articles_with_start_datetime,
        test.test_fetch_articles_default_behavior,
        test.test_bot_uses_last_run_time_for_fetch,
        test.test_deduplication_against_posted_history,
        test.test_deduplication_against_queued_articles,
        test.test_url_deduplication_still_works,
        test.test_new_unique_article_not_filtered,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ {test_func.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
