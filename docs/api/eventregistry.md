# EventRegistry Python API Reference

> **CRITICAL**: This is the permanent API reference for EventRegistry. Always reference this during refactoring!

## Installation & Setup

```python
pip install eventregistry

import eventregistry
from eventregistry import *

# Initialize with API key
er = EventRegistry(apiKey="YOUR_API_KEY")
```

## Core Classes

### EventRegistry Class

Main client class for all API operations.

```python
er = EventRegistry(
    apiKey="YOUR_API_KEY",
    verboseOutput=False,  # Set to True for debugging
    allowUseOfArchive=True  # False = last 30 days only
)
```

**Key Methods:**
- `execQuery(query)` - Execute any query object
- `getConceptUri(concept_name)` - Get URI for concept lookup
- `getLocationUri(location_name)` - Get URI for location lookup  
- `getCategoryUri(category_name)` - Get URI for category lookup
- `getSourceUri(source_name)` - Get URI for news source lookup

### QueryArticlesIter Class

**CRITICAL FOR BOT**: Iterator for fetching articles with automatic pagination.

```python
from eventregistry import QueryArticlesIter, QueryItems

# Basic keyword search
q = QueryArticlesIter(
    keywords="bitcoin mining",
    lang="eng"
)

# Advanced query with multiple filters
q = QueryArticlesIter(
    keywords=QueryItems.OR(["bitcoin mining", "BTC mining"]),
    conceptUri=er.getConceptUri("Bitcoin"),
    sourceLocationUri=er.getLocationUri("USA"),
    dateStart=datetime.now() - timedelta(days=1),
    dateEnd=datetime.now(),
    lang="eng",
    dataType=["news"]  # excludes blogs, pr
)

# Execute query
for article in q.execQuery(er, sortBy="date", maxItems=100):
    print(article)
```

**Key Parameters:**
- `keywords` (str|QueryItems) - Search keywords
- `conceptUri` (str|list) - Concept URIs to match
- `sourceUri` (str|list) - Source URIs to include  
- `sourceLocationUri` (str|list) - Source location URIs
- `categoryUri` (str|list) - Category URIs
- `lang` (str|list) - Language codes ("eng", "spa", etc.)
- `dateStart/dateEnd` (datetime) - Date range
- `dataType` (list) - ["news", "blog", "pr"] content types
- `minSentiment/maxSentiment` (float) - Sentiment range (-1 to 1)

**sortBy Options:**
- `"date"` - Most recent first (DEFAULT for bot)
- `"rel"` - Most relevant first
- `"socialScore"` - Most shared on social media

### QueryItems Class

Helper for complex query logic.

```python
# OR logic
keywords=QueryItems.OR(["bitcoin mining", "BTC mining", "cryptocurrency mining"])

# AND logic  
keywords=QueryItems.AND(["bitcoin", "mining"])

# Complex combinations
conceptUri=QueryItems.OR([
    er.getConceptUri("Bitcoin"),
    er.getConceptUri("Cryptocurrency mining")
])
```

### QueryEvents Class

For event-based queries (alternative to articles).

```python
q = QueryEvents(
    keywords="bitcoin mining",
    lang="eng"
)
q.setRequestedResult(RequestEventsInfo(count=50, sortBy="date"))
events = er.execQuery(q)
```

## Article Data Structure

Each article returned contains:

```python
{
    "uri": "unique_article_identifier",
    "title": "Article headline",
    "body": "Full article text",
    "url": "Original article URL",
    "dateTimePub": "2024-01-15T10:30:00Z",  # ISO format
    "source": {
        "title": "Source name",
        "uri": "source_identifier"
    },
    "lang": "eng",
    "sentiment": 0.1,  # -1 to 1 scale
    "concepts": [...],  # Extracted concepts
    "categories": [...],  # Topic categories
    "location": {...},  # Geographic data
    "socialScore": 42  # Social media shares
}
```

## Common Patterns Used in Bot

### 1. Recent Bitcoin Mining Articles

```python
# Fetch last 24 hours of Bitcoin mining news
q = QueryArticlesIter(
    keywords="bitcoin mining",
    dateStart=datetime.now() - timedelta(days=1),
    lang="eng",
    dataType=["news"]  # Exclude blogs/PR
)

articles = []
for article in q.execQuery(er, sortBy="date", maxItems=20):
    articles.append(article)
```

### 2. Filter by Source Quality

```python
# Only get articles from major news sources
quality_sources = [
    er.getSourceUri("Reuters"),
    er.getSourceUri("Bloomberg"),
    er.getSourceUri("CoinDesk")
]

q = QueryArticlesIter(
    keywords="bitcoin mining",
    sourceUri=quality_sources,
    lang="eng"
)
```

### 3. Geographic Filtering

```python
# US-based sources only
q = QueryArticlesIter(
    keywords="bitcoin mining",
    sourceLocationUri=er.getLocationUri("USA"),
    lang="eng"
)
```

### 4. Sentiment Filtering

```python
# Positive sentiment only
q = QueryArticlesIter(
    keywords="bitcoin mining",
    minSentiment=0.1,
    lang="eng"
)
```

## Error Handling

```python
try:
    articles = []
    for article in q.execQuery(er, sortBy="date", maxItems=100):
        articles.append(article)
except Exception as e:
    print(f"EventRegistry error: {e}")
    # Common errors:
    # - Invalid API key
    # - Rate limit exceeded  
    # - Network timeout
    # - Invalid query parameters
```

## Rate Limits & Best Practices

- **Free tier**: Limited requests per day
- **Paid tiers**: Higher limits, archive access
- **Best practices**:
  - Cache results when possible
  - Use specific date ranges to reduce results
  - Filter by language and data type
  - Use maxItems to limit results
  - Handle exceptions gracefully

## Bot Integration Notes

1. **Article Deduplication**: Use `uri` field for unique identification
2. **Date Handling**: Convert `dateTimePub` string to datetime objects
3. **Content Quality**: Check `body` field length and quality
4. **Source Validation**: Verify `source.title` for reliable sources
5. **Language Filtering**: Always specify `lang="eng"` for English content

## API Key Management

```python
# Environment variable (RECOMMENDED)
import os
api_key = os.getenv("EVENTREGISTRY_API_KEY")
er = EventRegistry(apiKey=api_key)

# Direct assignment (for testing only)
er = EventRegistry(apiKey="your-key-here")
```

## Testing & Debugging

```python
# Enable verbose output for debugging
er = EventRegistry(apiKey="your-key", verboseOutput=True)

# Test connection
try:
    test_concept = er.getConceptUri("Bitcoin")
    print(f"Bitcoin concept URI: {test_concept}")
except Exception as e:
    print(f"Connection failed: {e}")
```

---

**Last Updated**: 2025-01-05  
**Package Version**: eventregistry>=9.1
**Documentation Source**: https://github.com/EventRegistry/event-registry-python/wiki