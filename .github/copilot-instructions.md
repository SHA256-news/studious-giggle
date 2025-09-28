# Bitcoin Mining News Twitter Bot

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

Bitcoin Mining News Twitter Bot is a Python application that automatically fetches Bitcoin mining news from EventRegistry API and posts them to Twitter/X as AI-enhanced threads with Gemini-generated headlines and summaries. It runs every 90 minutes via GitHub Actions with sophisticated rate limiting, queue management, and comprehensive error handling.

## Elegant Architecture Overview

The bot now uses an **elegant, consolidated architecture** with clear separation of concerns:

- **`core.py`**: Complete core functionality (Config, Storage, API clients, GeminiClient, TimeManager, TextProcessor)
- **`bot.py`**: Main entry point with backward compatibility layer
- **`tools.py`**: Essential management tools (preview, queue, clean, diagnose)
- **`tests/test_bot.py`**: Core functionality tests (9 tests)
- **`tests/test_integration.py`**: Integration workflow tests (3 tests)

### Key Architectural Improvements
- **📉 Reduced Complexity**: Consolidated 47+ files into 5 elegant modules (89% file reduction)
- **🚀 Enhanced Performance**: Lazy loading, optimized imports, sub-second startup
- **🧹 Eliminated Redundancy**: Removed duplicate code and unnecessary abstractions  
- **📚 Clean Interfaces**: Simple, readable, maintainable code structure
- **🛡️ Robust Error Handling**: Comprehensive validation and graceful failure handling

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt`
- NEVER CANCEL: Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.

### Build and Test
- **Core tests**: `python tests/test_bot.py` -- comprehensive validation (9 tests)
- **Integration tests**: `python tests/test_integration.py` -- workflow validation (3 tests)
- **Bot diagnostics**: `python bot.py --diagnose` -- takes <3 seconds (optimized)
- **All tests organized**: All test files now in `tests/` directory for clean structure

### Essential Tools (New Consolidated Interface)
- **Preview next thread**: `python tools.py preview` -- shows complete thread structure with character counts
- **Simple queue view**: `python tools.py queue` -- clean list of queued articles  
- **Clean queue**: `python tools.py clean` -- interactive removal of unwanted content
- **Full diagnostics**: `python tools.py diagnose` -- comprehensive bot health check
- **Test live APIs**: `python tools.py test` -- test EventRegistry & Gemini APIs without posting (requires API keys)

### Run the Application
- **Diagnose issues**: `python bot.py --diagnose` -- takes <3 seconds (optimized)
- **Run bot normally**: `python bot.py` -- will fail without API keys (expected)

## Core Features (Simplified & Elegant)

### Smart Tweet Generation
- **AI-enhanced threads**: Multi-tweet structure with Gemini-generated headlines and summaries
- **Native URL context**: Gemini 2.0 Flash Exp with direct article content access via Google's servers
- **Anti-repetition intelligence**: Headlines and summaries complement each other, zero duplicate information
- **Enhanced AI prompts**: Specific examples and instructions for quality content generation
- **Intelligent fallback**: 2-tweet threads (headline → URL) when Gemini unavailable
- **Emoji-free prefixes**: Professional text prefixes (BREAKING:, JUST IN:, NEWS:, HOT:)
- **Thread structure**: With Gemini: Headline → 3-point summary → URL | Without: Headline → URL
- **Character limit compliance**: Perfect Twitter threading with proper reply chaining
- **Content deduplication**: Tracks posted articles to prevent repeats

### Technical Implementation Details

**Gemini URL Context Implementation**:
- Uses `tools=[{"url_context": {}}]` parameter in `generate_content()` calls
- Gemini 2.0 Flash Exp model with native URL content fetching
- Comprehensive fallback system: URL context → EventRegistry content → generic fallback
- URL context metadata logging for debugging and validation
- Two-tier processing: `_process_headline_response()` and `_process_summary_response()` methods

**Anti-Repetition Logic Flow**:
1. Generate headline first using URL context
2. Pass headline to summary generation to avoid duplication
3. Summary prompt explicitly includes headline and instructs "DO NOT REPEAT"
4. Enhanced prompts with specific examples of good/bad complementary content
5. Result: Maximum information density with zero redundancy

**Content Quality Enhancements**:
- Specific character limits: Headlines 60-80 chars, summaries <180 chars
- Professional prefixes instead of emoji decorations
- Action-oriented language with specific facts/numbers when available
- Multi-level validation and text processing for consistency

### Robust Article Management
- **Bitcoin-focused filtering**: Advanced keyword matching for relevant content
- **Smart queueing**: Multiple articles queued, posted one at a time
- **Time-based validation**: Article freshness and staleness detection
- **Queue management**: Interactive tools for preview, editing, and cleaning

### Production-Ready Reliability
- **Rate limit handling**: Progressive cooldowns with intelligent recovery
- **Error resilience**: Graceful failure handling with detailed diagnostics
- **Data persistence**: JSON-based storage with atomic operations
- **Minimum interval enforcement**: Respects Twitter API daily limits

### Elegant Performance Optimizations

**⚡ Lightning-Fast Startup (< 1 second)**
- **Lazy initialization**: API clients created only when needed
- **Streamlined imports**: No heavy dependencies during startup
- **Optimized data structures**: Efficient in-memory processing

**🚀 Efficient Runtime**
- **Single-pass processing**: Minimized API calls and file operations
- **Smart caching**: Reuses loaded data throughout execution
- **Intelligent error recovery**: Continues operation despite transient failures

## Required API Keys Setup

The bot requires these GitHub repository secrets:
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token  
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret
- `EVENTREGISTRY_API_KEY` - EventRegistry/NewsAPI.ai API key
- `GEMINI_API_KEY` - Google Gemini API key (Gemini 2.0 Flash Exp with native URL context for AI headlines and summaries)

**Note**: With Gemini API key, the bot generates AI-enhanced multi-tweet threads using advanced URL context and anti-repetition systems. Without it, it falls back to clean 2-tweet threads (headline → URL).

### Advanced AI Content Generation

**Native URL Context (Latest Enhancement)**:
- Uses Gemini 2.0 Flash Exp model with built-in URL context tool
- Google's servers fetch article content directly (no manual web scraping)
- Eliminates bot detection and content extraction issues
- Enhanced content quality with full article access
- URL context metadata logging for debugging

**Anti-Repetition System**:
- Headlines generated first, then passed to summary generation
- Summary explicitly instructed to avoid repeating headline information
- Enhanced prompts with specific do/don't examples
- Results in complementary content: headline focuses on main story, summary provides additional details
- Example: Headline "Marathon Digital Deploys 5,000 New Miners" → Summary "Located in West Texas • Q2 2024 start • 8-month ROI target"

Without these keys, the bot will show clear error messages explaining what's missing.

## Validation Scenarios

### CRITICAL: Always Test These Scenarios After Changes

**Diagnostic Validation**:
- Run `python bot.py --diagnose` and verify it identifies missing API keys correctly
- Check that it shows helpful setup instructions
- Verify posted articles file is readable

### Test Suite Validation**:  
- Run `python tests/test_bot.py` and verify core bot functionality (9 tests)
- Run `python tests/test_integration.py` and verify integration workflows (3 tests)
- **Streamlined testing**: Only 2 test files for elegant architecture

**Error Handling Validation**:
- Run `python bot.py` without API keys and verify clear error messages
- Check that the bot exits gracefully with helpful instructions

**Complete Development Workflow Validation**:
```bash
# Streamlined validation sequence - elegant 2-test architecture
pip install -r requirements.txt
python tests/test_bot.py          # Core functionality tests (8+ tests)
python tests/test_integration.py  # Integration workflow tests (2+ tests)  
python bot.py --diagnose
python tools.py diagnose
```

### Manual Testing Without API Keys
Since this repository doesn't have API keys configured by default:
- Always run diagnostic commands to verify the bot detects missing configuration
- Test that error messages are clear and actionable
- Verify that all tests pass (they use mocked APIs)

## Common Tasks

### Code Locations (Elegantly Simplified)
- **Core functionality**: `core.py` (complete bot engine: Config, Storage, API clients, processing)
- **Main entry point**: `bot.py` (execution + backward compatibility layer)
- **Management tools**: `tools.py` (preview, queue management, diagnostics)
- **Core tests**: `tests/test_bot.py` (comprehensive core tests - 9 tests)
- **Integration tests**: `tests/test_integration.py` (streamlined integration tests - 3 tests)
- **GitHub Actions**: `.github/workflows/main.yml`

**Removed complexity**: Eliminated `api_clients.py`, `utils.py`, `config.py`, `tweet_poster.py`, `gemini_client.py`, image modules, and various diagnostic scripts - all consolidated into elegant core architecture.

### Key Dependencies (Core)
- `tweepy>=4.14.0` - Twitter API client  
- `eventregistry>=9.1` - News article fetching
- `google-generativeai>=0.8.0` - Gemini 2.0 Flash Exp with native URL context
- `beautifulsoup4>=4.12.0` - HTML parsing for fallback content extraction
- `newspaper3k>=0.2.8` - Article extraction fallback when URL context unavailable
- **Note**: All dependencies are required for full functionality including advanced AI content generation

### Important Files (Simplified)
- `requirements.txt` - Python dependencies (streamlined)
- `posted_articles.json` - Tracks posted articles and queue
- `rate_limit_cooldown.json` - Manages rate limiting state
- `README.md` - Comprehensive user documentation

**Removed files**: Image-related configs and directories eliminated for elegant simplicity

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

The bot includes two GitHub Actions workflows:

### Main Bot Workflow (`.github/workflows/main.yml`)
- **Schedule**: Runs every 90 minutes automatically
- **Purpose**: Fetches Bitcoin mining articles and posts Twitter threads
- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)
- **Python version**: 3.10 (but works with 3.12+)
- **Dependencies**: Installs from `requirements.txt`
- **Commits**: Updates `posted_articles.json` after successful runs

### Test & Preview Workflow (`.github/workflows/test-preview.yml`)
- **Trigger**: Manual dispatch only (workflow_dispatch)
- **Purpose**: Test EventRegistry & Gemini APIs without posting to Twitter
- **Output**: Creates GitHub issue with complete thread previews
- **Benefits**: Safe testing using production API keys from GitHub secrets
- **Use case**: Preview thread quality before letting main workflow post

## Development Workflow

### Always run these before committing:
1. `python tests/test_bot.py` - Test core functionality
2. `python tests/test_integration.py` - Test integration workflows  
3. `python tools.py diagnose` - Test diagnostics
4. `python bot.py --diagnose` - Test bot diagnostics

### When modifying core functionality:
- Always test with `python tests/test_bot.py`
- Verify integration with `python tests/test_integration.py`
- Check that all essential tools work: `python tools.py <command>`

### When modifying rate limiting or article processing:
- Test with existing rate limit test files (still work via compatibility layer)
- Verify progressive cooldown behavior in `core.py`
- Check storage operations in the `Storage` class

### When adding new features:
- Add to `core.py` for fundamental functionality
- Extend `tools.py` for management interfaces  
- Maintain backward compatibility in `bot.py` wrapper
- Test both new core functionality and legacy compatibility

## Repository Structure Reference

```
.
├── .github/
│   └── workflows/
│       ├── main.yml                # Main bot workflow (90-minute schedule)
│       └── test-preview.yml        # Manual testing workflow (creates GitHub issues)
├── tests/                          # Streamlined test files (2 total)
│   ├── test_bot.py                 # Core functionality tests (9 tests) 
│   └── test_integration.py         # Integration workflow tests (3 tests)
├── core.py                         # Complete bot engine (Config, Storage, APIs, Processing)
├── bot.py                          # Main entry point with backward compatibility layer
├── tools.py                        # Unified management interface (preview, queue, clean, diagnose)
├── requirements.txt                # Python dependencies (streamlined)
├── posted_articles.json            # Article tracking (auto-generated)
├── rate_limit_cooldown.json        # Rate limit state (auto-generated) 
└── README.md                       # Comprehensive user documentation
```

This is a production-ready Twitter bot with **clean 5-file core architecture**, achieving 89% file reduction (47→5 core files) while maintaining robust error handling, rate limiting, and comprehensive testing. All tests are streamlined into just 2 elegant test files. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.