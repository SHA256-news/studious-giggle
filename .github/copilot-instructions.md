# Bitcoin Mining News Twitter Bot

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

Bitcoin Mining News Twitter Bot is a Python application that automatically fetches Bitcoin mining news from EventRegistry API and posts them to Twitter/X as AI-enhanced threads with Gemini-generated headlines and summaries. It runs every 90 minutes via GitHub Actions with sophisticated rate limiting, queue management, and comprehensive error handling.

## Ultra-Minimal Architecture Overview

The bot uses an **ultra-minimal, consolidated architecture** with clear separation of concerns:

- **`core.py`**: Complete core functionality (Config, Storage, API clients, GeminiClient, TimeManager, TextProcessor)
- **`bot.py`**: Main entry point with backward compatibility layer
- **`tools.py`**: Essential management tools (preview, queue, clean, diagnose)
- **`tests/test_bot.py`**: Core functionality tests (9 tests)
- **`tests/test_integration.py`**: Integration workflow tests (3 tests)

### Key Architectural Improvements
- **📉 Ultra-Minimal Complexity**: Consolidated 47+ files into 10 essential files (79% file reduction)
- **🚀 Enhanced Performance**: Lazy loading, optimized imports, sub-second startup
- **🧹 Eliminated Redundancy**: Removed duplicate code and unnecessary abstractions  
- **📚 Clean Interfaces**: Simple, readable, maintainable code structure
- **🛡️ Robust Error Handling**: Comprehensive validation and graceful failure handling
- **🔧 Type Safety**: Proper type annotations and Optional type handling for reliable API client initialization

## Working Effectively

### Bootstrap and Setup
- Install Python dependencies: `pip install -r requirements.txt`
- NEVER CANCEL: Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.

### Build and Test
- **Core tests**: `python tests/test_bot.py` -- comprehensive validation (9 tests)
- **Integration tests**: `python tests/test_integration.py` -- workflow validation (3 tests)
- **Bot diagnostics**: `python bot.py --diagnose` -- takes <3 seconds (optimized)
- **All tests organized**: All test files now in `tests/` directory for clean structure

### Essential Tools (Ultra-Minimal Interface)
- **Preview next thread**: `python tools.py preview` -- shows complete thread structure with character counts
- **Simple queue view**: `python tools.py queue` -- clean list of queued articles  
- **Posted articles history**: `python tools.py history [limit]` -- view recently posted tweets with full metadata (default: 10)
- **Clean queue**: `python tools.py clean` -- interactive removal of unwanted content
- **Full diagnostics**: `python tools.py diagnose` -- comprehensive bot health check
- **Test live APIs**: `python tools.py test` -- test EventRegistry & Gemini APIs without posting (requires API keys)

### Run the Application
- **Diagnose issues**: `python bot.py --diagnose` -- takes <3 seconds (optimized)
- **Run bot normally**: `python bot.py` -- will fail without API keys (expected)

## Core Features (Ultra-Simplified & Elegant)

### Smart Tweet Generation (Gemini Required)
- **Mandatory AI enhancement**: Bot requires Gemini API - waits and retries if unavailable
- **Smart threading logic**: Combines headline + summary in single tweet if ≤280 chars
- **Thread structure**: [Headline + Summary] → [URL] OR [Headline] → [Summary] → [URL]
- **Native URL context**: Gemini 2.5 Flash with direct article content access via Google's servers (up to 34MB per URL)
- **Anti-repetition intelligence**: Headlines and summaries complement each other, zero duplicate information
- **Enhanced AI prompts**: Specific examples and instructions for quality content generation
- **Professional formatting**: Line-break bullet points for improved readability
- **Emoji-free prefixes**: Professional text prefixes (BREAKING:, JUST IN:, NEWS:, HOT:)
- **Character limit compliance**: Perfect Twitter threading with proper reply chaining
- **Content deduplication**: Intelligent content-based similarity detection prevents duplicate articles from different sources

### Enhanced Bitcoin Mining Filter (Latest Critical Fix)
**Problem Solved**: Articles like "Tether Eyes $200M for Tokenized Gold Crypto Treasury With Antalpha" were incorrectly approved because they mentioned "mining" in the context of hardware manufacturers, not actual Bitcoin mining operations.

**Multi-Layer Filtering System**:
- **Title-based exclusions**: Automatically rejects articles with non-mining titles (gold, treasury, stablecoin, tokenized, etc.)
- **Topic filtering**: Excludes crypto-adjacent but non-mining topics (investment vehicles, custody services, trading platforms)
- **Mining focus requirements**: Requires at least 2 substantial mining industry terms, not just tangential mentions
- **Hardware vs. operations distinction**: Differentiates between mining hardware manufacturers and actual mining operations
- **Anti-promotional blocking**: Advanced detection for promotional content, scam schemes, and "free mining" apps
- **Content quality validation**: Ensures articles are primarily about Bitcoin mining operations, not just mentioning them

