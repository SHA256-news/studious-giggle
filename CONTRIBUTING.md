# Contributing to Bitcoin Mining News Bot

Thank you for your interest in contributing! This guide will help you understand the project structure and development workflow.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/SHA256-news/studious-giggle.git
cd studious-giggle

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black mypy
```

### Project Structure

```
src/
├── domain/         # Pure business logic (no external deps)
├── adapters/       # External service interfaces & implementations
├── services/       # Business logic services
├── app/           # Application orchestration
└── config.py      # Configuration management

tests/
├── test_domain.py       # Domain entity tests
├── test_filtering.py    # Service tests
├── test_new_integration.py  # Integration tests
└── test_doubles.py      # Test fake implementations

main.py            # CLI entry point
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Follow the architecture principles:

- **Domain layer**: Pure Python, no external dependencies
- **Adapters**: Implement interfaces, wrap external services
- **Services**: Business logic using domain objects
- **App**: Orchestrate using dependency injection

### 3. Write Tests

Every change should include tests:

```python
# tests/test_your_feature.py
import unittest
from src.domain import Article
from tests.test_doubles import create_test_article

class TestYourFeature(unittest.TestCase):
    def test_feature_behavior(self):
        # Arrange
        article = create_test_article()
        
        # Act
        result = your_function(article)
        
        # Assert
        self.assertEqual(result, expected_value)
```

### 4. Run Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_your_feature

# Run with coverage
coverage run -m unittest discover tests/
coverage report
```

### 5. Format Code

```bash
# Format with black
black src/ tests/ main.py

# Type check
mypy src/
```

### 6. Commit Changes

```bash
git add .
git commit -m "Add feature: description of change"
```

Use clear commit messages:
- `Add feature: ...`
- `Fix bug: ...`
- `Refactor: ...`
- `Update docs: ...`

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Adding New Features

### Adding a New Adapter

Example: Adding a new news provider

1. **Define interface** (if not exists):

```python
# src/adapters/interfaces.py
class NewsProvider(ABC):
    @abstractmethod
    def fetch_articles(self, keywords, max_results, since_date) -> List[Article]:
        pass
```

2. **Implement adapter**:

```python
# src/adapters/yournews_adapter.py
from src.domain import Article
from src.adapters.interfaces import NewsProvider

