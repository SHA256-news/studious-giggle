"""
Unit tests for filtering services.
"""
import unittest
from datetime import datetime, timedelta

from src.services.filtering import BitcoinMiningFilter, DuplicateDetector
from tests.test_doubles import create_test_article


class TestBitcoinMiningFilter(unittest.TestCase):
    """Test Bitcoin mining relevance filter."""
    
    def setUp(self):
        self.filter = BitcoinMiningFilter()
    
    def test_public_miner_approved(self):
        """Test that public mining companies are always approved."""
        article = create_test_article(
            title="Marathon Digital Announces Expansion",
            body="Marathon Digital is expanding mining operations"
        )
        
        self.assertTrue(self.filter.is_relevant(article))
    
    def test_mining_terms_approved(self):
        """Test articles with mining terms are approved."""
        article = create_test_article(
            title="Bitcoin Mining Difficulty Reaches New High",
            body="Bitcoin mining difficulty increased to record levels"
        )
        
        self.assertTrue(self.filter.is_relevant(article))
    
    def test_exclusion_terms_rejected(self):
        """Test articles with exclusion terms are rejected."""
        article = create_test_article(
            title="New Cloud Mining App Scam Alert",
            body="Free mining app promises returns"
        )
        
        self.assertFalse(self.filter.is_relevant(article))
    
    def test_insufficient_mining_focus(self):
        """Test articles without enough mining focus are rejected."""
        article = create_test_article(
            title="General Bitcoin News",
            body="Bitcoin price increased today"
        )
        
        self.assertFalse(self.filter.is_relevant(article))
    
    def test_related_terms_counted(self):
        """Test that related terms contribute to relevance."""
        article = create_test_article(
            title="Mining Facility Power Consumption Study",
            body="Study examines electricity costs for mining operations"
        )
        
        self.assertTrue(self.filter.is_relevant(article))


class TestDuplicateDetector(unittest.TestCase):
    """Test duplicate detection."""
    
    def setUp(self):
        self.detector = DuplicateDetector(
            title_threshold=0.8,
            content_threshold=0.7
        )
    
    def test_exact_duplicate_detected(self):
        """Test exact duplicate is detected."""
        article1 = create_test_article(
            uri="article-1",
            title="Bitcoin Mining Difficulty Increases",
            body="Bitcoin mining difficulty increased to new highs"
        )
        
        article2 = create_test_article(
            uri="article-2",
            title="Bitcoin Mining Difficulty Increases",
            body="Bitcoin mining difficulty increased to new highs"
        )
        
        self.detector.add_articles([article1])
        self.assertTrue(self.detector.is_duplicate(article2))
    
    def test_similar_title_detected(self):
        """Test similar titles are detected as duplicates."""
        article1 = create_test_article(
            uri="article-1",
            title="Marathon Digital Expands Mining Operations",
            body="Different content"
        )
        
        article2 = create_test_article(
            uri="article-2",
            title="Marathon Digital Mining Operations Expand",
            body="Other content"
        )
        
        self.detector.add_articles([article1])
        self.assertTrue(self.detector.is_duplicate(article2))
    
    def test_different_articles_not_duplicate(self):
        """Test completely different articles are not duplicates."""
        article1 = create_test_article(
            uri="article-1",
            title="Marathon Digital Expands",
            body="Marathon expands operations"
        )
        
        article2 = create_test_article(
            uri="article-2",
            title="Riot Platforms Announces Results",
            body="Riot reports quarterly earnings"
        )
        
        self.detector.add_articles([article1])
        self.assertFalse(self.detector.is_duplicate(article2))
    
    def test_time_window_filtering(self):
        """Test that old articles are cleaned from detector."""
        old_date = datetime.now() - timedelta(hours=50)
        recent_date = datetime.now()
        
        old_article = create_test_article(
            uri="old",
            published_at=old_date
        )
        
        recent_article = create_test_article(
            uri="recent",
            published_at=recent_date
        )
        
        self.detector.add_articles([old_article])
        # Old article should be cleaned due to time window
        self.assertFalse(self.detector.is_duplicate(recent_article))


if __name__ == '__main__':
    unittest.main()
