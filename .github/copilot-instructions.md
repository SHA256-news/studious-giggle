# Bitcoin Mining News Twitter Bot

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

Bitcoin Mining News Twitter Bot is a Python application that automatically fetches Bitcoin mining news from EventRegistry API and posts them to Twitter/X as threaded tweets. It runs every 90 minutes via GitHub Actions with sophisticated rate limiting and error handling.

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt`
- Install testing framework: `pip install pytest`
- NEVER CANCEL: Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.

### Build and Test
- Run all tests: `python -m pytest tests/ -v` -- takes <1 second. NEVER CANCEL.
- Run standalone tests:
  - `python test_bot_fixes.py` -- takes <1 second
  - `python test_daily_rate_limits.py` -- takes <1 second  
  - `python test_success_scenario.py` -- takes <1 second
  - `python test_rate_limit_cooldown.py` -- takes 5+ minutes (includes 5-minute delay test). NEVER CANCEL. Set timeout to 10+ minutes.
- All tests complete in under 1 second total - this is normal and expected

### Run the Application
- **Diagnose issues**: `python bot.py --diagnose` -- takes <5 seconds
- **Run bot normally**: `python bot.py` -- will fail without API keys (expected)
- **Run diagnostics script**: `python diagnose_bot.py` -- takes <5 seconds

## Required API Keys Setup

The bot requires these GitHub repository secrets:
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token  
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret
- `EVENTREGISTRY_API_KEY` - EventRegistry/NewsAPI.ai API key

Without these keys, the bot will show clear error messages explaining what's missing.

## Validation Scenarios

### CRITICAL: Always Test These Scenarios After Changes

**Diagnostic Validation**:
- Run `python bot.py --diagnose` and verify it identifies missing API keys correctly
- Check that it shows helpful setup instructions
- Verify posted articles file is readable

**Test Suite Validation**:  
- Run `python -m pytest tests/ -v` and verify all 4 tests pass
- Run `python test_bot_fixes.py` and verify all bug fix scenarios work
- Run `python test_daily_rate_limits.py` and verify progressive cooldown logic
- Run `python test_success_scenario.py` and verify complete bot workflow
- Run `python test_rate_limit_cooldown.py` and verify rate limiting (NEVER CANCEL: takes 5+ minutes)

**Error Handling Validation**:
- Run `python bot.py` without API keys and verify clear error messages
- Check that the bot exits gracefully with helpful instructions

**Complete Development Workflow Validation**:
```bash
# Full validation sequence - run all commands to verify setup
pip install -r requirements.txt
pip install pytest
python -m pytest tests/ -v
python test_bot_fixes.py
python test_daily_rate_limits.py  
python test_success_scenario.py
python bot.py --diagnose
python diagnose_bot.py
```

### Manual Testing Without API Keys
Since this repository doesn't have API keys configured by default:
- Always run diagnostic commands to verify the bot detects missing configuration
- Test that error messages are clear and actionable
- Verify that all tests pass (they use mocked APIs)

## Common Tasks

### Code Locations
- **Main bot logic**: `bot.py` (class `BitcoinMiningNewsBot`)
- **Diagnostic tools**: `diagnose_bot.py` and `bot.py --diagnose`
- **Test suite**: `tests/` directory + standalone test files
- **Rate limiting logic**: `bot.py` methods `_set_rate_limit_cooldown()` and `_is_rate_limit_cooldown_active()`
- **GitHub Actions**: `.github/workflows/main.yml`

### Key Dependencies
- `tweepy>=4.14.0` - Twitter API client
- `eventregistry>=9.1` - News article fetching
- `pytest` - Testing framework (install separately)

### Important Files
- `requirements.txt` - Python dependencies
- `posted_articles.json` - Tracks posted articles to prevent duplicates  
- `rate_limit_cooldown.json` - Manages progressive rate limiting
- `README.md` - User documentation
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide

## Timing Expectations and Cancellation Warnings

### NEVER CANCEL these operations:
- **Dependency installation**: 30-60 seconds (set timeout to 120+ seconds)
- **Test execution**: Most tests complete in <1 second, but `test_rate_limit_cooldown.py` takes 5+ minutes (set timeout to 10+ minutes)
- **Bot diagnostics**: <5 seconds
- **Bot execution**: <10 seconds when working correctly

### GitHub Actions Timing:
- **Scheduled runs**: Every 90 minutes (16 times per day max)
- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)
- **Twitter API limits**: 17 requests per 24 hours

## Error Patterns and Solutions

### Missing API Keys (90% of issues)
**Symptoms**: "Missing required environment variables", "User is not logged in"
**Solution**: Set up GitHub repository secrets as documented above

### Rate Limiting  
**Symptoms**: "429 Too Many Requests", "Rate limit cooldown active"
**Solution**: Bot handles this automatically with progressive cooldowns

### No Articles Found
**Symptoms**: "No articles found from EventRegistry"  
**Solution**: Normal when no Bitcoin mining news in last 24 hours

### All Articles Posted
**Symptoms**: "No new articles to post (all articles were already posted)"
**Solution**: Normal behavior - bot tracks posted articles

## CI/GitHub Actions

The bot runs automatically via GitHub Actions:
- **Workflow file**: `.github/workflows/main.yml`
- **Python version**: 3.10 (but works with 3.12+)
- **Triggers**: Scheduled (every 90 minutes) + manual dispatch
- **Dependencies**: Installs from `requirements.txt`
- **Commits**: Updates `posted_articles.json` after successful runs

## Development Workflow

### Always run these before committing:
1. `python -m pytest tests/ -v` - Run test suite
2. `python test_bot_fixes.py` - Test bug fixes  
3. `python test_daily_rate_limits.py` - Test rate limiting
4. `python bot.py --diagnose` - Test diagnostics

### When modifying rate limiting logic:
- Always test with `python test_daily_rate_limits.py`
- Verify progressive cooldown behavior (2h → 4h → 8h → 24h)
- Check cooldown file creation in `rate_limit_cooldown.json`

### When modifying posting logic:
- Test with `python test_success_scenario.py` 
- Verify tweet threading behavior
- Check article deduplication logic

### When adding new features:
- Add tests following existing patterns in `tests/` directory
- Use mocked API calls (see `tests/test_fetch_articles.py` for examples)
- Test both success and failure scenarios

## Repository Structure Reference

```
.
├── .github/
│   └── workflows/main.yml          # GitHub Actions workflow
├── tests/                          # Pytest test suite
│   ├── test_fetch_articles.py     # Core posting logic tests
│   └── test_article_priority.py   # Article prioritization tests
├── bot.py                          # Main bot application
├── diagnose_bot.py                 # Diagnostic script
├── test_*.py                       # Standalone test files
├── requirements.txt                # Python dependencies
├── posted_articles.json            # Article tracking (auto-generated)
├── rate_limit_cooldown.json        # Rate limit state (auto-generated)
├── README.md                       # User documentation
└── TROUBLESHOOTING.md              # Detailed troubleshooting
```

This is a production-ready Twitter bot with robust error handling, rate limiting, and comprehensive testing. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.