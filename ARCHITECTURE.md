# Architecture Documentation

## Overview

The Bitcoin Mining News Bot follows **Clean Architecture** principles with clear separation between business logic, external services, and application orchestration.

## Core Principles

### 1. Dependency Rule

Dependencies point inward toward domain logic:

```
main.py → app → services → domain
           ↓
       adapters (implementations)
           ↓
       adapters (interfaces)
```

- **Domain** has zero external dependencies
- **Services** depend only on domain
- **Adapters** implement interfaces and can depend on external libraries
- **App** orchestrates using interfaces (not concrete implementations)

### 2. Dependency Injection

No singletons or global state. All dependencies injected through constructors:

```python
bot = BitcoinMiningNewsBot(
    news_provider=EventRegistryAdapter(api_key),
    storage=JSONStorage(filepath),
    publisher=TwitterAdapter(...),
    ai_provider=GeminiAdapter(api_key)
)
```

This enables:
- Easy testing with fakes
- Runtime configuration
- Multiple bot instances with different configs

### 3. Interface Segregation

Small, focused interfaces:

- `NewsProvider`: Fetches articles
- `AIProvider`: Generates content
- `SocialMediaPublisher`: Posts threads
- `ArticleStorage`: Persists data

Each can be tested, mocked, or swapped independently.

## Layer Details

### Domain Layer (`src/domain/`)

**Pure Python business logic with zero external dependencies.**

#### Entities (`entities.py`)

Immutable business objects:

- `Article`: News article with metadata
- `Tweet`: Single tweet with character validation
- `Thread`: Collection of tweets with article reference
- `PostedArticle`: Record of successful posting

**Design decisions:**
- Frozen dataclasses for immutability
- Validation in `__post_init__`
- Domain logic (e.g., `article.age_hours`)
- Serialization methods (`to_dict`, `from_dict`)

#### Value Objects (`value_objects.py`)

Immutable comparison and analysis objects:

- `ContentFingerprint`: For duplicate detection
- `TitleSignature`: For title similarity

**Design decisions:**
- Immutable (frozen dataclasses)
- Value-based equality
- Self-contained logic

### Adapters Layer (`src/adapters/`)

**Interfaces and implementations for external services.**

#### Interfaces (`interfaces.py`)

Abstract base classes defining contracts:

```python
class NewsProvider(ABC):
    @abstractmethod
    def fetch_articles(self, keywords, max_results, since_date) -> List[Article]:
        pass

class AIProvider(ABC):
    @abstractmethod
    def generate_headline(self, article, max_length) -> Optional[str]:
        pass
    
    @abstractmethod
    def generate_summary(self, article, headline, max_length) -> Optional[str]:
        pass
```

**Benefits:**
- Code depends on interfaces, not implementations
- Easy to swap implementations
- Straightforward to mock for tests

#### Implementations

Each adapter wraps an external service:

**EventRegistryAdapter**:
- Wraps EventRegistry Python SDK
- Lazy client initialization
- Converts API responses to domain `Article` objects

**GeminiAdapter**:
- Wraps Google Gemini API
- Handles prompt construction
- Response parsing and cleaning
- URL retrieval error detection

**TwitterAdapter**:
- Wraps Tweepy library
- Thread posting with reply chains
- Authentication validation

**JSONStorage**:
- File-based persistence
- Atomic writes with backup
- Graceful schema migration

### Services Layer (`src/services/`)

**Business logic services that orchestrate domain operations.**

#### BitcoinMiningFilter (`filtering.py`)

Determines Bitcoin mining relevance:

```python
class BitcoinMiningFilter:
    PUBLIC_MINERS = {...}  # Auto-approve
    MINING_TERMS = {...}   # Core terms
    EXCLUSION_TERMS = {...}  # Reject
    
    def is_relevant(self, article: Article) -> bool:
        # Multi-layer filtering logic
```

**Configurable via constructor:**
- `require_public_miner`
- `min_mining_terms`
- `check_exclusions`

#### DuplicateDetector (`filtering.py`)

Detects duplicate articles:

- Uses `ContentFingerprint` and `TitleSignature`
- Maintains sliding time window
- Configurable similarity thresholds

**Stateful design:**
- Accumulates seen articles
- Auto-cleans old articles

#### ThreadBuilder (`thread_builder.py`)

Builds Twitter threads from articles:

```python
class ThreadBuilder:
    def build_thread(self, article) -> Optional[Thread]:
        # Try AI-enhanced first
        # Fallback to simple if AI unavailable
```

**Graceful degradation:**
- Works with or without AI provider
- Simple fallback: title + URL

### Application Layer (`src/app/`)

**Orchestrates the bot pipeline.**

#### BitcoinMiningNewsBot (`bot.py`)

Main application class:

```python
class BitcoinMiningNewsBot:
    def __init__(
        self,
        news_provider: NewsProvider,
        storage: ArticleStorage,
        publisher: SocialMediaPublisher,
        ai_provider: Optional[AIProvider]
    ):
        # Initialize services
        self.mining_filter = BitcoinMiningFilter()
        self.duplicate_detector = DuplicateDetector()
        self.thread_builder = ThreadBuilder(ai_provider)
    
    def run(self, keywords, max_articles) -> bool:
        # 1. Fetch articles
        # 2. Filter for relevance
        # 3. Detect duplicates
        # 4. Post from queue
        # 5. Update storage
```

**Pipeline:**
1. Fetch articles from news provider
2. Filter for Bitcoin mining relevance
3. Check for duplicates
4. Add to queue
5. Post next queued article
6. Save state

**Testability:**
- All dependencies injected
- Returns boolean for success/failure
- Separate diagnostic method

### Configuration (`src/config.py`)

Environment-based configuration:

