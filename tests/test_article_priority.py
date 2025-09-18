"""
Test that the bot prioritizes the most recent unpublished article and discards older ones.
"""

import json
import sys
from unittest import mock

import pytest

# Mock modules before importing bot
if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

if "eventregistry" not in sys.modules:
    sys.modules["eventregistry"] = mock.MagicMock()

from bot import BitcoinMiningNewsBot


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    env_vars = {
        "TWITTER_API_KEY": "test_key",
        "TWITTER_API_SECRET": "test_secret",
        "TWITTER_ACCESS_TOKEN": "test_token",
        "TWITTER_ACCESS_TOKEN_SECRET": "test_token_secret",
        "EVENTREGISTRY_API_KEY": "test_er_key",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    yield

    for key in env_vars:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def mocked_dependencies(monkeypatch):
    mock_twitter_client = mock.Mock()
    mock_er_client = mock.Mock()

    monkeypatch.setattr("tweepy.Client", mock.Mock(return_value=mock_twitter_client))
    monkeypatch.setattr("eventregistry.EventRegistry", mock.Mock(return_value=mock_er_client))

    # Ensure we start with a clean posted articles list
    mock_open = mock.mock_open(read_data=json.dumps({"posted_uris": [], "queued_articles": []}))

    with mock.patch("builtins.open", mock_open):
        yield mock_twitter_client


def test_bot_prioritizes_most_recent_and_queues_older_articles(mocked_dependencies):
    """Test that when multiple new articles are available, only the most recent is posted and older ones are queued"""
    mock_twitter_client = mocked_dependencies

    # Sample articles - first one is most recent
    sample_articles = [
        {"uri": "uri-1", "title": "Most Recent News", "url": "https://example.com/1"},
        {"uri": "uri-2", "title": "Older News", "url": "https://example.com/2"},
        {"uri": "uri-3", "title": "Even Older News", "url": "https://example.com/3"},
    ]

    # Mock successful Twitter posting
    mock_tweet = mock.Mock()
    mock_tweet.data = {"id": "tweet123"}
    mock_twitter_client.create_tweet.return_value = mock_tweet

    # Create bot and test the prioritization logic
    bot = BitcoinMiningNewsBot()
    
    # Mock the fetch method to return our sample articles
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            # Reset posted articles to empty with new structure
            bot.posted_articles = {"posted_uris": [], "queued_articles": []}
            
            # Run the bot
            bot.run()

            # Verify that only the most recent article was actually posted to Twitter
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply with URL

            # Verify which article was posted
            first_call_args = mock_twitter_client.create_tweet.call_args_list[0]
            posted_text = first_call_args[1]['text']
            assert "Most Recent News" in posted_text

            # Verify that only the posted article is in posted_uris
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert "uri-1" in bot.posted_articles["posted_uris"]  # Actually posted
            
            # Verify that older articles are queued instead of being marked as posted
            assert len(bot.posted_articles["queued_articles"]) == 2
            queued_uris = [article["uri"] for article in bot.posted_articles["queued_articles"]]
            assert "uri-2" in queued_uris  # Queued for later
            assert "uri-3" in queued_uris  # Queued for later


def test_bot_works_normally_with_single_article(mocked_dependencies):
    """Test that bot works normally when there's only one new article"""
    mock_twitter_client = mocked_dependencies

    # Single article
    sample_articles = [
        {"uri": "uri-1", "title": "Single News Article", "url": "https://example.com/1"}
    ]

    # Mock successful Twitter posting
    mock_tweet = mock.Mock()
    mock_tweet.data = {"id": "tweet123"}
    mock_twitter_client.create_tweet.return_value = mock_tweet

    bot = BitcoinMiningNewsBot()
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.posted_articles = {"posted_uris": [], "queued_articles": []}
            
            bot.run()

            # Should post the single article normally
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert bot.posted_articles["posted_uris"][0] == "uri-1"
            assert len(bot.posted_articles["queued_articles"]) == 0  # No articles queued


def test_bot_posts_from_queue_when_no_new_articles(mocked_dependencies):
    """Test that bot posts from queue when no new articles are found"""
    mock_twitter_client = mocked_dependencies

    # No new articles fetched
    sample_articles = []

    # Mock successful Twitter posting
    mock_tweet = mock.Mock()
    mock_tweet.data = {"id": "tweet123"}
    mock_twitter_client.create_tweet.return_value = mock_tweet

    bot = BitcoinMiningNewsBot()
    
    # Set up queue with articles
    queued_article = {"uri": "queued-uri-1", "title": "Queued Article", "url": "https://example.com/queued"}
    bot.posted_articles = {
        "posted_uris": [], 
        "queued_articles": [
            queued_article,
            {"uri": "queued-uri-2", "title": "Another Queued Article", "url": "https://example.com/queued2"}
        ]
    }
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.run()

            # Should post from queue
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert bot.posted_articles["posted_uris"][0] == "queued-uri-1"
            assert len(bot.posted_articles["queued_articles"]) == 1  # One article remains in queue


def test_bot_skips_when_no_new_articles_and_empty_queue(mocked_dependencies):
    """Test that bot skips posting when no new articles and queue is empty"""
    mock_twitter_client = mocked_dependencies

    # No new articles fetched
    sample_articles = []

    bot = BitcoinMiningNewsBot()
    
    # Empty queue
    bot.posted_articles = {"posted_uris": [], "queued_articles": []}
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.run()

            # Should not post anything
            assert mock_twitter_client.create_tweet.call_count == 0
            assert len(bot.posted_articles["posted_uris"]) == 0
            assert len(bot.posted_articles["queued_articles"]) == 0


def test_bot_returns_failed_queue_article_to_queue(mocked_dependencies):
    """Test that failed articles from queue are returned to front of queue"""
    mock_twitter_client = mocked_dependencies

    # No new articles fetched
    sample_articles = []

    # Mock failed Twitter posting
    mock_twitter_client.create_tweet.return_value = None  # Simulate failure

    bot = BitcoinMiningNewsBot()
    
    # Set up queue with articles
    queued_article = {"uri": "queued-uri-1", "title": "Queued Article", "url": "https://example.com/queued"}
    bot.posted_articles = {
        "posted_uris": [], 
        "queued_articles": [
            queued_article,
            {"uri": "queued-uri-2", "title": "Another Queued Article", "url": "https://example.com/queued2"}
        ]
    }
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=sample_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.run()

            # Should attempt to post but fail, returning article to queue
            assert mock_twitter_client.create_tweet.call_count == 2  # 2 attempts (1 retry) per the bot logic
            assert len(bot.posted_articles["posted_uris"]) == 0  # Nothing posted
            assert len(bot.posted_articles["queued_articles"]) == 2  # Both articles still in queue
            # Failed article should be back at front of queue
            assert bot.posted_articles["queued_articles"][0] == queued_article


def test_bot_handles_backward_compatibility(mocked_dependencies):
    """Test that bot automatically upgrades old posted_articles.json format"""
    mock_twitter_client = mocked_dependencies

    # Create bot with a file that doesn't have queued_articles
    old_format_data = {"posted_uris": ["old-uri-1"]}
    
    with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(old_format_data))):
        bot = BitcoinMiningNewsBot()
        
        # Should auto-upgrade to include queued_articles
        assert "queued_articles" in bot.posted_articles
        assert bot.posted_articles["queued_articles"] == []
        assert bot.posted_articles["posted_uris"] == ["old-uri-1"]