import sys
from unittest import mock

import pytest

if "tweepy" not in sys.modules:
    sys.modules["tweepy"] = mock.MagicMock()

from config import BotConstants
from utils import TextUtils


def test_create_link_tweet_includes_call_to_action():
    article = {"url": "https://example.com/article"}

    link_tweet = TextUtils.create_link_tweet(article)

    assert BotConstants.TWEET_CALL_TO_ACTION in link_tweet
    assert article["url"] in link_tweet
    assert len(link_tweet) <= BotConstants.TWEET_MAX_LENGTH


def test_create_link_tweet_truncates_when_needed():
    long_url = "https://example.com/" + "a" * 400
    article = {"url": long_url}

    link_tweet = TextUtils.create_link_tweet(article)

    assert len(link_tweet) <= BotConstants.TWEET_MAX_LENGTH
    if len(long_url) <= BotConstants.TWEET_MAX_LENGTH:
        assert link_tweet == long_url
    else:
        assert link_tweet.endswith("...")


def test_create_thread_texts_uses_helpers(monkeypatch):
    article = {"url": "https://example.com/article"}

    monkeypatch.setattr(TextUtils, "create_hook_tweet", lambda a: "hook")
    monkeypatch.setattr(TextUtils, "create_link_tweet", lambda a: "link")

    hook, link = TextUtils.create_thread_texts(article)

    assert hook == "hook"
    assert link == "link"


def test_create_thread_texts_prevents_duplicate_urls(monkeypatch):
    """Test that create_thread_texts ensures URL is always in the last tweet (preventing duplication)"""
    article = {"url": "https://example.com/article"}

    # Mock hook tweet to contain the URL (simulating case where URL is in title/content)
    monkeypatch.setattr(TextUtils, "create_hook_tweet", 
                       lambda a: "Bitcoin news at https://example.com/article")

    hook, link = TextUtils.create_thread_texts(article)

    # Hook tweet should NOT contain the URL (it should be moved to last tweet)
    assert "https://example.com/article" not in hook
    
    # Link tweet should contain the URL (URLs always go in the last tweet)
    assert "https://example.com/article" in link
    
    # Link tweet should contain both the call to action and the URL
    assert BotConstants.TWEET_CALL_TO_ACTION in link
    
    # Hook tweet should have clean content without the URL
    assert hook == "Bitcoin news"


def test_create_thread_texts_normal_case_without_url_in_hook(monkeypatch):
    """Test normal behavior when hook tweet doesn't contain URL"""
    article = {"url": "https://example.com/article"}

    # Mock hook tweet to NOT contain URL (normal case)
    monkeypatch.setattr(TextUtils, "create_hook_tweet", 
                       lambda a: "Bitcoin mining expansion")

    hook, link = TextUtils.create_thread_texts(article)

    # Hook tweet should NOT contain the URL
    assert "https://example.com/article" not in hook
    
    # Link tweet should contain the URL (normal case)
    assert "https://example.com/article" in link
    assert BotConstants.TWEET_CALL_TO_ACTION in link
