"""
Content filtering services - determines article relevance and duplicates.
"""
import logging
from typing import List, Set
from datetime import datetime, timedelta

from src.domain import Article
from src.domain.value_objects import ContentFingerprint, TitleSignature

logger = logging.getLogger(__name__)


class BitcoinMiningFilter:
    """
    Filters articles for Bitcoin mining relevance.
    Configurable rules instead of hard-coded keywords.
    """
    
    # Public mining companies (always relevant)
    PUBLIC_MINERS = {
        "marathon digital", "mara", "riot platforms", "riot blockchain",
        "cleanspark", "clsk", "hut 8", "hut", "core scientific", "corz",
        "cipher mining", "cifr", "bitfarms", "bitf", "hive digital",
        "terawulf", "wulf", "bitdeer", "btdr", "iris energy", "iren",
        "bit digital", "btbt", "greenidge", "gree", "stronghold", "sdig",
        "argo blockchain", "arbk", "canaan", "can", "bit mining", "btcm",
        "bitfufu", "fufu"
    }
    
    # Core mining terms
    MINING_TERMS = {
        "bitcoin mining", "btc mining", "bitcoin miner", "bitcoin miners",
        "mining bitcoin", "mine bitcoin", "crypto mining", "cryptocurrency mining",
        "hash rate", "hashrate", "mining difficulty", "mining power",
        "asic miner", "asic miners", "mining hardware", "mining equipment",
        "mining pool", "mining pools", "mining farm", "mining farms",
        "mining operation", "mining operations", "mining facility",
        "mining company", "mining companies", "mining industry"
    }
    
    # Mining-related concepts
    RELATED_TERMS = {
        "mining rig", "mining rigs", "mining revenue", "mining profitability",
        "block reward", "mining reward", "miner revenue", "miner profitability",
        "electricity cost", "power consumption", "energy consumption",
        "data center", "bitcoin production", "bitcoin generated"
    }
    
    # Exclusion terms (not mining-focused)
    EXCLUSION_TERMS = {
        "cloud mining app", "free mining", "mining scam", "ponzi",
        "defi", "nft", "web3", "metaverse", "token launch",
        "ico", "airdrop", "tokenized", "staking only"
    }
    
    def __init__(
        self,
        require_public_miner: bool = False,
        min_mining_terms: int = 1,
        check_exclusions: bool = True
    ):
        """
        Initialize filter with configurable rules.
        
        Args:
            require_public_miner: If True, only accept articles about public mining companies
            min_mining_terms: Minimum number of mining terms required
            check_exclusions: If True, reject articles with exclusion terms
        """
        self.require_public_miner = require_public_miner
        self.min_mining_terms = min_mining_terms
        self.check_exclusions = check_exclusions
    
    def is_relevant(self, article: Article) -> bool:
        """
        Check if article is relevant to Bitcoin mining.
        
        Args:
            article: Article to check
            
        Returns:
            True if article is relevant, False otherwise
        """
        text = f"{article.title} {article.body}".lower()
        
        # Check for exclusion terms first
        if self.check_exclusions:
            if any(term in text for term in self.EXCLUSION_TERMS):
                logger.info(f"Filtered (exclusion term): {article.title}")
                return False
        
        # Check for public mining companies (auto-approve)
        if any(company in text for company in self.PUBLIC_MINERS):
            logger.info(f"Approved (public miner): {article.title}")
            return True
        
        # Count mining terms
        mining_count = sum(1 for term in self.MINING_TERMS if term in text)
        related_count = sum(1 for term in self.RELATED_TERMS if term in text)
        
        total_count = mining_count + (related_count * 0.5)  # Related terms worth half
        
        # Check if meets minimum threshold
        if total_count >= self.min_mining_terms:
            logger.info(f"Approved (mining terms: {total_count}): {article.title}")
            return True
        
        logger.info(f"Filtered (insufficient mining focus: {total_count}): {article.title}")
        return False


class DuplicateDetector:
    """
    Detects duplicate articles using content fingerprinting.
    Stateful detector maintains history of seen articles.
    """
    
    def __init__(
        self,
        title_threshold: float = 0.8,
        content_threshold: float = 0.7,
        time_window_hours: int = 48
    ):
        """
        Initialize duplicate detector.
        
        Args:
            title_threshold: Similarity threshold for title matching (0-1)
            content_threshold: Similarity threshold for content matching (0-1)
            time_window_hours: Only compare articles within this time window
        """
        self.title_threshold = title_threshold
        self.content_threshold = content_threshold
        self.time_window_hours = time_window_hours
        
        # In-memory cache of recent articles
        self._seen_articles: List[Article] = []
        self._title_signatures: List[TitleSignature] = []
        self._content_fingerprints: List[ContentFingerprint] = []
    
    def add_articles(self, articles: List[Article]) -> None:
        """Add articles to seen history."""
        for article in articles:
            self._seen_articles.append(article)
            self._title_signatures.append(TitleSignature.from_title(article.title))
            self._content_fingerprints.append(ContentFingerprint.from_text(article.body))
        
        # Clean old articles outside time window
        self._clean_old_articles()
    
    def is_duplicate(self, article: Article) -> bool:
        """
        Check if article is a duplicate of previously seen articles.
        
        Args:
            article: Article to check
            
        Returns:
            True if duplicate, False otherwise
        """
        if not self._seen_articles:
            return False
        
        article_title = TitleSignature.from_title(article.title)
        article_content = ContentFingerprint.from_text(article.body)
        
        # Check against all seen articles
        for i, seen_article in enumerate(self._seen_articles):
            # Skip if outside time window
            if not self._within_time_window(article, seen_article):
                continue
            
            # Check title similarity
            title_sim = article_title.similarity_score(self._title_signatures[i])
            if title_sim >= self.title_threshold:
                logger.info(f"Duplicate detected (title {title_sim:.2f}): {article.title}")
                return True
            
            # Check content similarity
            content_sim = article_content.similarity_score(self._content_fingerprints[i])
            if content_sim >= self.content_threshold:
                logger.info(f"Duplicate detected (content {content_sim:.2f}): {article.title}")
                return True
        
        return False
    
    def _within_time_window(self, article1: Article, article2: Article) -> bool:
        """Check if two articles are within the time window."""
        if not article1.published_at or not article2.published_at:
            return True  # If no dates, always compare
        
        time_diff = abs((article1.published_at - article2.published_at).total_seconds())
        return time_diff <= (self.time_window_hours * 3600)
    
    def _clean_old_articles(self) -> None:
        """Remove articles older than time window."""
        if not self._seen_articles:
            return
        
        cutoff = datetime.now() - timedelta(hours=self.time_window_hours)
        
        # Filter articles within time window
        valid_indices = [
            i for i, article in enumerate(self._seen_articles)
            if not article.published_at or article.published_at >= cutoff
        ]
        
        self._seen_articles = [self._seen_articles[i] for i in valid_indices]
        self._title_signatures = [self._title_signatures[i] for i in valid_indices]
        self._content_fingerprints = [self._content_fingerprints[i] for i in valid_indices]
        
        if len(valid_indices) < len(self._seen_articles):
            removed = len(self._seen_articles) - len(valid_indices)
            logger.info(f"Cleaned {removed} old articles from duplicate detector")
