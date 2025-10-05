# Bitcoin Mining News Twitter Bot# Bitcoin Mining News Twitter Bot



Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.



Bitcoin Mining News Twitter Bot is a Python application that automatically fetches Bitcoin mining news from EventRegistry API and posts them to Twitter/X as AI-enhanced threads with Gemini-generated headlines and summaries. It runs every 90 minutes via GitHub Actions with sophisticated rate limiting, queue management, and comprehensive error handling.Bitcoin Mining News Twitter Bot is a Python application that automatically fetches Bitcoin mining news from EventRegistry API and posts them to Twitter/X as AI-enhanced threads with Gemini-generated headlines and summaries. It runs every 90 minutes via GitHub Actions with sophisticated rate limiting, queue management, and comprehensive error handling.



## Ultra-Minimal Architecture Overview## Elegant Architecture Overview



The bot uses an **ultra-minimal, consolidated architecture** with clear separation of concerns:The bot now uses an **elegant, consolidated architecture** with clear separation of concerns:



- **`core.py`**: Complete core functionality (Config, Storage, API clients, GeminiClient, TimeManager, TextProcessor)- **`core.py`**: Complete core functionality (Config, Storage, API clients, GeminiClient, TimeManager, TextProcessor)

- **`bot.py`**: Main entry point with backward compatibility layer- **`bot.py`**: Main entry point with backward compatibility layer

- **`tools.py`**: Essential management tools (preview, queue, clean, diagnose)- **`tools.py`**: Essential management tools (preview, queue, clean, diagnose)

- **`tests/test_bot.py`**: Core functionality tests (9 tests)- **`tests/test_bot.py`**: Core functionality tests (9 tests)

- **`tests/test_integration.py`**: Integration workflow tests (3 tests)- **`tests/test_integration.py`**: Integration workflow tests (3 tests)



### Key Architectural Improvements### Key Architectural Improvements

- **📉 Ultra-Minimal Complexity**: Consolidated 47+ files into 10 essential files (79% file reduction)- **📉 Reduced Complexity**: Consolidated 47+ files into 5 elegant modules (89% file reduction)

- **🚀 Enhanced Performance**: Lazy loading, optimized imports, sub-second startup- **🚀 Enhanced Performance**: Lazy loading, optimized imports, sub-second startup

- **🧹 Eliminated Redundancy**: Removed duplicate code and unnecessary abstractions  - **🧹 Eliminated Redundancy**: Removed duplicate code and unnecessary abstractions  

- **📚 Clean Interfaces**: Simple, readable, maintainable code structure- **📚 Clean Interfaces**: Simple, readable, maintainable code structure

- **🛡️ Robust Error Handling**: Comprehensive validation and graceful failure handling- **🛡️ Robust Error Handling**: Comprehensive validation and graceful failure handling



## Working Effectively## Working Effectively



### Bootstrap and Setup### Bootstrap and Setup

- Install Python dependencies: `pip install -r requirements.txt`- Install Python dependencies: `pip install -r requirements.txt`

- NEVER CANCEL: Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.- NEVER CANCEL: Dependency installation takes 30-60 seconds. Set timeout to 120+ seconds.



### Build and Test### Build and Test

- **Core tests**: `python tests/test_bot.py` -- comprehensive validation (9 tests)- **Core tests**: `python tests/test_bot.py` -- comprehensive validation (9 tests)

- **Integration tests**: `python tests/test_integration.py` -- workflow validation (3 tests)- **Integration tests**: `python tests/test_integration.py` -- workflow validation (3 tests)

- **Bot diagnostics**: `python bot.py --diagnose` -- takes <3 seconds (optimized)- **Bot diagnostics**: `python bot.py --diagnose` -- takes <3 seconds (optimized)

- **All tests organized**: All test files now in `tests/` directory for clean structure- **All tests organized**: All test files now in `tests/` directory for clean structure



