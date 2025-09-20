# Bitcoin Mining News Analysis Reports

This directory contains AI-generated analysis reports for Bitcoin mining news articles posted by the bot.

## Report Format

Each report is generated using Google's Gemini AI and includes:
- Article metadata (title, URL, timestamp)
- AI analysis of the content
- Sentiment analysis
- Key insights about the Bitcoin mining industry

## File Naming Convention

Reports are named using the pattern: `YYYYMMDD_HHMMSS_article_title_slug.md`

Example: `20250920_143022_bitcoin_mining_difficulty_reaches_new_high.md`

## Configuration

Reports are generated when the `GEMINI_API_KEY` environment variable is configured in the GitHub Actions secrets. If this key is not available, the bot will continue to function normally but will not generate analysis reports.