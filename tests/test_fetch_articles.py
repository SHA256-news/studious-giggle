import json
import sys
from unittest import mock

import pytest


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


def test_post_to_twitter_posts_single_tweet(mocked_dependencies):
    mock_twitter_client = mocked_dependencies

    tweet = mock.Mock()
    tweet.data = {"id": "123"}

    mock_twitter_client.create_tweet.return_value = tweet

    bot = BitcoinMiningNewsBot()

    article = {
        "title": "Bitcoin mining news",
        "uri": "article-uri",
        "url": "https://example.com/article",
    }

    result = bot.post_to_twitter(article)

    assert result == "123"
    assert mock_twitter_client.create_tweet.call_count == 1


def test_post_to_twitter_without_url_does_not_post_reply(mocked_dependencies):
    mock_twitter_client = mocked_dependencies

    first_tweet = mock.Mock()
    first_tweet.data = {"id": "abc"}
    mock_twitter_client.create_tweet.return_value = first_tweet

    bot = BitcoinMiningNewsBot()

    article = {
        "title": "Bitcoin mining news",
        "uri": "article-uri",
        # No URL should skip replying
    }

    result = bot.post_to_twitter(article)

    assert result == "abc"
    mock_twitter_client.create_tweet.assert_called_once()
