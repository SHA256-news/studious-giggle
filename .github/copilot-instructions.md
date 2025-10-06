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
- **🛡️ Robust Error Handling**: Comprehensive validation and graceful failure handling including queue bounds checking, specific API error types, improved mining filter validation, safe dictionary access, robust None handling, and enhanced file cleanup
- **🔧 Type Safety**: Complete type annotation coverage with Optional[GeminiClient] fixes, explicit List[Article] typing, Union import support, and Dict[str, Any] annotations for all data structures
- **🧪 Production Reliability**: Improved test file handling, removed misleading parameters, optimized GitHub workflow scheduling, and comprehensive validation patterns

## Recent Critical Bug Fixes (Session Summary)

The codebase has undergone comprehensive bug fixing with **19 critical issues resolved** (6 new fixes added):

### Type Safety & Error Handling Improvements:
1. **✅ Gemini Client Type Mismatch**: Fixed Optional[GeminiClient] property return type annotation
2. **✅ Article List Type Safety**: Added explicit List[Article] annotations for data collections
3. **✅ Queue Bounds Checking**: Added validation before queue.pop() to prevent IndexError
4. **✅ Specific Error Handling**: Replaced broad Exception catching with ValueError/ConnectionError specificity
5. **✅ Union Import Support**: Added Union to typing imports for comprehensive type annotation capabilities
6. **✅ Dictionary Type Annotations**: Added explicit Dict[str, Any] type for posted_article_record
7. **✅ URL Retrieval Error Handling**: NEW - Distinguished URL retrieval failures from API failures with proper error categorization
8. **✅ Gemini Metadata Checking**: CRITICAL FIX - **ACTUALLY IMPLEMENTED** - Proper detection of URL failures from url_context_metadata with safe iteration to prevent posting error messages

### NEW: Additional Critical Fixes (October 2025):
15. **✅ URLRetrievalError Exception Safety**: CRITICAL - Fixed potential crashes when url_context_metadata is None or not iterable with proper type checking and safe iteration patterns
16. **✅ Queue Index Error Protection**: CRITICAL - Added bounds validation and exception handling in tools.py queue operations to prevent IndexError during concurrent modifications  
17. **✅ Complete Queue State Management**: CRITICAL - Implemented proper queue bounds checking with state recovery instead of just logging warnings when queue operations fail
18. **✅ URL Format Validation**: MODERATE - Added comprehensive URL validation to catch malformed URLs (non-http/https, spaces, too short) that pass empty string validation but cause downstream errors
19. **✅ URL Retrieval Status Logic**: CRITICAL - **JUST FIXED** - Corrected enum status checking to properly handle `UrlRetrievalStatus.URL_RETRIEVAL_STATUS_SUCCESS` format instead of simple string comparison, preventing rate limit cooldowns on successful URL retrievals
20. **✅ Gemini URL Context API Format**: CRITICAL - **OCTOBER 2025 MAJOR FIX** - Discovered and fixed fundamental SDK vs REST API format confusion. We were using REST API dict syntax `{"url_context": {}}` in Python SDK calls instead of proper object syntax `types.Tool(url_context=types.UrlContext())`. This was the root cause of "unable to fetch content" error messages being posted as tweets.

### Robustness & Validation Improvements:
9. **✅ Mining Filter Logic**: Enhanced counting validation with defensive bounds checking
10. **✅ Thread Type Error**: Added None check before enumeration in tools.py preview
11. **✅ Safe Dictionary Access**: Added isinstance() validation for source_data.get() calls
12. **✅ Test File Cleanup**: Improved temporary file handling to prevent race conditions

### API & Workflow Optimizations:
13. **✅ Clean API Design**: Removed misleading skip_gemini_analysis parameter
14. **✅ Optimized Scheduling**: Clarified GitHub workflow cron scheduling (complementary 90-minute intervals)

All fixes maintain **100% backward compatibility** with comprehensive testing validation. **NEW**: All 9 core functionality tests and 3 integration tests passing after latest fixes. **OCTOBER 2025 MAJOR UPDATE**: Fixed fundamental Gemini URL Context API implementation - bot will now fetch actual article content instead of posting error messages.

## Working Effectively

### 📚 API Documentation (NEW - CRITICAL FOR REFACTORING)
- **PERMANENT API REFERENCE**: `/docs/api/` directory contains hard-coded API documentation
- **Never forget API details**: Complete EventRegistry, Gemini, and Twitter API references
- **Before refactoring**: Always check `/docs/api/eventregistry.md` and `/docs/api/gemini.md`
- **Quick patterns**: `/docs/api/quick-reference.md` has copy-paste ready code snippets
- **In-code references**: All API clients in `core.py` link to permanent documentation
- **🚨 GEMINI URL CONTEXT**: `/docs/api/gemini-url-context-CORRECT.md` contains EXACT correct implementation to prevent error message tweets

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

