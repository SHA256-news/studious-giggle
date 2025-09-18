# Bitcoin Mining News Twitter Bot

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

Bootstrap and test the repository:
- `pip install -r requirements.txt` -- takes under 1 second. NEVER CANCEL.
- `python -m pytest tests/ -v` -- takes under 1 second. NEVER CANCEL. Run this to verify core functionality.
- `python test_success_scenario.py` -- takes under 1 second. NEVER CANCEL. Demonstrates complete working bot scenario.
- `python test_bot_fixes.py` -- takes under 1 second. NEVER CANCEL. Tests edge cases and error handling.
- `python diagnose_bot.py` -- takes under 1 second. NEVER CANCEL. Diagnoses configuration and API issues.

Run the bot:
- Production: `python bot.py` -- requires API keys as environment variables
- Diagnostics: `python bot.py --diagnose` -- same as `python diagnose_bot.py`
- Safe mode: Initialize bot with `BitcoinMiningNewsBot(safe_mode=True)` for testing without API calls

## Validation

ALWAYS run through this complete validation sequence after making changes:
- Run all tests: `python -m pytest tests/ -v`
- Test success scenario: `python test_success_scenario.py` 
- Test error handling: `python test_bot_fixes.py`
- Run diagnostics: `python diagnose_bot.py`
- MANUAL VALIDATION: Verify bot can be imported and initialized in safe mode without errors

ALWAYS validate that the bot handles these scenarios correctly:
- Missing API keys (should show clear error message with setup instructions)
- Article processing with missing/invalid data (title, URI, URL)
- Twitter API failures (should gracefully handle partial failures)
- Rate limiting (should implement progressive cooldowns)
- Already posted articles (should skip duplicates)

## Environment Setup

The bot requires these exact environment variables (usually set as GitHub repository secrets):
- `TWITTER_API_KEY` -- Twitter API key from developer.twitter.com
- `TWITTER_API_SECRET` -- Twitter API secret key
- `TWITTER_ACCESS_TOKEN` -- Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET` -- Twitter access token secret
- `EVENTREGISTRY_API_KEY` -- EventRegistry API key from newsapi.ai

Without these variables, the bot will exit with a clear error message explaining how to set them up.

## Common Tasks

### Repository Structure
```
/home/runner/work/studious-giggle/studious-giggle/
├── .github/workflows/main.yml     # GitHub Actions workflow (runs every 90 minutes)
├── bot.py                         # Main bot application
├── diagnose_bot.py               # Diagnostic script
├── requirements.txt              # Python dependencies (tweepy, eventregistry)
├── posted_articles.json         # Tracks posted articles to avoid duplicates
├── test_*.py                     # Various test scenarios
├── tests/                        # Pytest test suite
│   ├── test_fetch_articles.py
│   └── test_article_priority.py
├── README.md                     # User documentation
├── TROUBLESHOOTING.md           # Troubleshooting guide
└── SOLUTION_SUMMARY.md          # Summary of common issues
```

### Key Python Dependencies
- `tweepy>=4.14.0` -- Twitter API client
- `eventregistry>=9.1` -- EventRegistry/NewsAPI.ai client

### Main Bot Features
- Fetches Bitcoin mining news from EventRegistry API
- Posts tweets as threads (main tweet + reply with link)
- Posts only 1 article per run to avoid spam
- Tracks posted articles in `posted_articles.json`
- Implements progressive rate limiting cooldowns (2h → 4h → 8h → 24h)
- Runs via GitHub Actions every 90 minutes
- Conservative approach: stays under Twitter's 17 requests per 24 hours limit

### Testing and Validation Commands
```bash
# Install dependencies (< 1 second)
pip install -r requirements.txt

# Run core test suite (< 1 second)
python -m pytest tests/ -v

# Test complete success scenario (< 1 second)
python test_success_scenario.py

# Test error handling and edge cases (< 1 second)  
python test_bot_fixes.py

# Run comprehensive diagnostics (< 1 second)
python diagnose_bot.py

# Test bot without API calls
python -c "from bot import BitcoinMiningNewsBot; bot = BitcoinMiningNewsBot(safe_mode=True); print('✅ Bot initializes correctly')"
```

### What Success Looks Like
When the bot works correctly with API keys configured, logs will show:
```
Starting Bitcoin Mining News Bot
Fetching Bitcoin mining articles...
Found 3 articles about Bitcoin mining
Found 3 total articles
Posted article: [Article Title]...
Successfully posted 1 new article
```

### What Failure Looks Like
Most common failure (missing API keys):
```
🚨 CONFIGURATION ERROR: Missing API Keys
The bot cannot run without the required API keys.
To fix this issue:
1. Go to your GitHub repository settings
2. Navigate to Settings > Secrets and variables > Actions
3. Add the following repository secrets:
   • TWITTER_API_KEY
   • TWITTER_API_SECRET
   • TWITTER_ACCESS_TOKEN
   • TWITTER_ACCESS_TOKEN_SECRET
   • EVENTREGISTRY_API_KEY
```

### GitHub Actions Workflow
- File: `.github/workflows/main.yml`
- Schedule: Every 90 minutes (16 times per day max)
- Respects Twitter's 17 requests per 24 hours rate limit
- Auto-commits updated `posted_articles.json`
- Can be triggered manually via GitHub Actions UI

### Rate Limiting Behavior
- Uses progressive cooldowns when rate limited
- Creates `rate_limit_cooldown.json` when hitting limits
- Cooldown periods: 2h → 4h → 8h → 24h (max)
- Automatically clears expired cooldowns
- Conservative scheduling to prevent limit violations

### Troubleshooting Priority
1. **Missing API Keys** (90% of issues) -- Run `python diagnose_bot.py`
2. **All Articles Already Posted** (normal behavior) -- Check `posted_articles.json`
3. **Rate Limiting** (expected) -- Wait for cooldown period
4. **No Recent Articles** (external dependency) -- EventRegistry API issue
5. **Twitter API Issues** (external) -- Verify account status and API access

### Code Navigation
- **Main bot logic**: `bot.py` class `BitcoinMiningNewsBot`
- **API initialization**: `_init_twitter_client()` and `_init_eventregistry_client()` methods
- **Article fetching**: `fetch_articles()` method
- **Tweet posting**: `post_to_twitter()` method
- **Rate limiting**: `_is_rate_limit_cooldown_active()` and `_set_rate_limit_cooldown()` methods
- **Diagnostics**: `diagnose_bot.py` standalone script

### Making Changes
- ALWAYS test with `python test_success_scenario.py` after changes
- ALWAYS run the full test suite: `python -m pytest tests/ -v`
- Use safe mode for testing: `BitcoinMiningNewsBot(safe_mode=True)`
- The bot handles missing data gracefully -- test edge cases with `python test_bot_fixes.py`
- Changes to posting logic should be tested with mock Twitter API calls
- Rate limiting changes should be tested with `test_rate_limit_cooldown.py`

### File Purposes
- `bot.py` -- Main application with all bot logic
- `diagnose_bot.py` -- Diagnostic tool for troubleshooting
- `test_success_scenario.py` -- Complete working scenario demonstration
- `test_bot_fixes.py` -- Edge case and error handling tests
- `test_rate_limit_cooldown.py` -- Rate limiting functionality tests
- `posted_articles.json` -- Persistent storage of posted article URIs
- `rate_limit_cooldown.json` -- Temporary file created during rate limiting

This bot is production-ready and handles all common failure scenarios gracefully. The diagnostic tools will identify any configuration issues immediately.