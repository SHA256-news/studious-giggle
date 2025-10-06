# API Quick Reference Cheat Sheet

> **INSTANT REFERENCE**: Copy-paste ready code snippets for common refactoring operations

## EventRegistry - Quick Patterns

### Basic Article Fetch
```python
from eventregistry import QueryArticlesIter
from datetime import datetime, timedelta

q = QueryArticlesIter(
    keywords="bitcoin mining",
    dateStart=datetime.now() - timedelta(days=1),
    lang="eng"
)

articles = []
for article in q.execQuery(er, sortBy="date", maxItems=20):
    articles.append(article)
```

### Advanced Filtering
```python
# Multiple keywords with OR logic
keywords=QueryItems.OR(["bitcoin mining", "BTC mining", "crypto mining"])

# Date range + location + sentiment
q = QueryArticlesIter(
    keywords="bitcoin mining",
    sourceLocationUri=er.getLocationUri("USA"),
    minSentiment=0.1,
    dateStart=datetime.now() - timedelta(days=1),
    dataType=["news"]  # exclude blogs/PR
)
```

### Article Data Access
```python
# Standard article fields
article = {
    "title": data.get("title", ""),
    "body": data.get("body", ""),
    "url": data.get("url", ""),
    "source": data.get("source", {}).get("title", ""),
    "dateTimePub": data.get("dateTimePub")  # ISO format string
}
```

## Gemini - Quick Patterns

### URL Context Generation
```python
from google.genai import types

config = types.GenerateContentConfig(
    tools=[types.Tool(url_context=types.UrlContext())]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Analyze article at {url} and create headline",
    config=config
)
```

### Headline Generation
```python
def generate_headline(article_url: str) -> str:
    config = types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
        max_output_tokens=100
    )
    
    prompt = f"""
    Create Bitcoin mining headline for: {article_url}
    - 60-80 characters
    - Include specific facts/numbers
    - No emojis or hashtags
    Return only headline text.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    return response.text.strip()[:80]
```

### Summary Generation (Anti-Repetition)
```python
def generate_summary(article_url: str, headline: str) -> str:
    prompt = f"""
    Read article at {article_url} and create 3-point summary.
    Generated Headline: {headline}
    
    CRITICAL: DO NOT repeat headline information.
    - Under 180 characters total
    - Format: "• point"
    - New details only
    """
    
    config = types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())]
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    return process_summary(response.text.strip())
```

## Error Handling Patterns

### EventRegistry Errors
```python
try:
    articles = list(q.execQuery(er, sortBy="date", maxItems=20))
except Exception as e:
    logger.error(f"EventRegistry error: {e}")
    return []  # Return empty list on failure
```

### Gemini Errors
```python
try:
    response = client.models.generate_content(...)
    return response.text.strip()
    
except ValueError as e:
    # API key/auth issues - re-raise
    logger.error(f"Gemini auth error: {e}")
    raise
    
except ConnectionError as e:
    # Network issues - use fallback
    logger.warning(f"Gemini network error: {e}")
    return fallback_content
    
except Exception as e:
    # Other errors - use fallback
    logger.warning(f"Gemini error: {e}")
    return fallback_content
```

## Data Processing Patterns

### Article Validation
```python
def validate_article(data: dict) -> bool:
    """Quick article validation."""
    return (
        data.get("title", "").strip() != "" and
        data.get("url", "").strip() != "" and
        len(data.get("body", "")) > 100  # Minimum content
    )
```

### Date Processing
```python
def parse_article_date(date_str: str) -> Optional[datetime]:
    """Parse EventRegistry date format."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None
```

### Text Cleaning
```python
def clean_text(text: str) -> str:
    """Clean text for Twitter."""
    # Remove emojis
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+")
    text = emoji_pattern.sub('', text)
    
    # Clean whitespace
    return re.sub(r'\s+', ' ', text).strip()
```

## Common Configurations

### EventRegistry Client
```python
import eventregistry
er = eventregistry.EventRegistry(
    apiKey=os.getenv("EVENTREGISTRY_API_KEY"),
    verboseOutput=False
)
```

### Gemini Client
```python
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
```

### Twitter Threading Logic
```python
def create_thread(headline: str, summary: str, url: str) -> list[str]:
    """Smart Twitter thread creation."""
    combined = f"{headline}\n\n{summary}"
    
    if len(combined) <= 280:
        return [combined, url]  # Combined + URL
    else:
        thread = [headline]
        if len(summary) <= 280:
            thread.append(summary)
        else:
            thread.append(summary[:277] + "...")
        thread.append(url)
        return thread
```

## Bitcoin Mining Filter Pattern
```python
def is_bitcoin_mining_article(article: dict) -> bool:
    """Enhanced Bitcoin mining validation."""
    text = f"{article.get('title', '')} {article.get('body', '')}".lower()
    title = article.get('title', '').lower()
    
    # Exclude non-mining topics
    excluded_topics = ["gold", "treasury", "stablecoin", "tokenized", "trading"]
    if any(topic in title for topic in excluded_topics):
        return False
    
    # Require Bitcoin + mining terms
    bitcoin_terms = ["bitcoin", "btc"]
    mining_terms = ["mining", "miner", "miners"]
    
    has_bitcoin = any(term in text for term in bitcoin_terms)
    has_mining = any(term in text for term in mining_terms)
    
    return has_bitcoin and has_mining
```

## Debugging Helpers

### Test API Connections
```python
def test_apis():
    """Quick API connection test."""
    try:
        # Test EventRegistry
        test_concept = er.getConceptUri("Bitcoin")
        print(f"✅ EventRegistry: {test_concept}")
        
        # Test Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'OK'"
        )
        print(f"✅ Gemini: {response.text}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
```

### Response Inspection
```python
def inspect_article(article: dict):
    """Debug article data structure."""
    print(f"Title: {article.get('title', 'N/A')}")
    print(f"URL: {article.get('url', 'N/A')}")
    print(f"Source: {article.get('source', {}).get('title', 'N/A')}")
    print(f"Date: {article.get('dateTimePub', 'N/A')}")
    print(f"Body length: {len(article.get('body', ''))}")
```

---

**Usage**: Reference this file during any refactoring that involves API calls. All patterns are tested and production-ready.