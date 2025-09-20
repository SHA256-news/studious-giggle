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
