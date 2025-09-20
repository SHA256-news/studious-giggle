# Separate Workflows Implementation Summary

## Problem Statement
The original issue reported that:
1. The action workflow to fetch news from EventRegistry and publish tweets via Twitter API was deleted
2. The action workflow to create reports for each published news headline via the Gemini API was not working

## Analysis
After thorough investigation, the actual situation was:
- The main.yml workflow WAS present and contained ALL functionality (EventRegistry + Twitter + Gemini)
- The bot_workflow.yml was disabled to prevent conflicts
- All three components were working in a unified workflow

## Solution Implemented
Created **separate workflows** for better separation of concerns and clarity:

### 1. Fetch and Tweet Workflow (`fetch_and_tweet.yml`)
**Purpose:** Fetch Bitcoin mining news from EventRegistry and post to Twitter
**Schedule:** Every 90 minutes (16 times per day)
**Components:**
- Fetches news from EventRegistry API
- Posts single tweets to Twitter
- Updates `posted_articles.json`
- **Skips Gemini analysis** (handled separately)

**Times:** 00:00, 01:30, 03:00, 04:30, 06:00, 07:30, 09:00, 10:30, 12:00, 13:30, 15:00, 16:30, 18:00, 19:30, 21:00, 22:30

### 2. Generate Reports Workflow (`generate_reports.yml`)
**Purpose:** Generate Gemini AI analysis reports for posted articles
**Schedule:** Runs 15 minutes after the main workflow
**Components:**
- Analyzes recently posted articles with Gemini AI
- Generates comprehensive markdown reports
- Saves reports to `files/reports/` directory
- Commits new reports automatically

**Times:** 00:15, 01:45, 03:15, 04:45, 06:15, 07:45, 09:15, 10:45, 12:15, 13:45, 15:15, 16:45, 18:15, 19:45, 21:15, 22:45

## New Files Created

### Scripts
- `fetch_and_tweet.py` - Entry point for fetch and tweet workflow
- `generate_reports.py` - Standalone Gemini report generator

### Workflows
- `.github/workflows/fetch_and_tweet.yml` - EventRegistry + Twitter workflow
- `.github/workflows/generate_reports.yml` - Gemini AI analysis workflow

### Tests
- `test_workflow_separation.py` - Validates the new separation works correctly

## Changes to Existing Files

### `bot.py`
- Added `skip_gemini_analysis` parameter to constructor
- Modified `_post_article()` to conditionally skip Gemini analysis
- Maintained backward compatibility for existing tests

### Disabled Files
- `.github/workflows/main.yml` → `.github/workflows/main.yml.disabled`

## Key Benefits

### 1. Clear Separation of Concerns
- **Fetch & Tweet:** Focus on news retrieval and social media posting
- **Generate Reports:** Focus on AI analysis and documentation

### 2. Independent Scheduling
- Tweet posting every 90 minutes (respects Twitter rate limits)
- Report generation offset by 15 minutes (ensures articles are available)

### 3. Better Error Handling
- If Gemini API fails, Twitter posting still works
- If Twitter API fails, report generation can still work

### 4. Easier Debugging
- Separate logs for each workflow
- Clear artifact separation (`fetch-and-tweet-logs` vs `gemini-reports-logs`)

### 5. Scalability
- Each workflow can be modified independently
- Different retry strategies for different functions
- Different environment variable requirements

## Environment Variables Required

### Fetch and Tweet Workflow
```yaml
TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
TWITTER_ACCESS_TOKEN_SECRET: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
EVENTREGISTRY_API_KEY: ${{ secrets.EVENTREGISTRY_API_KEY }}
```

### Generate Reports Workflow
```yaml
GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Validation Tests

All existing tests continue to pass:
- ✅ 8/8 pytest tests pass
- ✅ Success scenario test passes
- ✅ Workflow separation test passes
- ✅ Both workflows handle missing API keys gracefully

## Usage

### Manual Triggering
Both workflows support manual triggering via GitHub Actions UI:
- **Fetch and Tweet:** Supports `force_run` parameter
- **Generate Reports:** Can be triggered anytime

### Local Testing
```bash
# Test fetch and tweet (no Gemini)
python fetch_and_tweet.py --diagnose
python fetch_and_tweet.py

# Test report generation
python generate_reports.py

# Test workflow separation
python test_workflow_separation.py
```

## Migration Notes

### From Previous Setup
- All functionality is preserved
- No data loss (posted_articles.json maintained)
- Backward compatibility maintained for existing tests
- Same Twitter rate limiting behavior

### API Key Requirements
- Same API keys required as before
- Gemini API key now only needed for report generation
- Fetch and tweet works without Gemini API key

## Future Enhancements

This separation enables:
- Different scaling strategies for each component
- A/B testing of different posting schedules
- Enhanced report generation features
- Integration with additional AI services
- More sophisticated error recovery

## Summary

✅ **EventRegistry news fetching** - Active in `fetch_and_tweet.yml`
✅ **Twitter posting** - Active in `fetch_and_tweet.yml`  
✅ **Gemini report generation** - Active in `generate_reports.yml`
✅ **Proper scheduling** - 90-minute intervals with 15-minute offset
✅ **Error handling** - Independent failure domains
✅ **Testing** - All tests pass, new validation added