**Real-World Examples**:
- ✅ **Approved**: "Marathon Digital Announces Major Bitcoin Mining Expansion" (12 mining terms detected)
- ❌ **Rejected**: "Tether Eyes $200M for Tokenized Gold Crypto Treasury" (non-mining title topic: gold, treasury, tokenized)
- ❌ **Rejected**: "HashJ Claims Users Can Earn $118 Daily Through Free Bitcoin Mining App" (promotional content detected)

### Posted Articles History System (New Accountability Feature)
**Problem Solved**: Queue clearing removed all tracking of what was actually posted to Twitter, leaving no accountability or debugging capability.

**Comprehensive History Tracking**:
- **Rich metadata preservation**: Saves title, source, URLs, publish date, post date, and content preview for each posted article
- **New tools command**: `python tools.py history [limit]` to view posted articles with full context
- **Enhanced data structure**: Added `posted_articles_history` field while maintaining backward compatibility
- **Persistent tracking**: All future posts will be recorded with complete metadata for debugging and accountability

**Usage Examples**:
```bash
python tools.py history       # View last 10 posted articles with full metadata
python tools.py history 20   # View last 20 posted articles
```

### Technical Implementation Details

**Gemini URL Context Implementation**:
- Uses modern `google-genai` library with `tools=[Tool(url_context=UrlContext())]` parameter
- Gemini 2.5 Flash model with native URL content fetching up to 34MB per URL
- Comprehensive fallback system: URL context → EventRegistry content → generic fallback
- URL context metadata logging for debugging and validation
- Two-tier processing: `_process_headline_response()` and `_process_summary_response()` methods

**Smart Threading Logic Flow**:
1. Generate headline first using URL context
2. Pass headline to summary generation to avoid duplication
3. Check combined character count: headline + "\n\n" + summary
4. If ≤280 chars: Combine in single tweet, add URL as second tweet
5. If >280 chars: Separate into headline, summary, and URL tweets
6. Result: Optimal character usage with maximum information density

**Content Quality Enhancements**:
- Specific character limits: Headlines 60-80 chars, summaries <180 chars
- Professional prefixes instead of emoji decorations
- Action-oriented language with specific facts/numbers when available
- Multi-level validation and text processing for consistency

### Robust Article Management
- **Enhanced Bitcoin mining filtering**: Multi-layer filtering system that requires substantial Bitcoin mining focus, not just tangential mentions
- **Crypto-adjacent content exclusion**: Rejects articles about tokenized assets (like Tether gold), treasury management, and other crypto topics that aren't mining-related
- **Anti-promotional protection**: Blocks scam content, cloud mining apps, and "get rich quick" schemes (prevents HashJ-style promotional content)
- **Content quality enforcement**: Requires minimum 2 substantial mining industry terms for approval, distinguishes hardware manufacturing from actual mining operations
- **Posted articles history retention**: Comprehensive tracking of all published tweets with full metadata (title, source, dates, content preview)
- **Smart queueing**: Multiple articles queued, posted one at a time
- **Time-based validation**: Article freshness and staleness detection
- **Queue management**: Interactive tools for preview, editing, and cleaning

### Production-Ready Reliability
- **Rate limit handling**: Progressive cooldowns with intelligent recovery
- **Error resilience**: Graceful failure handling with detailed diagnostics
- **Data persistence**: JSON-based storage with atomic operations
- **Minimum interval enforcement**: Respects Twitter API daily limits

### Ultra-Minimal Performance Optimizations

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
- `GEMINI_API_KEY` - Google Gemini API key (Gemini 2.5 Flash with native URL context for AI headlines and summaries) **MANDATORY**

**CRITICAL**: Gemini API key is now REQUIRED. The bot will not publish without AI enhancement - it waits and retries when Gemini is unavailable instead of posting inferior content.

### Advanced AI Content Generation

**Native URL Context (Latest Enhancement)**:
- Uses modern `google-genai` library with Gemini 2.5 Flash model
- Google's servers fetch article content directly (no manual web scraping)
- Up to 34MB content per URL with comprehensive article analysis
- Enhanced content quality with full article access
- URL context metadata logging for debugging

**Anti-Repetition System**:
- Headlines generated first, then passed to summary generation
- Summary explicitly instructed to avoid repeating headline information
- Enhanced prompts with specific do/don't examples
- Results in complementary content: headline focuses on main story, summary provides additional details
- Example: Headline "Marathon Digital Deploys 5,000 New Miners" → Summary:
  "• Located in West Texas
  • Q2 2024 start
  • 8-month ROI target"

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
- **Ultra-minimal testing**: Only 2 test files for elegant architecture

