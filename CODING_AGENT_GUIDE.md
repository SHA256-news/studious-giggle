# Coding Agent Quick Start Guide

## Repository Overview

This is a **Bitcoin Mining News Twitter Bot** that automatically fetches and posts Bitcoin mining news to Twitter/X every 90 minutes using GitHub Actions.

## Quick Architecture Summary

### Core Files (Must Know)
- **`bot.py`** - Main bot logic and orchestration
- **`utils.py`** - Utilities (file management, time checks, text processing)
- **`api_clients.py`** - Twitter, EventRegistry, and Gemini API clients
- **`tweet_poster.py`** - Tweet posting logic with retry handling
- **`config.py`** - Configuration constants and environment setup

### Key Data Files
- **`posted_articles.json`** - Tracks posted articles and queued content
- **`rate_limit_cooldown.json`** - Manages API rate limiting

### GitHub Actions
- **`.github/workflows/main.yml`** - Active workflow (runs every 90 minutes)
- **`.github/workflows/fetch_and_tweet.yml.disabled`** - Disabled duplicate workflow

## Development Workflow

### 1. Setup and Testing
```bash
# Install dependencies (takes 30-60 seconds - NEVER CANCEL)
pip install -r requirements.txt
pip install pytest

# Run all tests (takes <2 seconds each)
python -m pytest tests/ -v
python test_bot_fixes.py
python test_daily_rate_limits.py
python test_minimum_interval.py

# Diagnose issues
python bot.py --diagnose
python diagnose_bot.py
```

### 2. Key Test Files
- **`tests/`** - Main pytest suite (13 tests)
- **`test_bot_fixes.py`** - Bug fix validations
- **`test_daily_rate_limits.py`** - Rate limiting logic
- **`test_minimum_interval.py`** - 90-minute interval enforcement
- **`test_rate_limit_cooldown.py`** - Extended cooldown tests (5+ minutes)

### 3. Common Tasks

#### API Keys Missing (90% of issues)
```bash
python bot.py --diagnose  # Shows missing environment variables
```
**Expected**: Bot shows clear error messages about missing GitHub repository secrets.

#### Rate Limiting Issues
- Progressive cooldowns: 2h → 4h (simplified from complex system)
- Daily limit: 17 requests per 24 hours
- Minimum interval: 90 minutes between runs

#### Queue Management
```bash
python show_queued_tweets.py  # View queued articles
python clean_queue.py        # Clean unwanted content
```

## Architecture Patterns

### 1. Error Handling
- **Graceful degradation**: Bot continues with reduced functionality
- **Clear error messages**: All failures have human-readable explanations
- **Rate limit awareness**: Automatic cooldowns prevent API violations

### 2. File Management
- **Atomic operations**: JSON files updated atomically
- **Backup systems**: Multiple backup files maintained
- **Auto-migration**: Files auto-upgrade to new formats

### 3. Time Management
- **90-minute minimum interval**: Prevents rapid consecutive runs
- **Last run tracking**: Only updated after successful completion
- **UTC handling**: All timestamps use ISO format

## Critical Logic Points

### 1. Timing Bug (Recently Fixed)
**Problem**: `last_run_time` was updated during intermediate saves
**Solution**: Now only updates after successful bot completion
```python
# CORRECT - Only update on success
FileManager.save_posted_articles(data, update_last_run_time=True)

# INCORRECT - Updates during intermediate saves  
FileManager.save_posted_articles(data)  # old behavior
```

### 2. Rate Limiting Logic
```python
# Simplified cooldown system
RATE_LIMIT_INITIAL_HOURS = 2    # First rate limit
RATE_LIMIT_SUBSEQUENT_HOURS = 4 # Subsequent rate limits (max)
```

### 3. Article Prioritization
1. **New articles** always prioritized over queued content
2. **Most recent first** within new articles
3. **FIFO** for queued articles (oldest first)

