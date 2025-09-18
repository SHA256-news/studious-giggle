# Bitcoin Mining News Bot - Why No Tweets Were Posted?

This document explains how to diagnose and fix issues when the Bitcoin Mining News Bot doesn't post any tweets.

## Quick Diagnosis

Run this command to get an instant diagnosis:

```bash
python bot.py --diagnose
```

Or use the detailed diagnostic script:

```bash
python diagnose_bot.py
```

## Most Common Issues

### 1. Missing API Keys (90% of cases)

**Error Messages:**
- "Missing required environment variables"
- "User is not logged in. Unable to execute the request"

**Fix:**
1. Go to GitHub repository settings
2. Navigate to Settings > Secrets and variables > Actions  
3. Add these secrets:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET` 
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `EVENTREGISTRY_API_KEY`

### 2. All Articles Already Posted

**Message:** "No new articles to post (all articles were already posted)"

**Explanation:** This is normal! The bot tracks posted articles and won't repost them.

### 3. No Recent Articles

**Message:** "No articles found from EventRegistry"

**Causes:**
- No Bitcoin mining news in last 24 hours
- EventRegistry API issues
- Wrong API key

### 4. Rate Limiting

**Messages:** 
- "Found X new articles but couldn't post any due to rate limiting"
- "Rate limit cooldown active. Skipping run. X minutes remaining."

**Fix:** 
- The bot automatically retries with exponential backoff during a single run
- If rate limiting persists, wait up to 1 hour for the cooldown period to end
- The bot will automatically resume normal operation after the cooldown

## GitHub Actions Logs

To check what happened in GitHub Actions:

1. Go to your repository
2. Click "Actions" tab
3. Click on the latest workflow run
4. Look for error messages in the logs

## Testing Locally

Test the bot with mock data:

```bash
python test_bot_fixes.py
```

## Need Help?

1. Run diagnostics first: `python bot.py --diagnose`
2. Check GitHub Actions logs
3. Verify all API keys are set correctly
4. Make sure the repository secrets match the required names exactly

The diagnostic tools will tell you exactly what's wrong and how to fix it!