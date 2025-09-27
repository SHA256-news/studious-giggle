# Bitcoin Mining News Twitter Bot

**Elegant, production-ready Twitter bot for Bitcoin mining news with sophisticated rate limiting and comprehensive error handling.**

## ✨ New Elegant Architecture (2024 Refactoring)

This bot has been completely refactored into a **streamlined 3-file architecture** with 84% file reduction while maintaining 100% functionality:

- **`core.py`** (402 lines) - Complete bot engine with all essential functionality
- **`bot.py`** (123 lines) - Main entry point with backward compatibility  
- **`tools.py`** (180 lines) - Unified management interface for all bot operations

### Key Improvements
- **⚡ Sub-second startup** with lazy loading optimizations
- **🏗️ Elegant consolidation** of 8+ modules into clean architecture
- **🔄 Full backward compatibility** with existing tests and workflows
- **🛠️ Unified tools interface** replacing 6+ separate management scripts

## 🚀 Features

- **Smart Bitcoin Mining News**: Fetches relevant articles from EventRegistry (NewsAPI.ai) with intelligent filtering
- **Engaging Tweet Format**: Dynamic prefixes (🚨 BREAKING:, 📢 JUST IN:, ⚡ NEWS:, 🔥 HOT:) with optimized character limits
- **Production-Ready Automation**: Runs every 90 minutes via GitHub Actions with comprehensive error handling
- **Intelligent Deduplication**: Tracks posted articles and manages queue to prevent repeats
- **Progressive Rate Limiting**: Sophisticated cooldown system (2h → 4h → 8h → 24h) with automatic recovery
- **Robust Error Handling**: Graceful failure handling with detailed diagnostics and clear user feedback

## 🛠️ Essential Tools (New Unified Interface)

All management operations now use the elegant `tools.py` interface:

```bash
# Preview next tweet with character count and formatting
python tools.py preview

# View queued articles in clean format
python tools.py queue

# Interactive queue cleaning and management
python tools.py clean

# Comprehensive bot health check and diagnostics
python tools.py diagnose
```

## 🤖 How It Works (Streamlined Process)

1. **Scheduled Execution**: Runs every 90 minutes via GitHub Actions with intelligent interval protection
2. **Smart Article Fetching**: Connects to EventRegistry API with Bitcoin mining keyword filtering
3. **Intelligent Processing**: 
   - Filters out already posted articles using persistent tracking
   - Prioritizes fresh content over stale queued articles
   - Manages queue with FIFO processing and staleness detection
4. **Optimized Posting**: 
   - Posts most recent article immediately
   - Queues older articles for future runs
   - Applies dynamic emoji prefixes and character optimization
5. **Comprehensive Tracking**: Updates `posted_articles.json` with posted URIs and queue state

## ⚙️ Running the Bot

### Quick Start
```bash
# Install dependencies (takes 30-60 seconds - NEVER CANCEL)
pip install -r requirements.txt

# Run comprehensive diagnostics  
python bot.py --diagnose

# Run the bot normally (requires API keys)
python bot.py
```

### Architecture Validation
```bash
# Test new elegant architecture (comprehensive validation)
python test_refactored_architecture.py

# Legacy test compatibility (still works via compatibility layer)
python -m pytest tests/ -v
```


## 🛡️ Rate Limiting & Error Handling

The bot features **production-grade reliability** with multiple layers of protection:

### Intelligent Rate Management
- **Conservative Scheduling**: Maximum 16 runs per day (every 90 minutes) to stay under Twitter API limits
- **Minimum Interval Protection**: Runtime validation prevents runs within 90 minutes of last execution
- **Progressive Cooldowns**: Smart escalation (2h → 4h → 8h → 24h) with automatic recovery
- **Single Retry Strategy**: Conserves daily quota with targeted 5-minute delay retries
- **Precise Timing**: `last_run_time` updates only after successful completion (prevents timing drift)

### Robust Error Recovery
- **Graceful Failure Handling**: Distinguishes between rate limiting, missing articles, and API errors
- **Comprehensive Logging**: Clear status messages for monitoring and debugging
- **Queue Management**: Automatic stale article cleanup and fresh content prioritization
- **Safe Mode**: Diagnostic mode prevents accidental API usage during testing

## 🔧 Troubleshooting Guide

### Primary Issues and Solutions

#### 🚨 Missing API Keys (90% of problems)
**Symptoms:**
- `"Missing required environment variables"`
- `"User is not logged in"`

**Solution:**
```bash
# Quick diagnosis
python bot.py --diagnose

# Or comprehensive check
python tools.py diagnose
```

