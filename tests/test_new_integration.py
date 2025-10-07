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
            ai_provider=self.ai_provider
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
    
    def test_bot_runs_multiple_times_without_interval_restriction(self):
        """Test bot can run multiple times without interval restriction."""
        # Setup: provide relevant articles for both runs
        article1 = create_test_article(
            uri="test-789",
            title="Bitcoin Mining Difficulty Adjusts",
            body="Bitcoin mining difficulty adjustment occurred"
        )
        article2 = create_test_article(
            uri="test-790",
            title="New Mining Pool Launches",
            body="A new Bitcoin mining pool has launched"
        )
        
        # First run
        self.news_provider.articles_to_return = [article1]
        success1 = self.bot.run(keywords=["bitcoin mining"], max_articles=20)
        
        # Second run immediately after (no interval restriction)
        self.news_provider.articles_to_return = [article2]
        success2 = self.bot.run(keywords=["bitcoin mining"], max_articles=20)
        
        # Verify: both runs should complete successfully
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertTrue(self.news_provider.fetch_called)
        # Verify two articles were posted
        self.assertEqual(len(self.publisher.posted_threads), 2)


if __name__ == '__main__':
    unittest.main()
