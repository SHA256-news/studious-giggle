# Cleanup Guide - Old Files to Delete

## ❌ DELETE These Old Files (v1.0 Architecture)

### Old Code Files
- `bot.py` - Replaced by `main.py` with clean architecture
- `core.py` - Split into `src/domain/`, `src/adapters/`, `src/services/`, `src/app/`
- `tools.py` - Functionality moved to `main.py` commands

### Old Documentation Files  
- `BUG-FIXES-OCTOBER-2025.md` - Historical, no longer relevant
- `GEMINI-API-NEVER-FORGET.md` - Information now in `src/adapters/gemini_adapter.py`
- `GEMINI_URL_CONTEXT_FIX_OCTOBER_2025.md` - Information now in adapter code
- `PROMPT-IMPROVEMENTS-NEVER-FORGET.md` - Prompts now in `src/adapters/gemini_adapter.py`
- `.github/copilot-instructions.md` - Outdated instructions

### Old Test Files
- `show_improved_prompts.py` - No longer needed
- `test_gemini_fix.py` - Replaced by new test suite
- `test_gemini_headlines.py` - Replaced by new test suite

### Old README
- Keep for reference, but rename to `README-OLD.md` if you want

---

## ✅ KEEP These Files (v2.0 Architecture)

### New Code (src/)
- `src/domain/entities.py`
- `src/domain/value_objects.py`
- `src/domain/__init__.py`
- `src/adapters/interfaces.py`
- `src/adapters/eventregistry_adapter.py`
- `src/adapters/gemini_adapter.py`
- `src/adapters/twitter_adapter.py`
- `src/adapters/json_storage.py`
- `src/adapters/__init__.py`
- `src/services/filtering.py`
- `src/services/thread_builder.py`
- `src/services/__init__.py`
- `src/app/bot.py`
- `src/app/__init__.py`
- `src/config.py`
- `src/__init__.py`

### New Entry Point
- `main.py` - New CLI with dependency injection

### New Tests
- `tests/test_doubles.py`
- `tests/test_domain.py`
- `tests/test_filtering.py`
- `tests/test_new_integration.py`

### New Documentation
- `README-NEW.md` - New user guide
- `ARCHITECTURE.md` - Architecture documentation
- `CONTRIBUTING.md` - Development guidelines
- `MIGRATION.md` - Migration guide

### Keep These
- `requirements.txt` - Dependencies (same)
- `posted_articles.json` - Data file
- `.github/workflows/` - GitHub Actions (may need updating)
- `.gitignore`
- `LICENSE`
- `docs/api/` - API documentation

---

## Commands to Delete Old Files

```bash
# Delete old code files
rm bot.py core.py tools.py

# Delete old documentation
rm BUG-FIXES-OCTOBER-2025.md
rm GEMINI-API-NEVER-FORGET.md
rm GEMINI_URL_CONTEXT_FIX_OCTOBER_2025.md
rm PROMPT-IMPROVEMENTS-NEVER-FORGET.md
rm .github/copilot-instructions.md

# Delete old test files
rm show_improved_prompts.py
rm test_gemini_fix.py
rm test_gemini_headlines.py

# Optional: Keep old tests for reference but move them
mkdir -p old_tests
mv tests/test_bot.py old_tests/ 2>/dev/null || true
mv tests/test_integration.py old_tests/ 2>/dev/null || true

# Optional: Rename old README
mv README.md README-OLD.md
mv README-NEW.md README.md
```

---

## After Cleanup

Your directory should look like:

```
studious-giggle/
├── .github/
│   └── workflows/
├── docs/
│   └── api/
├── src/
│   ├── domain/
│   ├── adapters/
│   ├── services/
│   ├── app/
│   └── config.py
├── tests/
│   ├── test_doubles.py
│   ├── test_domain.py
│   ├── test_filtering.py
│   └── test_new_integration.py
├── main.py
├── requirements.txt
├── posted_articles.json
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── MIGRATION.md
├── LICENSE
└── .gitignore
```

Clean, organized, maintainable! 🎉
