# Bitcoin Mining News Bot - Clean Architecture Edition

**Automated Bitcoin mining news aggregation and Twitter posting with clean, maintainable architecture.**

## Overview

This bot automatically:
- Fetches Bitcoin mining news from EventRegistry API
- Filters articles for Bitcoin mining relevance
- Generates AI-enhanced headlines and summaries using Gemini
- Posts formatted Twitter threads
- Tracks posting history and manages article queues

**Version 2.0** features a complete architectural rebuild with:
- Clean separation of concerns across layers
- Dependency injection for testability
- Interface-based design for easy substitution
- Comprehensive test coverage with no external dependencies

## Quick Start

### Prerequisites

- Python 3.10+
- API Keys for:
  - Twitter/X (API key, secret, access token, access token secret)
  - EventRegistry (news aggregation)
  - Google Gemini (AI generation)

### Installation

```bash
# Clone repository
git clone https://github.com/SHA256-news/studious-giggle.git
cd studious-giggle

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TWITTER_API_KEY="your_twitter_api_key"
export TWITTER_API_SECRET="your_twitter_api_secret"
export TWITTER_ACCESS_TOKEN="your_twitter_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_twitter_access_token_secret"
export EVENTREGISTRY_API_KEY="your_eventregistry_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

### Usage

```bash
# Run the bot
python main.py run

# Check configuration and status
python main.py diagnose

# Preview next article in queue
python main.py preview

# View posting history
python main.py history

# Clear article queue
python main.py clean

# Show help
python main.py help
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

### Layer Structure

```
src/
├── domain/              # Pure business logic (no dependencies)
│   ├── entities.py      # Article, Tweet, Thread, PostedArticle
│   └── value_objects.py # ContentFingerprint, TitleSignature
├── adapters/            # External service interfaces & implementations
│   ├── interfaces.py    # Abstract base classes
│   ├── eventregistry_adapter.py
│   ├── gemini_adapter.py
│   ├── twitter_adapter.py
│   └── json_storage.py
├── services/            # Business logic services
│   ├── filtering.py     # BitcoinMiningFilter, DuplicateDetector
│   └── thread_builder.py
├── app/                 # Application orchestration
│   └── bot.py          # BitcoinMiningNewsBot
└── config.py           # Configuration management
```

### Key Design Principles

1. **Dependency Injection** - No hard-wired dependencies or singletons
2. **Interface-Based** - All external services behind abstract interfaces
3. **Immutability** - Domain entities are immutable (frozen dataclasses)
4. **Testability** - Easy to test with fake implementations
5. **Single Responsibility** - Each module has one clear purpose

## Features

### Content Filtering

- **Bitcoin Mining Focus**: Multi-layer filtering with public mining companies, core mining terms, and related concepts
- **Duplicate Detection**: Content-based similarity analysis to prevent posting duplicates
- **Quality Validation**: Ensures articles meet minimum relevance thresholds

### AI-Powered Content

- **Smart Headlines**: Professional, action-oriented headlines (60-80 chars)
- **Complementary Summaries**: Bullet-point summaries with additional details (≤180 chars)
- **Graceful Degradation**: Works without AI provider (simple title + URL)

### Thread Generation

- **Intelligent Threading**: Combines headline + summary if ≤280 chars, otherwise separate tweets
- **URL Placement**: Article URL always in final tweet
- **Character Optimization**: Maximum information density while respecting Twitter limits

### Queue Management

- **Persistent Queues**: Articles queue across bot runs
- **History Tracking**: Complete posting history with metadata
- **Interactive Tools**: Preview, clean, and manage queued content

## Testing

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test suites
python -m unittest tests.test_domain
python -m unittest tests.test_filtering
python -m unittest tests.test_new_integration

# Test with coverage (if installed)
coverage run -m unittest discover tests/
coverage report
```

### Test Structure

- **test_domain.py**: Unit tests for domain entities and value objects
- **test_filtering.py**: Unit tests for filtering services
- **test_new_integration.py**: Integration tests with fake adapters
- **test_doubles.py**: Fake implementations for testing

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TWITTER_API_KEY` | Yes | Twitter API key |
| `TWITTER_API_SECRET` | Yes | Twitter API secret |
| `TWITTER_ACCESS_TOKEN` | Yes | Twitter access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Yes | Twitter access token secret |
| `EVENTREGISTRY_API_KEY` | Yes | EventRegistry API key |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `MAX_ARTICLES` | No | Maximum articles to fetch (default: 20) |
| `MIN_INTERVAL_MINUTES` | No | Minimum minutes between runs (default: 90) |
| `STORAGE_FILE` | No | Storage file path (default: posted_articles.json) |

### GitHub Actions

The bot runs automatically via GitHub Actions:

```yaml
schedule:
  - cron: '0 */90 * * *'  # Every 90 minutes
```

Configure secrets in GitHub repository settings.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Adding New Features

1. **New Adapters**: Implement interface from `src/adapters/interfaces.py`
2. **New Services**: Add to `src/services/` following single responsibility principle
3. **New Commands**: Extend `main.py` command handlers

### Code Style

- Type hints for all functions
- Docstrings for public APIs
- Immutable entities where possible
- Comprehensive test coverage

## Migration from v1.0

The 2.0 architecture is a complete rewrite. Key changes:

- **Old**: Monolithic `core.py` with 1,500+ lines
- **New**: Layered architecture with clear boundaries

- **Old**: Hard-coded dependencies and singletons
- **New**: Dependency injection throughout

- **Old**: "NEVER CHANGE" warnings on prompts
- **New**: Configurable, maintainable prompt management

- **Old**: Difficult to test without API keys
- **New**: Full test coverage with fake adapters

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- EventRegistry for news aggregation API
- Google Gemini for AI content generation
- Twitter/X API for social media posting