### Enhanced Bitcoin Mining Filter (CORRECTED Based on User Feedback)
**Problem Solved**: Previous filter was too restrictive, rejecting valid mining articles about public miners, AI/mining relationships, and political/regulatory news.

**Improved Multi-Layer Filtering System**:
- **Public mining companies auto-approval**: Comprehensive coverage of 33 publicly traded Bitcoin mining companies including Marathon Digital (MARA), Riot Platforms (RIOT), CleanSpark (CLSK), Hut 8 (HUT), Core Scientific (CORZ), Cipher Mining (CIFR), Bitfarms (BITF), HIVE Digital (HIVE), TeraWulf (WULF), Bitdeer (BTDR), Iris Energy (IREN), Bit Digital (BTBT), Greenidge (GREE), Stronghold (SDIG), Argo Blockchain (ARBK), Canaan (CAN), BIT Mining (BTCM), BitFuFu (FUFU), and many more - ALL are ALWAYS relevant
- **AI + mining relationships**: Articles about AI data centers, power struggles, electricity consumption with mining context are approved
- **Political/regulatory mining news**: Government policies, regulations, bans, approvals related to Bitcoin mining are approved
- **Flexible mining focus**: Requires only 1 substantial mining term (not 2+) for approval
- **Targeted exclusions**: Only excludes obvious cloud mining, promotional schemes, and clear non-mining topics (DeFi, NFT, Web3)
- **Content quality validation**: Ensures articles are genuinely about Bitcoin mining operations, companies, or regulation

**Real-World Examples** (Now APPROVED):
- ✅ **"Why Hut 8 Stock Was Blasting Higher This Week"** - Public mining company (auto-approved)
- ✅ **"'Shark Tank' Star Kevin O'Leary Says Bitcoin Mining, AI Data Centers Are Locked In A 'Power Struggle'"** - AI+mining relationship (approved)
- ✅ **"JPMorgan Downgrades CleanSpark (CLSK) to Neutral"** - Public mining company (auto-approved)  
- ✅ **"France: Éric Ciotti Opposes U.S. Takeover of Exaion, Defends Bitcoin Mining"** - Political/regulatory (approved)
- ✅ **"MARA | My Life Long Girlfriend Stock | LONG"** - Public mining company MARA (auto-approved)

**Validation Results**: 7/7 filter tests passing after corrections, with proper rejection of promotional content like "HashJ Claims Users Can Earn $118 Daily Through Free Bitcoin Mining App" while approving legitimate mining industry content.

**Complete Public Miners Coverage**: The filter now includes all major publicly traded Bitcoin mining companies: Marathon Digital Holdings Inc. (MARA), Riot Platforms Inc. (RIOT), CleanSpark Inc. (CLSK), Hut 8 Mining Corp. (HUT), Core Scientific Inc. (CORZ), Cipher Mining Inc. (CIFR), Bitfarms Ltd. (BITF), HIVE Digital Technologies Ltd. (HIVE), TeraWulf Inc. (WULF), Bitdeer Technologies Group (BTDR), Iris Energy Ltd. (IREN), Bit Digital Inc. (BTBT), Greenidge Generation Holdings Inc. (GREE), Stronghold Digital Mining Inc. (SDIG), Argo Blockchain PLC (ARBK/ARBKF), Canaan Inc. (CAN), BIT Mining Limited (BTCM), BitFuFu Inc. (FUFU), Phoenix Group PLC (PHX), The9 Limited (NCTY), DMG Blockchain Solutions Inc. (DMGI/DMGGF), Cathedra Bitcoin Inc. (CBIT/CBTTF), Bitcoin Well Inc. (BTCW), LM Funding America Inc. (LMFA), SOS Limited (SOS), Neptune Digital Assets (NDA/NPPTF), Digihost Technology Inc. (HSSHF), SATO Technologies Corp. (SATO), Sphere 3D Corp (ANY), Gryphon Digital Mining Inc. (GRYP), American Bitcoin Corp. (ABTC), and Abits Group Inc. (ABTS).

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

### 🚨 CRITICAL: Gemini URL Context API Implementation (NEVER GET WRONG AGAIN!)

**RECURRING ISSUE**: This bug keeps coming up when we modify code. Always follow this EXACT pattern:

**✅ CORRECT Implementation (October 2025 FIX):**
```python
from google import genai
from google.genai.types import GenerateContentConfig

client = genai.Client(api_key=api_key)

# ✅ CORRECT: Simple dict format - ALWAYS USE THIS
config = GenerateContentConfig(
    tools=[{"url_context": {}}]  # Simple dict, NOT complex objects
)
```

