# Fix Verification: Article Re-fetching and Duplicate Publishing

## Problem Statement

The bot had two critical issues:

1. **Re-fetching old articles**: The bot queried for articles from the last 24 hours on every run, instead of fetching articles published since its last successful run. This caused it to process the same articles repeatedly.

2. **Re-publishing duplicate articles**: The content similarity check only compared new articles against other articles in the current queue. It did not check against the history of already posted articles, leading to the re-publication of similar content with different URLs.

## Solution Implemented

### 1. Improved Fetch Logic

**File**: `core.py` - `NewsAPI.fetch_articles()` method

**Changes**:
- Added optional `start_datetime` parameter to `fetch_articles()` method
- Method now accepts a specific datetime to fetch articles from
- Falls back to default `article_lookback_days` config if `start_datetime` not provided
- Bot now uses `last_run_time` from storage to fetch only new articles

**Code**:
```python
def fetch_articles(self, max_articles: int = 20, start_datetime: Optional[datetime] = None) -> List[Article]:
    """Fetch fresh Bitcoin mining articles.
    
    Args:
        max_articles: Maximum number of articles to fetch
        start_datetime: Optional datetime to fetch articles from. If not provided,
                      uses article_lookback_days config setting.
    """
    # Use provided start_datetime or fall back to article_lookback_days
    if start_datetime is None:
        start_datetime = datetime.now(timezone.utc) - timedelta(days=self.config.article_lookback_days)
    
    q = QueryArticlesIter(
        keywords="bitcoin mining",
        dateStart=start_datetime,  # Now uses dynamic datetime
        lang="eng"
    )
```

**Bot Integration** (`BitcoinMiningBot.run()`):
```python
# Use last_run_time if available to fetch only new articles
start_datetime = None
if self.posted_data.get("last_run_time"):
    try:
        last_run_str = self.posted_data["last_run_time"]
        # Parse ISO format datetime string
        if last_run_str.endswith('Z'):
            last_run_str = last_run_str[:-1] + '+00:00'
        start_datetime = datetime.fromisoformat(last_run_str)
        # Ensure timezone aware
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        logger.info(f"Fetching articles published since last run: {start_datetime.isoformat()}")
    except (ValueError, AttributeError) as e:
        logger.warning(f"Could not parse last_run_time, using default lookback: {e}")
        start_datetime = None

articles = self.news.fetch_articles(self.config.max_articles, start_datetime=start_datetime)
```

### 2. Enhanced Deduplication

**File**: `core.py` - `BitcoinMiningBot.run()` method

**Changes**:
- Bot now loads articles from `posted_articles_history` 
- Reconstructs Article objects from history records for content comparison
- Includes historical articles in the deduplication check
- Prevents re-publishing similar content with different URLs

**Code**:
```python
# ENHANCED: Also load posted articles history for deduplication
posted_history = self.posted_data.get("posted_articles_history", [])
for history_item in posted_history:
    try:
        # Reconstruct Article object from history record
        article_dict = {
            "url": history_item.get("url", ""),
            "title": history_item.get("title", ""),
            "body": history_item.get("body_preview", ""),  # Use preview as body
            "source": {"title": history_item.get("source", "")},
            "dateTimePub": history_item.get("date_published")
        }
        existing_articles.append(Article.from_dict(article_dict))
    except (ValueError, KeyError) as e:
        logger.warning(f"Invalid posted history data: {e}")
        continue

logger.info(f"Checking duplicates against {len(existing_articles)} existing articles ({len(queued_articles_data)} queued + {len(posted_history)} posted)")
```

## Test Coverage

Created comprehensive test suite in `tests/test_fetch_and_deduplication.py`:

### Tests Added:
1. ✅ **test_fetch_articles_with_start_datetime** - Verifies parameter acceptance
2. ✅ **test_fetch_articles_default_behavior** - Verifies fallback to default
3. ✅ **test_bot_uses_last_run_time_for_fetch** - Verifies bot uses stored timestamp
4. ✅ **test_deduplication_against_posted_history** - Verifies history checking
5. ✅ **test_deduplication_against_queued_articles** - Verifies queue checking
6. ✅ **test_url_deduplication_still_works** - Verifies URL matching preserved
7. ✅ **test_new_unique_article_not_filtered** - Verifies new articles pass through

### Test Results:
- **7/7 new tests passing** ✅
- **14/14 core tests passing** ✅  
- **3/3 integration tests passing** ✅
- **Total: 24/24 tests passing** ✅

## Verification Results

### Manual Testing Output:

```
1. Testing NewsAPI.fetch_articles with start_datetime parameter...
   ✅ fetch_articles accepts start_datetime parameter

2. Testing bot uses last_run_time from storage...
   ✅ Bot loaded last_run_time: 2025-10-18T16:46:00.015755+00:00

3. Testing content similarity detection...
   Title similarity: 1.00
   Content similarity: 0.88
   Detected as duplicate: True
   ✅ Similar articles correctly detected as duplicates

4. Testing deduplication against posted_articles_history...
   Loaded 1 article(s) from history
   ✅ Bot successfully loads posted_articles_history
   ✅ Successfully reconstructed Article from history

5. Testing URL-based deduplication...
   ✅ Articles with same URL correctly detected as duplicates
```

## Impact

### Before Fix:
- ❌ Bot queries last 24 hours on every run (e.g., if runs at 2pm, fetches from 2pm yesterday)
- ❌ Same articles re-fetched and re-evaluated on every run
- ❌ Similar articles with different URLs can be posted multiple times
- ❌ No protection against duplicate content from different sources

### After Fix:
- ✅ Bot queries from last successful run time (e.g., if last run at 12pm, only fetches articles since 12pm)
- ✅ Only truly new articles are fetched and evaluated
- ✅ Similar content is detected even with different URLs
- ✅ Comprehensive deduplication against all posted history

## Backward Compatibility

All changes maintain full backward compatibility:
- ✅ Default behavior unchanged when `start_datetime` not provided
- ✅ Graceful fallback if `last_run_time` missing or invalid
- ✅ URL-based deduplication still works
- ✅ All existing tests pass without modification
- ✅ No breaking changes to API or data structures

## Code Quality

- ✅ Minimal changes (surgical modifications only)
- ✅ Well-documented with clear comments
- ✅ Proper error handling and logging
- ✅ Type hints maintained
- ✅ Follows existing code style and patterns
- ✅ No new dependencies required

## Summary

The fix successfully addresses both critical issues:

1. **Prevents re-fetching old articles** by using `last_run_time` to query EventRegistry API for only articles published since the last successful run.

2. **Prevents re-publishing duplicates** by checking new articles against the complete history of posted articles, not just the current queue.

The implementation is minimal, well-tested, and maintains full backward compatibility with the existing codebase.
