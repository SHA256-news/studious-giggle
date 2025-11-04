# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

Setup
- pip install -r requirements.txt

Diagnostics and running
- python bot.py --diagnose
- python bot.py

Management tools
- python tools.py diagnose
- python tools.py preview
- python tools.py queue
- python tools.py history            # show last 10 (or: python tools.py history 20)
- python tools.py clean
- python tools.py test               # live EventRegistry + Gemini check (no tweets)

Tests (self-contained runners; no pytest needed)
- python tests/test_bot.py           # core tests
- python tests/test_integration.py   # integration tests
- Run a single test method (example):
  - python - <<'PY'
import importlib, sys, os
sys.path.insert(0, os.getcwd())
mod = importlib.import_module('tests.test_bot')
t = mod.TestBot(); t.test_text_processing(); print('ok')
PY

GitHub Actions
- Workflow: .github/workflows/main.yml (scheduled every 90 minutes). It runs diagnostics, the bot, then commits updated posted_articles.json.

Required environment (set locally or as GitHub Secrets)
- TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
- EVENTREGISTRY_API_KEY
- GEMINI_API_KEY (mandatory; bot will not publish without it)

## High-level Architecture

Single-module core (core.py)
- Config: central settings and env loading; posted_articles.json and rate_limit_cooldown.json file paths.
- Storage: atomic JSON load/save; posted_data schema includes posted_uris, queued_articles, posted_articles_history, last_run_time.
- TimeManager: minimum-interval checks and cooldown windows.
- ContentSimilarity: deduplication via title Jaccard, content fingerprinting, and date window.
- GeminiClient: generates headline + 3-point summary using Gemini 2.5 Flash with URL context; enforces:
  - tools=[{"url_context": {}}] configuration (simple dict form)
  - URL retrieval status checks; raises URLRetrievalError on fetch/access failures
- NewsAPI: EventRegistry client; fetches recent Bitcoin mining articles; multi-layer relevance filter (public miners, AI+mining, political/regulatory, promo/scam exclusions).
- TwitterAPI: tweepy client; post_tweet and post_thread with 429 handling.
- TextProcessor: builds thread: headline + summary (combined if <= 280, else split), final tweet is the URL; returns None if Gemini unavailable (bot should retry later).
- BitcoinMiningBot: orchestrates run() with order: diagnostics → cooldown/min-interval → fetch → deduplicate → post first viable article as a thread → queue remaining; URLRetrievalError causes skip without cooldown; only Twitter 429 sets cooldown.

Entrypoint and compatibility (bot.py)
- BitcoinMiningNewsBotLegacy wraps BitcoinMiningBot to preserve older attributes/methods used by scripts/tests.

Operational tools (tools.py)
- diagnose, preview next tweet, simple queue display, interactive clean, posted history viewer, live API test. Import paths are resilient; diagnostics check presence of core files and basic env.

Tests
- tests/test_bot.py and tests/test_integration.py are self-running scripts (no pytest). They mock external APIs; do not require real keys. Integration test verifies thread structure and queueing behavior.

Persistent data
- posted_articles.json: queue + history + posted URL list.
- rate_limit_cooldown.json: cooldown window persisted between runs.

Docs and guardrails
- docs/api/: permanent API references (eventregistry.md, gemini.md, quick-reference.md, README.md). Consult before changing API code.
- docs/api/gemini-url-context-CORRECT.md and GEMINI-API-NEVER-FORGET.md: definitive guidance for Gemini URL context. Always use tools=[{"url_context": {}}]; do not use types.Tool(...).

## Notes from Copilot instructions (important excerpts)
- Ultra-minimal architecture: core.py as the engine; bot.py for compatibility; tools.py for operations.
- Gemini is mandatory; the bot will not publish without AI enhancement and should retry on later runs.
- URL retrieval failures (blocked/403/404) must not trigger cooldown; skip the article and continue.
- Only Twitter API rate limits (429; 17 posts/day) trigger progressive cooldown and persistence to rate_limit_cooldown.json.
- Before refactoring API code, copy patterns from docs/api/quick-reference.md and the Gemini URL context docs referenced above.
