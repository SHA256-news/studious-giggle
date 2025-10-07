"""
Unit tests for domain entities and value objects.
"""
import unittest
from datetime import datetime

from src.domain import Article, Tweet, Thread, PostedArticle, ArticleStatus
from src.domain.value_objects import ContentFingerprint, TitleSignature


class TestArticle(unittest.TestCase):
    """Test Article entity."""
    
    def test_article_creation(self):
        """Test creating a valid article."""
        article = Article(
            uri="test-123",
            title="Bitcoin Mining Test",
            url="https://example.com/article",
            source="Test Source",
            body="Test content"
        )
        
        self.assertEqual(article.uri, "test-123")
        self.assertEqual(article.title, "Bitcoin Mining Test")
        self.assertEqual(article.url, "https://example.com/article")
    
    def test_article_validation(self):
        """Test article validation."""
        with self.assertRaises(ValueError):
            Article(uri="", title="Test", url="https://example.com", source="", body="")
        
        with self.assertRaises(ValueError):
            Article(uri="123", title="", url="https://example.com", source="", body="")
        
        with self.assertRaises(ValueError):
            Article(uri="123", title="Test", url="invalid-url", source="", body="")
    
    def test_article_serialization(self):
        """Test article to_dict and from_dict."""
        article = Article(
            uri="test-123",
            title="Test",
            url="https://example.com",
            source="Source",
            body="Body"
        )
        
        data = article.to_dict()
        restored = Article.from_dict(data)
        
        self.assertEqual(article.uri, restored.uri)
        self.assertEqual(article.title, restored.title)


class TestTweet(unittest.TestCase):
    """Test Tweet entity."""
    
    def test_tweet_creation(self):
        """Test creating a valid tweet."""
        tweet = Tweet("Test tweet content")
        self.assertEqual(tweet.text, "Test tweet content")
        self.assertEqual(tweet.char_count, len("Test tweet content"))
    
    def test_tweet_too_long(self):
        """Test tweet length validation."""
        with self.assertRaises(ValueError):
            Tweet("a" * 281)
    
    def test_tweet_empty(self):
        """Test empty tweet validation."""
        with self.assertRaises(ValueError):
            Tweet("")


class TestThread(unittest.TestCase):
    """Test Thread entity."""
    
    def test_thread_creation(self):
        """Test creating a valid thread."""
        article = Article(
            uri="test",
            title="Test",
            url="https://example.com",
            source="Source",
            body="Body"
        )
        
        tweets = (
            Tweet("First tweet"),
            Tweet("Second tweet")
        )
        
        thread = Thread(tweets=tweets, article=article)
        
        self.assertEqual(thread.tweet_count, 2)
        self.assertEqual(len(thread.to_list()), 2)
    
    def test_thread_empty(self):
        """Test empty thread validation."""
        article = Article(
            uri="test",
            title="Test",
            url="https://example.com",
            source="Source",
            body="Body"
        )
        
        with self.assertRaises(ValueError):
            Thread(tweets=(), article=article)


class TestContentFingerprint(unittest.TestCase):
    """Test ContentFingerprint value object."""
    
    def test_fingerprint_creation(self):
        """Test creating content fingerprint."""
        fp = ContentFingerprint.from_text("Bitcoin mining is important")
        
        self.assertIsNotNone(fp.hash_value)
        self.assertGreater(fp.word_count, 0)
        self.assertGreater(len(fp.key_terms), 0)
    
    def test_fingerprint_similarity(self):
        """Test similarity calculation."""
        fp1 = ContentFingerprint.from_text("Bitcoin mining operations continue to expand")
        fp2 = ContentFingerprint.from_text("Bitcoin mining operations continue to grow")
        fp3 = ContentFingerprint.from_text("Completely different content about cats")
        
        # Similar texts should have high similarity
        self.assertGreater(fp1.similarity_score(fp2), 0.5)
        
        # Different texts should have low similarity
        self.assertLess(fp1.similarity_score(fp3), 0.3)


class TestTitleSignature(unittest.TestCase):
    """Test TitleSignature value object."""
    
    def test_signature_creation(self):
        """Test creating title signature."""
        sig = TitleSignature.from_title("Bitcoin Mining Hits New High")
        
        self.assertIsNotNone(sig.normalized)
        self.assertGreater(len(sig.word_set), 0)
    
    def test_signature_similarity(self):
        """Test title similarity."""
        sig1 = TitleSignature.from_title("Bitcoin Mining Difficulty Increases")
        sig2 = TitleSignature.from_title("Mining Difficulty for Bitcoin Increases")
        sig3 = TitleSignature.from_title("Completely Different Title")
        
        # Similar titles
        self.assertGreater(sig1.similarity_score(sig2), 0.5)
        
        # Different titles
        self.assertLess(sig1.similarity_score(sig3), 0.3)


if __name__ == '__main__':
    unittest.main()