### Essential Tools (Ultra-Minimal Interface)### Essential Tools (New Consolidated Interface)

- **Preview next thread**: `python tools.py preview` -- shows complete thread structure with character counts- **Preview next thread**: `python tools.py preview` -- shows complete thread structure with character counts

- **Simple queue view**: `python tools.py queue` -- clean list of queued articles  - **Simple queue view**: `python tools.py queue` -- clean list of queued articles  

- **Clean queue**: `python tools.py clean` -- interactive removal of unwanted content- **Clean queue**: `python tools.py clean` -- interactive removal of unwanted content

- **Full diagnostics**: `python tools.py diagnose` -- comprehensive bot health check- **Full diagnostics**: `python tools.py diagnose` -- comprehensive bot health check

- **Test live APIs**: `python tools.py test` -- test EventRegistry & Gemini APIs without posting (requires API keys)- **Test live APIs**: `python tools.py test` -- test EventRegistry & Gemini APIs without posting (requires API keys)



### Run the Application### Run the Application

- **Diagnose issues**: `python bot.py --diagnose` -- takes <3 seconds (optimized)- **Diagnose issues**: `python bot.py --diagnose` -- takes <3 seconds (optimized)

- **Run bot normally**: `python bot.py` -- will fail without API keys (expected)- **Run bot normally**: `python bot.py` -- will fail without API keys (expected)



## Core Features (Ultra-Simplified & Elegant)## Core Features (Simplified & Elegant)



### Smart Tweet Generation### Smart Tweet Generation

- **AI-enhanced threads**: Multi-tweet structure with Gemini-generated headlines and summaries- **AI-enhanced threads**: Multi-tweet structure with Gemini-generated headlines and summaries

- **Native URL context**: Gemini 2.0 Flash Exp with direct article content access via Google's servers- **Native URL context**: Gemini 2.0 Flash Exp with direct article content access via Google's servers

- **Anti-repetition intelligence**: Headlines and summaries complement each other, zero duplicate information- **Anti-repetition intelligence**: Headlines and summaries complement each other, zero duplicate information

- **Enhanced AI prompts**: Specific examples and instructions for quality content generation- **Enhanced AI prompts**: Specific examples and instructions for quality content generation

- **Professional formatting**: Line-break bullet points for improved readability- **Professional formatting**: Line-break bullet points for improved readability

- **Intelligent fallback**: 2-tweet threads (headline → URL) when Gemini unavailable- **Intelligent fallback**: 2-tweet threads (headline → URL) when Gemini unavailable

- **Emoji-free prefixes**: Professional text prefixes (BREAKING:, JUST IN:, NEWS:, HOT:)- **Emoji-free prefixes**: Professional text prefixes (BREAKING:, JUST IN:, NEWS:, HOT:)

- **Thread structure**: With Gemini: Headline → 3-point summary → URL | Without: Headline → URL- **Thread structure**: With Gemini: Headline → 3-point summary → URL | Without: Headline → URL

- **Character limit compliance**: Perfect Twitter threading with proper reply chaining- **Character limit compliance**: Perfect Twitter threading with proper reply chaining

- **Content deduplication**: Tracks posted articles to prevent repeats- **Content deduplication**: Tracks posted articles to prevent repeats



### Technical Implementation Details### Technical Implementation Details



**Gemini URL Context Implementation**:**Gemini URL Context Implementation**:

- Uses `tools=[{"url_context": {}}]` parameter in `generate_content()` calls- Uses `tools=[{"url_context": {}}]` parameter in `generate_content()` calls

- Gemini 2.0 Flash Exp model with native URL content fetching- Gemini 2.0 Flash Exp model with native URL content fetching

- Comprehensive fallback system: URL context → EventRegistry content → generic fallback- Comprehensive fallback system: URL context → EventRegistry content → generic fallback

- URL context metadata logging for debugging and validation- URL context metadata logging for debugging and validation

