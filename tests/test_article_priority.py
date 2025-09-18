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
    mock_open = mock.mock_open(read_data=json.dumps({"posted_uris": []}))

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
            # Reset posted articles to empty
            bot.posted_articles = {"posted_uris": []}
            
            # Run the bot
            bot.run()

            # Verify that only the most recent article was actually posted to Twitter
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply with URL

            # Verify which article was posted
            first_call_args = mock_twitter_client.create_tweet.call_args_list[0]
            posted_text = first_call_args[1]['text']
            assert "Most Recent News" in posted_text

            # Verify that only the most recent article was marked as "posted"
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert "uri-1" in bot.posted_articles["posted_uris"]  # Actually posted
            
            # Verify that older articles were queued instead of being marked as posted
            assert len(bot.posted_articles.get("queued_articles", [])) == 2
            queued_uris = [article["uri"] for article in bot.posted_articles.get("queued_articles", [])]
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
            bot.posted_articles = {"posted_uris": []}
            
            bot.run()

            # Should post the single article normally
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert bot.posted_articles["posted_uris"][0] == "uri-1"


def test_bot_posts_queued_article_when_no_new_articles_found(mocked_dependencies):
    """Test that when no new articles are found, bot posts from queued articles"""
    mock_twitter_client = mocked_dependencies

    # Mock successful Twitter posting
    mock_tweet = mock.Mock()
    mock_tweet.data = {"id": "tweet123"}
    mock_twitter_client.create_tweet.return_value = mock_tweet

    bot = BitcoinMiningNewsBot()
    
    # Set up scenario: all articles are already posted, but we have queued articles
    already_posted_articles = [
        {"uri": "uri-posted", "title": "Already Posted Article", "url": "https://example.com/posted"}
    ]
    
    # Set up initial state with queued articles
    bot.posted_articles = {
        "posted_uris": ["uri-posted"],
        "queued_articles": [
            {"uri": "uri-queued-1", "title": "Queued Article 1", "url": "https://example.com/queued1"},
            {"uri": "uri-queued-2", "title": "Queued Article 2", "url": "https://example.com/queued2"}
        ]
    }
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=already_posted_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.run()

            # Should post the oldest queued article
            assert mock_twitter_client.create_tweet.call_count == 2  # Main tweet + reply
            
            # Verify which article was posted
            first_call_args = mock_twitter_client.create_tweet.call_args_list[0]
            posted_text = first_call_args[1]['text']
            assert "Queued Article 1" in posted_text
            
            # Verify state changes
            assert "uri-queued-1" in bot.posted_articles["posted_uris"]  # Now posted
            assert len(bot.posted_articles["queued_articles"]) == 1  # One removed from queue
            assert bot.posted_articles["queued_articles"][0]["uri"] == "uri-queued-2"  # Second article still queued


def test_bot_skips_when_no_new_articles_and_no_queued_articles(mocked_dependencies):
    """Test that bot skips posting when no new articles and no queued articles"""
    mock_twitter_client = mocked_dependencies

    bot = BitcoinMiningNewsBot()
    
    # Set up scenario: all articles are already posted, no queued articles
    already_posted_articles = [
        {"uri": "uri-posted", "title": "Already Posted Article", "url": "https://example.com/posted"}
    ]
    
    # Set up initial state with no queued articles
    bot.posted_articles = {
        "posted_uris": ["uri-posted"],
        "queued_articles": []
    }
    
    with mock.patch.object(bot, 'fetch_bitcoin_mining_articles', return_value=already_posted_articles):
        with mock.patch.object(bot, '_save_posted_articles'):
            bot.run()

            # Should not post anything
            assert mock_twitter_client.create_tweet.call_count == 0
            
            # State should remain unchanged
            assert len(bot.posted_articles["posted_uris"]) == 1
            assert len(bot.posted_articles["queued_articles"]) == 0