```python
@dataclass
class BotConfig:
    # API Keys
    twitter_api_key: str
    # ... other required fields
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        # Load from environment
    
    def validate(self) -> List[str]:
        # Return validation errors
```

**Design:**
- Single source of truth
- Validation on demand
- Safe string representation (no leaked keys)

### Entry Point (`main.py`)

CLI with dependency injection:

```python
def create_bot(config: BotConfig) -> BitcoinMiningNewsBot:
    # Create adapters
    news_provider = EventRegistryAdapter(config.eventregistry_api_key)
    storage = JSONStorage(config.storage_file)
    # ...
    
    # Inject dependencies
    return BitcoinMiningNewsBot(
        news_provider=news_provider,
        storage=storage,
        publisher=publisher,
        ai_provider=ai_provider
    )
```

**Commands:**
- `run`: Execute bot pipeline
- `diagnose`: Check configuration and status
- `preview`: Show next queued article
- `history`: View posting history
- `clean`: Clear queue

## Data Flow

### Normal Run

```
1. main.py loads config from env
2. Creates adapters (EventRegistry, Gemini, Twitter, Storage)
3. Creates bot with dependency injection
4. Bot.run() executes:
   
   a. Check minimum interval (via Storage)
   b. Fetch articles (via NewsProvider)
   c. Filter relevance (via BitcoinMiningFilter)
   d. Detect duplicates (via DuplicateDetector)
   e. Add to queue (via Storage)
   f. Pop next from queue
   g. Build thread (via ThreadBuilder + AIProvider)
   h. Post thread (via Publisher)
   i. Save posted article (via Storage)
   j. Update last run time (via Storage)
```

### Testing Flow

```
1. Test creates fake adapters (no real APIs)
2. Injects fakes into bot
3. Configures fake behavior (articles to return, etc.)
4. Runs bot
5. Asserts on fake adapter calls and state
```

## Testing Strategy

### Unit Tests

Test each layer in isolation:

- **Domain**: Pure logic, no mocks needed
- **Services**: Use domain objects, no external deps
- **Adapters**: Mock underlying libraries (EventRegistry, Tweepy, etc.)

### Integration Tests

Test complete pipeline with **fakes** (not mocks):

```python
# Create fake adapters
news_provider = FakeNewsProvider()
news_provider.articles_to_return = [test_article]

storage = FakeStorage()
publisher = FakePublisher()
ai_provider = FakeAIProvider()

# Inject into bot
bot = BitcoinMiningNewsBot(
    news_provider=news_provider,
    storage=storage,
    publisher=publisher,
    ai_provider=ai_provider
)

# Run and assert
bot.run(keywords=["bitcoin mining"])
assert publisher.post_thread_called
```

**Benefits:**
- No API keys required
- Fast execution
- Full pipeline coverage
- Easy to reproduce scenarios

### Test Doubles

`tests/test_doubles.py` provides:

- `FakeNewsProvider`
- `FakeAIProvider`
- `FakePublisher`
- `FakeStorage`
- `create_test_article()` helper

All implement real interfaces, making substitution seamless.

## Design Patterns Used

### Repository Pattern

`ArticleStorage` abstracts persistence:
- Load/save posted articles
- Load/save queue
- Get/set last run time

Implementation can be swapped (JSON, SQL, Redis, etc.) without changing bot logic.

### Adapter Pattern

External services wrapped behind interfaces:
- `EventRegistryAdapter` wraps EventRegistry SDK
- `GeminiAdapter` wraps Gemini API
- `TwitterAdapter` wraps Tweepy

### Factory Pattern

`create_bot()` in `main.py` constructs bot with all dependencies.

### Strategy Pattern

`BitcoinMiningFilter` is configurable strategy for relevance determination.

### Builder Pattern

`ThreadBuilder` constructs complex `Thread` objects with optional AI enhancement.

## Extension Points

### Adding New News Provider

1. Implement `NewsProvider` interface
2. Return `List[Article]`
3. Inject into bot

Example: NewsAPI, Google News, RSS feeds

### Adding New AI Provider

1. Implement `AIProvider` interface
2. Return `Optional[str]` for headline/summary
3. Inject into bot

Example: OpenAI, Claude, local models

### Adding New Storage Backend

1. Implement `ArticleStorage` interface
2. Handle load/save operations
3. Inject into bot

Example: PostgreSQL, MongoDB, S3

### Adding New Publishing Platform

1. Implement `SocialMediaPublisher` interface
2. Handle thread posting
3. Inject into bot

Example: Mastodon, Bluesky, Threads

## Comparison to Old Architecture

| Aspect | Old (v1.0) | New (v2.0) |
|--------|-----------|-----------|
| **Structure** | Monolithic `core.py` (1,500+ lines) | Layered architecture (10-15 files) |
| **Dependencies** | Hard-coded, singletons | Dependency injection |
| **Testing** | Difficult, requires mocking singletons | Easy with fake adapters |
| **Extensibility** | Risky, "NEVER CHANGE" warnings | Safe, interface-based |
| **Maintainability** | All logic intertwined | Clear separation of concerns |
| **Configuration** | Scattered across modules | Centralized in `config.py` |
| **Prompts** | Hard-coded with warnings | Encapsulated in adapter |

## Future Enhancements

Potential improvements (all achievable without major refactoring):

1. **Multiple Publishers**: Post to Twitter + Mastodon simultaneously
2. **Custom Filters**: User-defined relevance rules via config
3. **Scheduling**: Built-in scheduler instead of GitHub Actions
4. **Metrics**: Track posting success rates, API usage
5. **Webhooks**: Notify on errors or successful posts
6. **Database Storage**: PostgreSQL instead of JSON
7. **Web Dashboard**: View queue, history, and diagnostics

All enabled by the clean architecture!