- Two-tier processing: `_process_headline_response()` and `_process_summary_response()` methods- Two-tier processing: `_process_headline_response()` and `_process_summary_response()` methods



**Anti-Repetition Logic Flow**:**Anti-Repetition Logic Flow**:

1. Generate headline first using URL context1. Generate headline first using URL context

2. Pass headline to summary generation to avoid duplication2. Pass headline to summary generation to avoid duplication

3. Summary prompt explicitly includes headline and instructs "DO NOT REPEAT"3. Summary prompt explicitly includes headline and instructs "DO NOT REPEAT"

4. Enhanced prompts with specific examples of good/bad complementary content4. Enhanced prompts with specific examples of good/bad complementary content

5. Result: Maximum information density with zero redundancy5. Result: Maximum information density with zero redundancy



**Content Quality Enhancements**:**Content Quality Enhancements**:

- Specific character limits: Headlines 60-80 chars, summaries <180 chars- Specific character limits: Headlines 60-80 chars, summaries <180 chars

- Professional prefixes instead of emoji decorations- Professional prefixes instead of emoji decorations

- Action-oriented language with specific facts/numbers when available- Action-oriented language with specific facts/numbers when available

- Multi-level validation and text processing for consistency- Multi-level validation and text processing for consistency



### Robust Article Management### Robust Article Management

- **Bitcoin-focused filtering**: Advanced keyword matching for relevant content- **Bitcoin-focused filtering**: Advanced keyword matching for relevant content

- **Smart queueing**: Multiple articles queued, posted one at a time- **Smart queueing**: Multiple articles queued, posted one at a time

- **Time-based validation**: Article freshness and staleness detection- **Time-based validation**: Article freshness and staleness detection

- **Queue management**: Interactive tools for preview, editing, and cleaning- **Queue management**: Interactive tools for preview, editing, and cleaning



### Production-Ready Reliability### Production-Ready Reliability

- **Rate limit handling**: Progressive cooldowns with intelligent recovery- **Rate limit handling**: Progressive cooldowns with intelligent recovery

- **Error resilience**: Graceful failure handling with detailed diagnostics- **Error resilience**: Graceful failure handling with detailed diagnostics

- **Data persistence**: JSON-based storage with atomic operations- **Data persistence**: JSON-based storage with atomic operations

- **Minimum interval enforcement**: Respects Twitter API daily limits- **Minimum interval enforcement**: Respects Twitter API daily limits



### Ultra-Minimal Performance Optimizations### Elegant Performance Optimizations



**⚡ Lightning-Fast Startup (< 1 second)****⚡ Lightning-Fast Startup (< 1 second)**

- **Lazy initialization**: API clients created only when needed- **Lazy initialization**: API clients created only when needed

- **Streamlined imports**: No heavy dependencies during startup- **Streamlined imports**: No heavy dependencies during startup

- **Optimized data structures**: Efficient in-memory processing- **Optimized data structures**: Efficient in-memory processing



**🚀 Efficient Runtime****🚀 Efficient Runtime**

- **Single-pass processing**: Minimized API calls and file operations- **Single-pass processing**: Minimized API calls and file operations

- **Smart caching**: Reuses loaded data throughout execution- **Smart caching**: Reuses loaded data throughout execution

- **Intelligent error recovery**: Continues operation despite transient failures- **Intelligent error recovery**: Continues operation despite transient failures



## Required API Keys Setup## Required API Keys Setup



The bot requires these GitHub repository secrets:The bot requires these GitHub repository secrets:

- `TWITTER_API_KEY` - Twitter API key- `TWITTER_API_KEY` - Twitter API key

- `TWITTER_API_SECRET` - Twitter API secret- `TWITTER_API_SECRET` - Twitter API secret

- `TWITTER_ACCESS_TOKEN` - Twitter access token  - `TWITTER_ACCESS_TOKEN` - Twitter access token  

- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret

