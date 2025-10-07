"""
EventRegistry adapter - fetches Bitcoin mining news articles.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from eventregistry import EventRegistry, QueryArticlesIter

from src.domain import Article
from src.adapters.interfaces import NewsProvider, NewsProviderError

logger = logging.getLogger(__name__)


class EventRegistryAdapter(NewsProvider):
    """Adapter for EventRegistry news API."""
    
    def __init__(self, api_key: str):
        """
        Initialize EventRegistry client.
        
        Args:
            api_key: EventRegistry API key
        """
        if not api_key:
            raise ValueError("EventRegistry API key cannot be empty")
        
        self.api_key = api_key
        self._client: Optional[EventRegistry] = None
    
    @property
    def client(self) -> EventRegistry:
        """Lazy-load EventRegistry client."""
        if self._client is None:
            self._client = EventRegistry(apiKey=self.api_key, allowUseOfArchive=False)
        return self._client
    
    def fetch_articles(
        self,
        keywords: List[str],
        max_results: int = 20,
        since_date: Optional[datetime] = None
    ) -> List[Article]:
        """
        Fetch articles matching Bitcoin mining keywords.
        
        Args:
            keywords: List of search keywords
            max_results: Maximum number of articles to return
            since_date: Only return articles published after this date
            
        Returns:
            List of Article objects
            
        Raises:
            NewsProviderError: If the API call fails
        """
        try:
            # Default to last 24 hours if no date specified
            if since_date is None:
                since_date = datetime.now() - timedelta(days=1)
            
            # Build query - EventRegistry takes single keyword string
            keyword_query = " OR ".join(f'"{kw}"' for kw in keywords)
            
            logger.info(f"Fetching articles with query: {keyword_query}")
            logger.info(f"Since date: {since_date.isoformat()}")
            
            # Query articles
            query_iter = QueryArticlesIter(
                keywords=keyword_query,
                lang="eng"
            )
            
            articles: List[Article] = []
            count = 0
            
            for event_article in query_iter.execQuery(
                self.client,
                sortBy="date",
                sortByAsc=False,
                maxItems=max_results * 2  # Fetch extra for filtering
            ):
                if count >= max_results:
                    break
                
                try:
                    article = self._parse_article(event_article)
                    
                    # Filter by date
                    if article.published_at and article.published_at < since_date:
                        continue
                    
                    articles.append(article)
                    count += 1
                    
                except (KeyError, ValueError) as e:
                    logger.warning(f"Failed to parse article: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from EventRegistry")
            return articles
            
        except Exception as e:
            logger.error(f"EventRegistry API error: {e}")
            raise NewsProviderError(f"Failed to fetch articles: {e}") from e
    
    def _parse_article(self, data: dict) -> Article:
        """
        Parse EventRegistry article data into domain Article.
        
        Args:
            data: Raw article data from EventRegistry
            
        Returns:
            Article domain object
            
        Raises:
            ValueError: If required fields are missing
        """
        # Extract required fields
        uri = data.get('uri', '')
        title = data.get('title', '')
        url = data.get('url', '')
        body = data.get('body', '')
        
        if not all([uri, title, url]):
            raise ValueError("Missing required article fields")
        
        # Extract source
        source = "Unknown"
        source_data = data.get('source')
        if isinstance(source_data, dict):
            source = source_data.get('title', source_data.get('uri', 'Unknown'))
        elif isinstance(source_data, str):
            source = source_data
        
        # Parse published date
        published_at = None
        date_str = data.get('dateTime') or data.get('date')
        if date_str:
            try:
                published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse date: {date_str}")
        
        return Article(
            uri=uri,
            title=title,
            url=url,
            source=source,
            body=body,
            published_at=published_at
        )
