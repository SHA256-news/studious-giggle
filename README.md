# Bitcoin Mining News Twitter Bot

This bot automatically tweets about the latest Bitcoin mining news every 90 minutes.

## Features

- Automatically fetches news about Bitcoin mining from EventRegistry (NewsAPI.ai)
- Posts tweets with catchy prefixes like "BREAKING:" or "JUST IN:"
- **AI-Enhanced Headlines**: Uses Google Gemini AI to generate engaging tweet headlines (when configured)
- Runs every 90 minutes via GitHub Actions
- Tracks posted articles to avoid duplicates
- **Smart rate limiting handling** with exponential backoff retry logic
- **Improved error reporting** to distinguish between different failure types

## Preview Next Tweet

To see what the next tweet will look like before it's posted:

```bash
python show_next_tweet.py
```

This shows:
- The exact tweet text that will be posted
- Character count and formatting
- Whether it will be posted as a thread (2 tweets)
- Article source and URL
- Timing information

Other preview options:
- `python show_queue_simple.py` - Simple list of queued tweets
- `python show_queued_tweets.py` - Detailed queue analysis with metrics

## How It Works

1. The bot runs every 90 minutes via GitHub Actions
2. It connects to EventRegistry API to find new articles about Bitcoin mining
3. It filters out articles that have already been posted
4. For each new article, it:
   - Generates an engaging tweet headline using Google Gemini AI (if configured)
   - Posts the tweet to Twitter/X
5. It updates the tracking file to avoid posting duplicates


## Rate Limiting & Error Handling

The bot includes robust handling for Twitter API daily rate limits with multiple layers of protection:

- **Conservative scheduling**: Runs every 90 minutes (16 times max per day) to stay under limits
- **Minimum interval enforcement**: Runtime check prevents runs within 90 minutes of the last successful execution
- **Simplified cooldowns**: 2h → 4h cooldowns when rate limited (simplified from complex progressive system)
- **Single retry policy**: Uses 1 retry with 5-minute delay to conserve daily quota
- **Clear logging**: Distinguishes between "no new articles" and "rate limited" scenarios
- **Smart reporting**: Provides detailed information about why posting succeeded or failed
- **Precise timing**: `last_run_time` only updates after successful bot completion (bug fixed Sep 2024)

## Troubleshooting

### Why No Tweets Were Posted?

If the bot runs but doesn't post any tweets, here are the most common causes and solutions:

#### 1. Missing API Keys (Most Common)
**Symptoms:**
- Error: "Missing required environment variables"
- Error: "User is not logged in. Unable to execute the request"

**Solution:**
1. Go to your GitHub repository settings
2. Navigate to **Settings > Secrets and variables > Actions**
3. Add all required repository secrets:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `EVENTREGISTRY_API_KEY`

**Quick Diagnosis:**
```bash
python bot.py --diagnose
```

#### 2. All Articles Already Posted
**Symptoms:**
- Message: "No new articles to post (all articles were already posted)"

**Explanation:**
This is normal behavior! The bot only posts each article once and tracks what's been posted in `posted_articles.json`.

#### 3. No Recent Articles Found
**Symptoms:**
- Message: "No articles found from EventRegistry"

**Possible Causes:**
- No Bitcoin mining articles in the last 24 hours
- EventRegistry API issues
- Invalid EventRegistry API key

#### 4. Rate Limiting
**Symptoms:**
- Message: "Found X new articles but couldn't post any due to rate limiting"
- Error: "429 Too Many Requests"
- Message: "Rate limit cooldown active. Skipping run. X hours Y minutes remaining."

**Solution:**
- The bot automatically handles Twitter's 17 requests per 24 hours limit
- Uses simplified cooldowns (2h → 4h) when rate limited (fixed Sep 2024)
- Enforces minimum 90-minute intervals between successful runs
- Runs every 90 minutes maximum to stay within daily limits
- Wait for the cooldown period to end before the bot resumes normal operation
- Rate limits reset every 24 hours automatically

#### 5. Twitter API Issues
**Symptoms:**
- Errors during tweet posting
- Authentication failures

**Solution:**
- Verify Twitter API keys are correct
- Check if Twitter account is in good standing
- Ensure API access level supports posting tweets

### Diagnostic Tools

Run the built-in diagnostic tool to identify issues:

```bash
# Quick diagnosis
python bot.py --diagnose

# Or run the dedicated diagnostic script
python diagnose_bot.py
```

### "No new articles to post" vs Rate Limiting

If the bot shows different messages in the logs:

- `"No new articles to post (all articles were already posted)"` - All found articles have been posted before
- `"Found X new articles but couldn't post any due to rate limiting or other errors"` - New articles found but posting failed due to API limits
- `"Successfully posted X new articles"` - Normal successful operation

### Manual Trigger Issues

If a manual workflow trigger doesn't post anything, check the logs for:
- Rate limiting messages (`429 Too Many Requests`)
- Article fetching issues (`No articles found from EventRegistry`)
- API authentication problems

## API Keys and Secrets

The bot requires the following API keys set as GitHub repository secrets:

### Required Keys
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token
- `TWITTER_ACCESS_TOKEN_SECRET` - Twitter access token secret
- `EVENTREGISTRY_API_KEY` - EventRegistry/NewsAPI.ai API key

### Optional Keys
- `GEMINI_API_KEY` - Google Gemini AI API key (for enhanced tweet headlines)

### How to Get API Keys

#### Twitter API Keys
1. Go to https://developer.twitter.com/
2. Create a developer account and app
3. Generate API keys and access tokens

#### EventRegistry API Key
1. Go to https://newsapi.ai/dashboard
2. Sign up for an account
3. Get your API key from the dashboard

#### Google Gemini API Key
1. Go to https://ai.google.dev/
2. Sign up for Google AI Studio
3. Create an API key for Gemini

### Setting Up Repository Secrets
1. Go to your GitHub repository **Settings > Secrets and variables > Actions**
2. Add each API key as a new repository secret
3. Use the exact names listed above

## License

This project is licensed under the MIT License - see the LICENSE file for details.