- `EVENTREGISTRY_API_KEY` - EventRegistry/NewsAPI.ai API key- `EVENTREGISTRY_API_KEY` - EventRegistry/NewsAPI.ai API key

- `GEMINI_API_KEY` - Google Gemini API key (Gemini 2.0 Flash Exp with native URL context for AI headlines and summaries)- `GEMINI_API_KEY` - Google Gemini API key (Gemini 2.0 Flash Exp with native URL context for AI headlines and summaries)



**Note**: With Gemini API key, the bot generates AI-enhanced multi-tweet threads using advanced URL context and anti-repetition systems. Without it, it falls back to clean 2-tweet threads (headline → URL).**Note**: With Gemini API key, the bot generates AI-enhanced multi-tweet threads using advanced URL context and anti-repetition systems. Without it, it falls back to clean 2-tweet threads (headline → URL).



### Advanced AI Content Generation### Advanced AI Content Generation



**Native URL Context (Latest Enhancement)**:**Native URL Context (Latest Enhancement)**:

- Uses Gemini 2.0 Flash Exp model with built-in URL context tool- Uses Gemini 2.0 Flash Exp model with built-in URL context tool

- Google's servers fetch article content directly (no manual web scraping)- Google's servers fetch article content directly (no manual web scraping)

- Eliminates bot detection and content extraction issues- Eliminates bot detection and content extraction issues

- Enhanced content quality with full article access- Enhanced content quality with full article access

- URL context metadata logging for debugging- URL context metadata logging for debugging



**Anti-Repetition System**:**Anti-Repetition System**:

- Headlines generated first, then passed to summary generation- Headlines generated first, then passed to summary generation

- Summary explicitly instructed to avoid repeating headline information- Summary explicitly instructed to avoid repeating headline information

- Enhanced prompts with specific do/don't examples- Enhanced prompts with specific do/don't examples

- Results in complementary content: headline focuses on main story, summary provides additional details- Results in complementary content: headline focuses on main story, summary provides additional details

- Example: Headline "Marathon Digital Deploys 5,000 New Miners" → Summary:- Example: Headline "Marathon Digital Deploys 5,000 New Miners" → Summary:

  "• Located in West Texas  "• Located in West Texas

  • Q2 2024 start  • Q2 2024 start

  • 8-month ROI target"  • 8-month ROI target"



Without these keys, the bot will show clear error messages explaining what's missing.Without these keys, the bot will show clear error messages explaining what's missing.



## Validation Scenarios## Validation Scenarios



### CRITICAL: Always Test These Scenarios After Changes### CRITICAL: Always Test These Scenarios After Changes



**Diagnostic Validation**:**Diagnostic Validation**:

- Run `python bot.py --diagnose` and verify it identifies missing API keys correctly- Run `python bot.py --diagnose` and verify it identifies missing API keys correctly

- Check that it shows helpful setup instructions- Check that it shows helpful setup instructions

- Verify posted articles file is readable- Verify posted articles file is readable



### Test Suite Validation**:  ### Test Suite Validation**:  

- Run `python tests/test_bot.py` and verify core bot functionality (9 tests)- Run `python tests/test_bot.py` and verify core bot functionality (9 tests)

- Run `python tests/test_integration.py` and verify integration workflows (3 tests)- Run `python tests/test_integration.py` and verify integration workflows (3 tests)

- **Ultra-minimal testing**: Only 2 test files for elegant architecture- **Streamlined testing**: Only 2 test files for elegant architecture



**Error Handling Validation**:**Error Handling Validation**:

- Run `python bot.py` without API keys and verify clear error messages- Run `python bot.py` without API keys and verify clear error messages

- Check that the bot exits gracefully with helpful instructions- Check that the bot exits gracefully with helpful instructions



**Complete Development Workflow Validation**:**Complete Development Workflow Validation**:

```bash```bash

# Ultra-minimal validation sequence - elegant 2-test architecture# Streamlined validation sequence - elegant 2-test architecture