## Debugging Guide

### Common Issues and Solutions

#### 1. "No tweets posted but GitHub Actions succeed"
```bash
python bot.py --diagnose
```
**Likely cause**: Missing API keys (intended behavior)

#### 2. Rate limiting errors
```bash
# Check current cooldown status
ls -la rate_limit_cooldown.json
python debug_schedule.py
```

#### 3. Queue problems
```bash
# View queue status
python show_queued_tweets.py
python debug_queue.py
```

#### 4. Image functionality issues
```bash
# Test image processing
python demo_image_functionality.py
python test_image_functionality.py
```

## Code Quality Standards

### 1. Testing Requirements
- **All changes must pass existing tests**
- **New features need corresponding tests**
- **Rate limit tests take 5+ minutes** (never cancel)

### 2. Error Handling
- Use specific exception types, not bare `except:`
- Always log errors with context
- Provide actionable error messages

### 3. Configuration
- Store constants in `config.py`
- Use environment variables for secrets
- Document all configuration options

## API Integration

### 1. Twitter API
- **Rate limit**: 17 requests per 24 hours
- **Retry policy**: 1 retry with 5-minute delay
- **Threading**: Automatic reply tweets for articles with URLs

### 2. EventRegistry API
- **Source**: NewsAPI.ai/EventRegistry
- **Keywords**: Bitcoin mining specific terms
- **Lookback**: 24 hours for fresh content

### 3. Gemini AI (Optional)
- **Purpose**: Enhanced tweet headlines
- **Fallback**: Standard prefixes if unavailable
- **Configuration**: `skip_gemini_analysis` parameter

## File Structure Reference

```
├── .github/workflows/
│   ├── main.yml                    # Active workflow
│   └── fetch_and_tweet.yml.disabled
├── tests/                          # Pytest test suite  
├── bot.py                          # Main application
├── utils.py                        # Core utilities
├── api_clients.py                  # API integrations
├── tweet_poster.py                 # Tweet posting logic
├── config.py                       # Configuration
├── diagnose_bot.py                 # Diagnostic tools
├── posted_articles.json            # Article tracking
└── requirements.txt                # Dependencies
```

## Security Considerations

### 1. API Keys
- **Never commit secrets to code**
- **Use GitHub repository secrets**
- **Validate environment variables on startup**

### 2. Rate Limiting
- **Respect API limits strictly**  
- **Use progressive cooldowns**
- **Log all rate limit encounters**

## Performance Notes

### 1. Timing Expectations
- **Dependency installation**: 30-60 seconds
- **Test execution**: <2 seconds (except cooldown tests)
- **Bot execution**: <10 seconds typical
- **Rate limit cooldown tests**: 5+ minutes

### 2. Resource Usage
- **Memory**: Minimal (< 100MB typical)
- **Network**: Conservative API usage
- **Storage**: JSON files + image cache

## Recent Changes and Fixes

### September 2024 Major Fixes
1. **Workflow Configuration**: Fixed duplicate workflows
2. **Timing Logic**: Fixed `last_run_time` update behavior  
3. **Logging Consistency**: Added proper logging to fetch_and_tweet.py
4. **Gemini Analysis**: Fixed incorrect skip_gemini_analysis flag
5. **Dead Code**: Removed unused bot_original.py

## Need Help?

### 1. Start with Diagnostics
```bash
python bot.py --diagnose
python diagnose_bot.py
```

### 2. Check Documentation
- `README.md` - User-facing documentation
- `TROUBLESHOOTING.md` - Common issues and solutions
- `*_SUMMARY.md` files - Implementation details

### 3. Run Tests for Verification
```bash
# Quick validation
python test_bot_fixes.py

# Full test suite  
python -m pytest tests/ -v
```

The bot is production-ready with comprehensive error handling, rate limiting, and diagnostic tools. Focus on understanding the timing logic and rate limiting as these are the most complex parts of the system.