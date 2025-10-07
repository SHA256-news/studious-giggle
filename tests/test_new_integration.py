"""
New integration tests for clean architecture bot.
"""
import unittest
from datetime import datetime, timedelta

from src.app import BitcoinMiningNewsBot
from tests.test_doubles import (
    FakeNewsProvider,
    FakeAIProvider,
    FakePublisher,
    FakeStorage,
    create_test_article
)


class TestBotIntegration(unittest.TestCase):
    """Test bot with fake dependencies."""
    
    def setUp(self):
        """Set up test bot with fake adapters."""
        self.news_provider = FakeNewsProvider()
        self.storage = FakeStorage()
        self.publisher = FakePublisher()
        self.ai_provider = FakeAIProvider()
        
        self.bot = BitcoinMiningNewsBot(
            news_provider=self.news_provider,
            storage=self.storage,
            publisher=self.publisher,
            ai_provider=self.ai_provider,
            min_interval_minutes=90
        )
    
    def test_bot_run_with_relevant_articles(self):
        """Test bot successfully processes relevant articles."""
        # Setup: provide relevant articles
        article = create_test_article(
            uri="test-123",
            title="Marathon Digital Expands Mining Operations",
            body="Marathon Digital announced expansion of Bitcoin mining"
        )
        self.news_provider.articles_to_return = [article]
        
        # Run bot
        success = self.bot.run(keywords=["bitcoin mining"], max_articles=20)
        
        # Verify
        self.assertTrue(success)
        self.assertTrue(self.news_provider.fetch_called)
        self.assertTrue(self.publisher.post_thread_called)
        self.assertEqual(len(self.publisher.posted_threads), 1)
        self.assertTrue(self.storage.save_posted_article_called)
    
    def test_bot_run_filters_irrelevant_articles(self):
        """Test bot filters out irrelevant articles."""
        # Setup: provide irrelevant article
        article = create_test_article(
            uri="test-456",
            title="General Crypto News",
            body="Generic cryptocurrency content"
        )
        self.news_provider.articles_to_return = [article]
        
        # Run bot
        success = self.bot.run(keywords=["bitcoin mining"], max_articles=20)
        
        # Verify: no posting happened
        self.assertFalse(success)
        self.assertFalse(self.publisher.post_thread_called)
    
    def test_bot_respects_minimum_interval(self):
        """Test bot respects minimum interval between runs."""
        # Set last run time to recent
        self.storage.last_run_time = datetime.now() - timedelta(minutes=30)
        
        # Run bot
        success = self.bot.run(keywords=["bitcoin mining"], max_articles=20)
        
        # Verify: should not fetch or post
        self.assertFalse(success)
        self.assertFalse(self.news_provider.fetch_called)
        self.assertFalse(self.publisher.post_thread_called)


if __name__ == '__main__':
    unittest.main()