pip install -r requirements.txtpip install -r requirements.txt

python tests/test_bot.py          # Core functionality tests (9 tests)python tests/test_bot.py          # Core functionality tests (8+ tests)

python tests/test_integration.py  # Integration workflow tests (3 tests)  python tests/test_integration.py  # Integration workflow tests (2+ tests)  

python bot.py --diagnosepython bot.py --diagnose

python tools.py diagnosepython tools.py diagnose

``````



### Manual Testing Without API Keys### Manual Testing Without API Keys

Since this repository doesn't have API keys configured by default:Since this repository doesn't have API keys configured by default:

- Always run diagnostic commands to verify the bot detects missing configuration- Always run diagnostic commands to verify the bot detects missing configuration

- Test that error messages are clear and actionable- Test that error messages are clear and actionable

- Verify that all tests pass (they use mocked APIs)- Verify that all tests pass (they use mocked APIs)



## Common Tasks## Common Tasks



### Code Locations (Ultra-Minimally Simplified)### Code Locations (Elegantly Simplified)

- **Core functionality**: `core.py` (complete bot engine: Config, Storage, API clients, processing)- **Core functionality**: `core.py` (complete bot engine: Config, Storage, API clients, processing)

- **Main entry point**: `bot.py` (execution + backward compatibility layer)- **Main entry point**: `bot.py` (execution + backward compatibility layer)

- **Management tools**: `tools.py` (preview, queue management, diagnostics)- **Management tools**: `tools.py` (preview, queue management, diagnostics)

- **Core tests**: `tests/test_bot.py` (comprehensive core tests - 9 tests)- **Core tests**: `tests/test_bot.py` (comprehensive core tests - 9 tests)

- **Integration tests**: `tests/test_integration.py` (streamlined integration tests - 3 tests)- **Integration tests**: `tests/test_integration.py` (streamlined integration tests - 3 tests)

- **GitHub Actions**: `.github/workflows/main.yml`- **GitHub Actions**: `.github/workflows/main.yml`



**Removed complexity**: Eliminated all complex dependencies and file structures - everything consolidated into ultra-minimal core architecture.**Removed complexity**: Eliminated `api_clients.py`, `utils.py`, `config.py`, `tweet_poster.py`, `gemini_client.py`, image modules, and various diagnostic scripts - all consolidated into elegant core architecture.



### Key Dependencies (Ultra-Minimal)### Key Dependencies (Core)

- `tweepy>=4.14.0` - Twitter API client  - `tweepy>=4.14.0` - Twitter API client  

- `eventregistry>=9.1` - News article fetching- `eventregistry>=9.1` - News article fetching

- `google-generativeai>=0.8.0` - Gemini 2.0 Flash Exp with native URL context- `google-generativeai>=0.8.0` - Gemini 2.0 Flash Exp with native URL context

- `requests>=2.25.0` - HTTP client for API calls- `beautifulsoup4>=4.12.0` - HTML parsing for fallback content extraction

- **Note**: Only 4 essential dependencies (60% reduction from 10 packages) for ultra-minimal setup- `newspaper3k>=0.2.8` - Article extraction fallback when URL context unavailable

- **Note**: All dependencies are required for full functionality including advanced AI content generation

### Important Files (Ultra-Simplified)

- `requirements.txt` - Python dependencies (ultra-minimal: 4 packages)### Important Files (Simplified)

- `posted_articles.json` - Tracks posted articles and queue- `requirements.txt` - Python dependencies (streamlined)

- `README.md` - Comprehensive user documentation- `posted_articles.json` - Tracks posted articles and queue

- `rate_limit_cooldown.json` - Manages rate limiting state

**Removed files**: All complex configurations and directories eliminated for ultra-minimal simplicity- `README.md` - Comprehensive user documentation



## Timing Expectations and Cancellation Warnings**Removed files**: Image-related configs and directories eliminated for elegant simplicity