**Error Handling Validation**:
- Run `python bot.py` without API keys and verify clear error messages
- Check that the bot exits gracefully with helpful instructions

**Complete Development Workflow Validation**:
```bash
# Ultra-minimal validation sequence - elegant 2-test architecture
pip install -r requirements.txt
python tests/test_bot.py          # Core functionality tests (9 tests)
python tests/test_integration.py  # Integration workflow tests (3 tests)  
python bot.py --diagnose
python tools.py diagnose
```

### Manual Testing Without API Keys
Since this repository doesn't have API keys configured by default:
- Always run diagnostic commands to verify the bot detects missing configuration
- Test that error messages are clear and actionable
- Verify that all tests pass (they use mocked APIs)

## Common Tasks

### Code Locations (Ultra-Minimally Simplified)
- **Core functionality**: `core.py` (complete bot engine: Config, Storage, API clients, ContentSimilarity, processing)
- **Main entry point**: `bot.py` (execution + backward compatibility layer)
- **Management tools**: `tools.py` (preview, queue management, diagnostics)
- **Core tests**: `tests/test_bot.py` (comprehensive core tests - 9 tests)
- **Integration tests**: `tests/test_integration.py` (streamlined integration tests - 3 tests)
- **GitHub Actions**: `.github/workflows/main.yml`

**Removed complexity**: Eliminated all complex dependencies and file structures - everything consolidated into ultra-minimal core architecture.

### Key Dependencies (Ultra-Minimal)
- `tweepy>=4.14.0` - Twitter API client  
- `eventregistry>=9.1` - News article fetching
- `google-genai>=0.1.0` - Modern Gemini 2.5 Flash with native URL context support
- `requests>=2.25.0` - HTTP client for API calls
- **Note**: Only 4 essential dependencies (60% reduction from 10 packages) for ultra-minimal setup

### Important Files (Ultra-Simplified)
- `requirements.txt` - Python dependencies (ultra-minimal: 4 packages)
- `posted_articles.json` - Tracks posted articles and queue
- `README.md` - Comprehensive user documentation

**Removed files**: All complex configurations and directories eliminated for ultra-minimal simplicity

## Timing Expectations and Cancellation Warnings

### NEVER CANCEL these operations:
- **Dependency installation**: 30-60 seconds (set timeout to 120+ seconds)
- **Test execution**: Most tests complete in <1 second
- **Bot diagnostics**: <3 seconds (ultra-optimized)
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

### Gemini API Unavailable (New Mandatory Behavior)
**Symptoms**: "Gemini API is required but not available - will retry later"
**Solution**: Bot waits for Gemini API without setting rate limit cooldowns - retries on next scheduled run

### EventRegistry API Parameter Error (Fixed in v1.1)
**Symptoms**: "QueryArticles.__init__() got an unexpected keyword argument 'keywordLoc'"
**Solution**: Fixed by removing invalid keywordLoc parameter from QueryArticlesIter constructor. Bot now uses default keyword search behavior.

## CI/GitHub Actions

The bot includes a single, focused GitHub Actions workflow:

### Main Bot Workflow (`.github/workflows/main.yml`)
- **Schedule**: Runs every 90 minutes automatically
- **Purpose**: Fetches Bitcoin mining articles and posts Twitter threads
- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)
- **Python version**: 3.10 (but works with 3.12+)
- **Dependencies**: Installs from `requirements.txt`
- **Commits**: Updates `posted_articles.json` after successful runs
- **Ultra-minimal approach**: Single workflow eliminates complexity

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
│       └── main.yml                # Single bot workflow (90-minute schedule)
├── tests/                          # Ultra-minimal test files (2 total)
│   ├── test_bot.py                 # Core functionality tests (9 tests) 
│   └── test_integration.py         # Integration workflow tests (3 tests)
├── core.py                         # Complete bot engine (Config, Storage, APIs, Processing)
├── bot.py                          # Main entry point with backward compatibility layer
├── tools.py                        # Unified management interface (preview, queue, clean, diagnose)
├── requirements.txt                # Python dependencies (ultra-minimal: 4 packages)
├── posted_articles.json            # Article tracking (auto-generated)
└── README.md                       # Comprehensive user documentation

**TOTAL: 10 essential files (79% reduction from 47 files)**
```

This is a production-ready Twitter bot with **ultra-minimal 10-file core architecture**, achieving 79% file reduction while maintaining robust error handling, rate limiting, and comprehensive testing. All tests are streamlined into just 2 elegant test files. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.