Set up GitHub repository secrets at **Settings > Secrets and variables > Actions**:
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET`  
- `EVENTREGISTRY_API_KEY`

#### 📭 No New Articles
**Symptoms:**
- `"No new articles to post (all articles were already posted)"`
- `"No articles found from EventRegistry"`

**Normal Behavior:** Bot only posts each article once and tracks posted content.

#### ⏱️ Rate Limiting
**Symptoms:**
- `"Rate limit cooldown active"`
- `"429 Too Many Requests"`

**Automatic Handling:** Bot implements progressive cooldowns and will resume automatically.

### Diagnostic Commands
```bash
# Primary diagnostics (new elegant interface)
python tools.py diagnose

# Legacy compatibility (still works)
python bot.py --diagnose
```

## 🔐 API Configuration

### Required API Keys (GitHub Repository Secrets)

Set these at **Settings > Secrets and variables > Actions**:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `TWITTER_API_KEY` | Twitter API key | ✅ |
| `TWITTER_API_SECRET` | Twitter API secret | ✅ |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | ✅ |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret | ✅ |
| `EVENTREGISTRY_API_KEY` | EventRegistry/NewsAPI.ai API key | ✅ |

### API Key Setup Guide

#### Twitter API Keys
1. Visit [Twitter Developer Portal](https://developer.twitter.com/)
2. Create developer account and new app
3. Generate API keys and access tokens
4. Ensure app has **Read and Write** permissions

#### EventRegistry API Key  
1. Go to [NewsAPI.ai Dashboard](https://newsapi.ai/dashboard)
2. Create account and get API key
3. Verify API key has sufficient quota for daily usage

### Validation
```bash
# Verify all API keys are properly configured
python tools.py diagnose

# Test core functionality without posting
python bot.py --diagnose
```

## 📁 Project Structure (Elegant 3-File Architecture)

```
studious-giggle/
├── 📦 Core Architecture
│   ├── core.py                    # Complete bot engine (Config, Storage, APIs, Processing)
│   ├── bot.py                     # Main entry point with backward compatibility
│   └── tools.py                   # Unified management interface
├── 🧪 Testing & Validation  
│   ├── test_refactored_architecture.py  # New architecture validation
│   ├── tests/                           # Legacy test suite (still works)
│   └── test_*.py                        # Comprehensive test coverage
├── 📋 Data & Configuration
│   ├── requirements.txt                 # Python dependencies (streamlined)
│   ├── posted_articles.json            # Article tracking (auto-generated)
│   └── rate_limit_cooldown.json        # Rate limit state (auto-generated)
├── 🚀 Automation
│   └── .github/workflows/main.yml       # GitHub Actions workflow  
└── 📚 Documentation
    ├── README.md                        # This file
    ├── REFACTORING_SUMMARY.md           # Architecture transformation details
    └── CLEANUP_SUMMARY.md               # File reduction achievements
```

### Architecture Benefits
- **84% File Reduction**: From 47 to 8 Python files with no functionality loss
- **Consolidated Logic**: Single source of truth for all bot operations  
- **Maintainable Code**: Clear separation of concerns and elegant interfaces
- **Backward Compatible**: All existing tests and workflows continue to work
- **Production Ready**: Comprehensive error handling and robust failure recovery

## 📊 Development Workflow

### Complete Development Validation
```bash
# Full validation sequence
pip install -r requirements.txt
python test_refactored_architecture.py    # New architecture tests
python -m pytest tests/ -v                # Legacy compatibility tests
python tools.py diagnose                  # Bot health check
python bot.py --diagnose                  # API validation
```

### Common Development Tasks
```bash
# Preview next tweet
python tools.py preview

# Manage article queue  
python tools.py queue
python tools.py clean

# Architecture validation
python test_refactored_architecture.py

# Legacy test compatibility
python test_bot_fixes.py
python test_success_scenario.py
```

## 📈 Performance & Reliability

### Optimizations
- **⚡ Lightning-Fast Startup**: <1 second with lazy loading
- **🚀 Efficient Runtime**: Single-pass processing, smart caching
- **🛡️ Intelligent Error Recovery**: Continues operation despite transient failures
- **📊 Comprehensive Monitoring**: Detailed logging and execution metrics

### Production Features
- **Automated Scheduling**: GitHub Actions every 90 minutes
- **Rate Limit Compliance**: Smart cooldowns respecting Twitter API limits  
- **Queue Management**: FIFO processing with stale content cleanup
- **Error Resilience**: Graceful handling of API failures and network issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.