### NEVER CANCEL these operations:## Timing Expectations and Cancellation Warnings

- **Dependency installation**: 30-60 seconds (set timeout to 120+ seconds)

- **Test execution**: Most tests complete in <1 second### NEVER CANCEL these operations:

- **Bot diagnostics**: <3 seconds (ultra-optimized)- **Dependency installation**: 30-60 seconds (set timeout to 120+ seconds)

- **Bot execution**: <10 seconds when working correctly- **Test execution**: Most tests complete in <1 second, but `test_rate_limit_cooldown.py` takes 5+ minutes (set timeout to 10+ minutes)

- **Bot diagnostics**: <5 seconds

### GitHub Actions Timing:- **Bot execution**: <10 seconds when working correctly

- **Scheduled runs**: Every 90 minutes (16 times per day max)

- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)### GitHub Actions Timing:

- **Twitter API limits**: 17 requests per 24 hours- **Scheduled runs**: Every 90 minutes (16 times per day max)

- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)

## Error Patterns and Solutions- **Twitter API limits**: 17 requests per 24 hours



### Missing API Keys (90% of issues)## Error Patterns and Solutions

**Symptoms**: "Missing required environment variables", "User is not logged in"

**Solution**: Set up GitHub repository secrets as documented above### Missing API Keys (90% of issues)

**Symptoms**: "Missing required environment variables", "User is not logged in"

### Rate Limiting  **Solution**: Set up GitHub repository secrets as documented above

**Symptoms**: "429 Too Many Requests", "Rate limit cooldown active"

**Solution**: Bot handles this automatically with progressive cooldowns### Rate Limiting  

**Symptoms**: "429 Too Many Requests", "Rate limit cooldown active"

### No Articles Found**Solution**: Bot handles this automatically with progressive cooldowns

**Symptoms**: "No articles found from EventRegistry"  

**Solution**: Normal when no Bitcoin mining news in last 24 hours### No Articles Found

**Symptoms**: "No articles found from EventRegistry"  

### All Articles Posted**Solution**: Normal when no Bitcoin mining news in last 24 hours

**Symptoms**: "No new articles to post (all articles were already posted)"

**Solution**: Normal behavior - bot tracks posted articles### All Articles Posted

**Symptoms**: "No new articles to post (all articles were already posted)"

## CI/GitHub Actions**Solution**: Normal behavior - bot tracks posted articles



The bot includes a single, focused GitHub Actions workflow:## CI/GitHub Actions



### Main Bot Workflow (`.github/workflows/main.yml`)The bot includes two GitHub Actions workflows:

- **Schedule**: Runs every 90 minutes automatically

- **Purpose**: Fetches Bitcoin mining articles and posts Twitter threads### Main Bot Workflow (`.github/workflows/main.yml`)

- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)- **Schedule**: Runs every 90 minutes automatically

- **Python version**: 3.10 (but works with 3.12+)- **Purpose**: Fetches Bitcoin mining articles and posts Twitter threads

- **Dependencies**: Installs from `requirements.txt`- **Rate limiting**: Progressive cooldowns (2h → 4h → 8h → 24h)

- **Commits**: Updates `posted_articles.json` after successful runs- **Python version**: 3.10 (but works with 3.12+)

- **Ultra-minimal approach**: Single workflow eliminates complexity- **Dependencies**: Installs from `requirements.txt`

- **Commits**: Updates `posted_articles.json` after successful runs

## Development Workflow

### Test & Preview Workflow (`.github/workflows/test-preview.yml`)

### Always run these before committing:- **Trigger**: Manual dispatch only (workflow_dispatch)

1. `python tests/test_bot.py` - Test core functionality- **Purpose**: Test EventRegistry & Gemini APIs without posting to Twitter

2. `python tests/test_integration.py` - Test integration workflows  - **Output**: Creates GitHub issue with complete thread previews