class YourNewsAdapter(NewsProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    def fetch_articles(self, keywords, max_results, since_date) -> List[Article]:
        # Implementation
        pass
```

3. **Create test double**:

```python
# tests/test_doubles.py
class FakeYourNewsProvider(NewsProvider):
    def __init__(self):
        self.articles_to_return = []
    
    def fetch_articles(self, keywords, max_results, since_date):
        return self.articles_to_return
```

4. **Write tests**:

```python
# tests/test_yournews_adapter.py
import unittest
from tests.test_doubles import FakeYourNewsProvider

class TestYourNewsAdapter(unittest.TestCase):
    def test_fetch_articles(self):
        provider = FakeYourNewsProvider()
        # Test implementation
```

5. **Update factory**:

```python
# main.py
def create_bot(config):
    news_provider = YourNewsAdapter(api_key=config.your_news_api_key)
    # ... rest of setup
```

### Adding a New Service

Example: Adding advanced filtering

1. **Create service class**:

```python
# src/services/your_filter.py
from src.domain import Article

class YourFilter:
    def __init__(self, threshold: float):
        self.threshold = threshold
    
    def is_valid(self, article: Article) -> bool:
        # Implementation
        pass
```

2. **Write tests**:

```python
# tests/test_your_filter.py
import unittest
from src.services.your_filter import YourFilter
from tests.test_doubles import create_test_article

class TestYourFilter(unittest.TestCase):
    def test_valid_article(self):
        filter = YourFilter(threshold=0.5)
        article = create_test_article(...)
        self.assertTrue(filter.is_valid(article))
```

3. **Integrate into bot**:

```python
# src/app/bot.py
class BitcoinMiningNewsBot:
    def __init__(self, ...):
        # ...
        self.your_filter = YourFilter(threshold=0.7)
    
    def _filter_articles(self, articles):
        # Use your_filter
```

### Adding a New Command

Example: Adding `export` command

1. **Add command handler**:

```python
# main.py
def cmd_export(config: BotConfig) -> int:
    """Export posted articles to CSV."""
    try:
        storage = JSONStorage(filepath=config.storage_file)
        posted = storage.load_posted_articles()
        
        # Export logic
        
        return 0
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1
```

2. **Register command**:

```python
# main.py, in main() function
def main():
    # ...
    if command == "export":
        return cmd_export(config)
```

3. **Update help text**:

```python
# main.py
def show_help():
    print("""
    ...
    export      Export posted articles to CSV
    ...
    """)
```

## Testing Guidelines

### Unit Tests

- Test one thing at a time
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- No external dependencies

### Integration Tests

- Use fake adapters from `test_doubles.py`
- Test complete workflows
- Verify adapter interactions
- Fast execution (no API calls)

### Test Coverage

Aim for:
- Domain: 100%
- Services: >90%
- Adapters: >80%
- App: >80%

### Writing Good Tests

```python
def test_descriptive_name_of_what_is_tested(self):
    """Test description explaining purpose."""
    # Arrange - Set up test data
    article = create_test_article(title="Test")
    filter = BitcoinMiningFilter()
    
    # Act - Execute the code
    result = filter.is_relevant(article)
    
    # Assert - Verify results
    self.assertTrue(result)
```

## Code Style

### Python Style

Follow PEP 8:
- 4 spaces for indentation
- Max line length: 100 characters
- Descriptive variable names

Use type hints:

```python
def fetch_articles(
    self,
    keywords: List[str],
    max_results: int = 20
) -> List[Article]:
    pass
```

### Docstrings

Use Google style:

```python
def complex_function(param1: str, param2: int) -> bool:
    """
    One-line summary.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Imports

Order:
1. Standard library
2. Third-party libraries
3. Local imports

```python
import logging
from datetime import datetime
from typing import List, Optional

import tweepy
from eventregistry import EventRegistry

from src.domain import Article
from src.adapters.interfaces import NewsProvider
```

## Architecture Principles

### Dependency Rule

**Dependencies point inward toward domain:**

```
main.py → app → services → domain
           ↓
       adapters
```

- Domain has no external dependencies
- Services depend only on domain
- Adapters implement interfaces
- App uses interfaces (not concrete classes)

### Immutability

Domain entities should be immutable:

```python
@dataclass(frozen=True)
class Article:
    uri: str
    title: str
    # ...
```

### Interface Segregation

Keep interfaces small and focused:

```python
class AIProvider(ABC):
    @abstractmethod
    def generate_headline(self, article) -> Optional[str]:
        pass
    
    @abstractmethod  
    def generate_summary(self, article, headline) -> Optional[str]:
        pass
```

### Dependency Injection

No singletons or global state:

```python
# Good
class Bot:
    def __init__(self, storage: ArticleStorage):
        self.storage = storage

# Bad
class Bot:
    def __init__(self):
        self.storage = Storage()  # Hard-coded dependency
```

## Common Tasks

### Running Locally

```bash
# Set environment variables
export TWITTER_API_KEY="test_key"
export EVENTREGISTRY_API_KEY="test_key"
export GEMINI_API_KEY="test_key"
# ... other required vars

# Run bot
python main.py run

# Check diagnostics
python main.py diagnose
```

### Debugging

Add logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Performance

- Use lazy initialization for expensive objects
- Cache expensive computations
- Profile with `cProfile` if needed

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Type hints added
- [ ] Documentation updated
- [ ] ARCHITECTURE.md updated (if architecture changed)

### PR Description

Include:
1. **What**: What does this PR do?
2. **Why**: Why is this change needed?
3. **How**: How does it work?
4. **Testing**: How was it tested?

### Review Process

1. Automated tests run on PR
2. Maintainer reviews code
3. Address feedback
4. Approval and merge

## Getting Help

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Questions**: Add comment in your PR

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