**❌ WRONG Implementation (NEVER USE):**
```python
# ❌ WRONG: Complex object format (causes "unable to fetch content" errors)
from google.genai import types
tools = [types.Tool(url_context=types.UrlContext())]
```

**🚨 CRITICAL: URL Retrieval Status Checking (October 2025 FIX):**
```python
# ✅ CORRECT: Proper status checking
if hasattr(url_meta, 'url_retrieval_status'):
    status = url_meta.url_retrieval_status
    status_str = str(status)
    # Check for SUCCESS status (handle both enum value and string representation)
    is_success = (
        status_str == "URL_RETRIEVAL_STATUS_SUCCESS" or 
        "URL_RETRIEVAL_STATUS_SUCCESS" in status_str
    )
    if not is_success:
        # URL retrieval failed
        raise URLRetrievalError(f"Failed to retrieve content from {url}: {status_str}")
    else:
        # URL retrieval succeeded - continue processing
        logger.info(f"✅ URL retrieval successful: {status_str}")
```

**❌ WRONG Status Checking (What We Fixed):**
```python
# ❌ WRONG: String comparison fails with enum representation
if str(status) != "URL_RETRIEVAL_STATUS_SUCCESS":
    # This fails because enum includes class name: "UrlRetrievalStatus.URL_RETRIEVAL_STATUS_SUCCESS"
```

**Reference Documentation:**
- **Official URL Context Docs**: https://ai.google.dev/gemini-api/docs/url-context
- **Cookbook Examples**: https://github.com/google-gemini/cookbook
- **Internal Reference**: `/docs/api/gemini-url-context-CORRECT.md`

**If Bot Posts Error Messages OR Triggers Rate Limits on Success**: This means wrong tool configuration or status checking - use patterns above!

### Technical Implementation Details

**Gemini URL Context Implementation**:
- Uses modern `google-genai` library with `tools=[{"url_context": {}}]` parameter (CORRECTED)
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
- **Rate limit handling**: Progressive cooldowns with intelligent recovery (only for Twitter API 17 posts/day limit)
- **Smart URL error handling**: URL retrieval failures skip article and continue with next one (no cooldown triggered)  
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
- **CRITICAL**: Uses `tools=[{"url_context": {}}]` simple dict format (NOT complex objects)
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

### Technical Implementation Details

**URL Error Handling Implementation**:
- Custom `URLRetrievalError` exception class distinguishes URL failures from API failures
- Gemini methods check `url_context_metadata` for `URL_RETRIEVAL_STATUS_ERROR` after each response
- When URL retrieval fails, `URLRetrievalError` is raised immediately before content generation
- Bot logic catches `URLRetrievalError` and skips problematic articles without triggering rate limit cooldown
- Only Twitter API failures (429 Too Many Requests, 17 posts/day limit) trigger progressive cooldowns
- URL failures result in article removal from queue and continuation with next available article
- **CRITICAL**: Prevents posting error messages like "I am unable to access the content..." as tweets

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

### URL Retrieval Failures (New Smart Handling) 
**Symptoms**: "URL retrieval failed", "Failed to retrieve content from [URL]", URLRetrievalError
**Solution**: Bot automatically skips articles with inaccessible URLs and moves to the next article in queue
**CRITICAL**: URL retrieval failures **DO NOT** trigger rate limit cooldowns - only Twitter API failures (17 posts/day limit) trigger cooldowns
**Behavior**: When Gemini cannot access a specific URL (blocked, 403, 404, etc.), the article is skipped and removed from queue
**Impact**: Bot continues processing remaining articles without waiting, ensuring maximum posting efficiency

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
├── docs/
│   └── api/                        # 🆕 PERMANENT API DOCUMENTATION
│       ├── README.md               # API documentation usage guide
│       ├── eventregistry.md        # Complete EventRegistry Python SDK reference
│       ├── gemini.md               # Complete Google Gemini API reference
│       └── quick-reference.md      # Copy-paste ready code snippets
├── tests/                          # Ultra-minimal test files (2 total)
│   ├── test_bot.py                 # Core functionality tests (9 tests) 
│   └── test_integration.py         # Integration workflow tests (3 tests)
├── core.py                         # Complete bot engine (Config, Storage, APIs, Processing)
├── bot.py                          # Main entry point with backward compatibility layer
├── tools.py                        # Unified management interface (preview, queue, clean, diagnose)
├── requirements.txt                # Python dependencies (ultra-minimal: 4 packages)
├── posted_articles.json            # Article tracking (auto-generated)
└── README.md                       # Comprehensive user documentation

**TOTAL: 10 essential files + 4 permanent API docs (79% reduction from 47 files)**
```

This is a production-ready Twitter bot with **ultra-minimal 10-file core architecture**, achieving 79% file reduction while maintaining robust error handling, rate limiting, and comprehensive testing. All tests are streamlined into just 2 elegant test files. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.