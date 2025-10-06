# API Documentation

This directory contains permanent API reference documentation to prevent forgetting API details during refactoring.

## 📚 Available References

### Core APIs
- **[EventRegistry API](./eventregistry.md)** - Complete Python SDK reference for news article fetching
- **[Gemini API](./gemini.md)** - Complete Google Gemini AI reference for content generation  
- **[Quick Reference](./quick-reference.md)** - Copy-paste ready code snippets for common operations

## 🎯 Usage During Refactoring

### Before Refactoring Any API Code:
1. **Read the specific API reference first** (`eventregistry.md` or `gemini.md`)
2. **Check the quick reference** (`quick-reference.md`) for proven patterns
3. **Copy tested patterns** instead of rewriting from memory
4. **Test changes** against the documented examples

### Code Comments Point Here:
Look for these references in `core.py`:
```python
class NewsAPI:
    """
    📚 API REFERENCE: /docs/api/eventregistry.md
    🔗 Quick Reference: /docs/api/quick-reference.md
    """

class GeminiClient:
    """
    📚 API REFERENCE: /docs/api/gemini.md  
    🔗 Quick Reference: /docs/api/quick-reference.md
    """
```

## 🔄 When to Update Documentation

- **New API features discovered** - Add to relevant reference file
- **Breaking changes in dependencies** - Update examples and patterns
- **New error patterns found** - Document in error handling sections
- **Performance optimizations** - Update best practices

## 📋 Quick Links for Common Tasks

| Task | Reference Section |
|------|------------------|
| Fetch Bitcoin mining articles | [EventRegistry - Bot Patterns](./eventregistry.md#common-patterns-used-in-bot) |
| Generate AI headlines | [Gemini - Headline Generation](./gemini.md#1-headline-generation-with-url-context) |
| Create Twitter threads | [Quick Reference - Threading](./quick-reference.md#twitter-threading-logic) |
| Handle API errors | [Quick Reference - Error Handling](./quick-reference.md#error-handling-patterns) |
| Filter Bitcoin content | [Quick Reference - Mining Filter](./quick-reference.md#bitcoin-mining-filter-pattern) |

## 🧪 Testing API Changes

Always test API changes with these patterns:

```python
# Test EventRegistry connection
try:
    test_concept = er.getConceptUri("Bitcoin")
    print(f"✅ EventRegistry connected: {test_concept}")
except Exception as e:
    print(f"❌ EventRegistry failed: {e}")

# Test Gemini connection  
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say 'SUCCESS'"
    )
    print(f"✅ Gemini connected: {response.text}")
except Exception as e:
    print(f"❌ Gemini failed: {e}")
```

## 📝 Maintenance Notes

- **Last Updated**: 2025-01-05
- **EventRegistry Version**: eventregistry>=9.1
- **Gemini Version**: google-genai>=0.1.0
- **Python Version**: 3.10+

---

**Remember**: These docs are your refactoring safety net. Always reference them before making API changes!