3. `python tools.py diagnose` - Test diagnostics- **Benefits**: Safe testing using production API keys from GitHub secrets

4. `python bot.py --diagnose` - Test bot diagnostics- **Use case**: Preview thread quality before letting main workflow post



### When modifying core functionality:## Development Workflow

- Always test with `python tests/test_bot.py`

- Verify integration with `python tests/test_integration.py`### Always run these before committing:

- Check that all essential tools work: `python tools.py <command>`1. `python tests/test_bot.py` - Test core functionality

2. `python tests/test_integration.py` - Test integration workflows  

### When modifying rate limiting or article processing:3. `python tools.py diagnose` - Test diagnostics

- Test with existing rate limit test files (still work via compatibility layer)4. `python bot.py --diagnose` - Test bot diagnostics

- Verify progressive cooldown behavior in `core.py`

- Check storage operations in the `Storage` class### When modifying core functionality:

- Always test with `python tests/test_bot.py`

### When adding new features:- Verify integration with `python tests/test_integration.py`

- Add to `core.py` for fundamental functionality- Check that all essential tools work: `python tools.py <command>`

- Extend `tools.py` for management interfaces  

- Maintain backward compatibility in `bot.py` wrapper### When modifying rate limiting or article processing:

- Test both new core functionality and legacy compatibility- Test with existing rate limit test files (still work via compatibility layer)

- Verify progressive cooldown behavior in `core.py`

## Repository Structure Reference- Check storage operations in the `Storage` class



```### When adding new features:

.- Add to `core.py` for fundamental functionality

├── .github/- Extend `tools.py` for management interfaces  

│   └── workflows/- Maintain backward compatibility in `bot.py` wrapper

│       └── main.yml                # Single bot workflow (90-minute schedule)- Test both new core functionality and legacy compatibility

├── tests/                          # Ultra-minimal test files (2 total)

│   ├── test_bot.py                 # Core functionality tests (9 tests) ## Repository Structure Reference

│   └── test_integration.py         # Integration workflow tests (3 tests)

├── core.py                         # Complete bot engine (Config, Storage, APIs, Processing)```

├── bot.py                          # Main entry point with backward compatibility layer.

├── tools.py                        # Unified management interface (preview, queue, clean, diagnose)├── .github/

├── requirements.txt                # Python dependencies (ultra-minimal: 4 packages)│   └── workflows/

├── posted_articles.json            # Article tracking (auto-generated)│       ├── main.yml                # Main bot workflow (90-minute schedule)

└── README.md                       # Comprehensive user documentation│       └── test-preview.yml        # Manual testing workflow (creates GitHub issues)

├── tests/                          # Streamlined test files (2 total)

**TOTAL: 10 essential files (79% reduction from 47 files)**│   ├── test_bot.py                 # Core functionality tests (9 tests) 

```│   └── test_integration.py         # Integration workflow tests (3 tests)

├── core.py                         # Complete bot engine (Config, Storage, APIs, Processing)

This is a production-ready Twitter bot with **ultra-minimal 10-file core architecture**, achieving 79% file reduction while maintaining robust error handling, rate limiting, and comprehensive testing. All tests are streamlined into just 2 elegant test files. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.├── bot.py                          # Main entry point with backward compatibility layer
├── tools.py                        # Unified management interface (preview, queue, clean, diagnose)
├── requirements.txt                # Python dependencies (streamlined)
├── posted_articles.json            # Article tracking (auto-generated)
├── rate_limit_cooldown.json        # Rate limit state (auto-generated) 
└── README.md                       # Comprehensive user documentation
```

This is a production-ready Twitter bot with **clean 5-file core architecture**, achieving 89% file reduction (47→5 core files) while maintaining robust error handling, rate limiting, and comprehensive testing. All tests are streamlined into just 2 elegant test files. The codebase is designed to be maintainable and well-documented for GitHub Copilot assistance.