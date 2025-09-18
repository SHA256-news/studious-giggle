# Bitcoin Mining News Twitter Bot

This bot automatically tweets about the latest Bitcoin mining news every 15 minutes. It creates a thread for each article with:
1. First tweet: A catchy headline and summary
2. Second tweet: A link to the full article

## Features

- Automatically fetches news about Bitcoin mining from EventRegistry (NewsAPI.ai)
- Posts tweets with catchy prefixes like "BREAKING:" or "JUST IN:"
- Creates tweet threads with the article link
- Runs every 15 minutes via GitHub Actions
- Tracks posted articles to avoid duplicates
- **Smart rate limiting handling** with exponential backoff retry logic
- **Improved error reporting** to distinguish between different failure types

## How It Works

1. The bot runs every 15 minutes via GitHub Actions
2. It connects to EventRegistry API to find new articles about Bitcoin mining
3. It filters out articles that have already been posted
4. For each new article, it creates a tweet thread:
   - First tweet: Catchy headline and summary
   - Second tweet: Link to the full article
5. It updates the tracking file to avoid posting duplicates

## Rate Limiting & Error Handling

The bot includes robust handling for Twitter API rate limits:

- **Exponential backoff retry**: Automatically retries failed tweets with increasing delays (1min, 2min, 4min)
- **1-hour automation cooldown**: If rate limiting persists after all retries, the bot prevents automation runs for 1 hour
- **Graceful degradation**: If the second tweet (with link) fails, the first tweet is still considered successful
- **Clear logging**: Distinguishes between "no new articles" and "rate limited" scenarios
- **Smart reporting**: Provides detailed information about why posting succeeded or failed

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
- Message: "Rate limit cooldown active. Skipping run. X minutes remaining."

**Solution:**
- The bot automatically retries with exponential backoff during a single run
- If rate limiting persists, the bot sets a 1-hour cooldown to prevent further automation runs
- Wait for the cooldown period to end (up to 1 hour) before the bot resumes normal operation

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
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `EVENTREGISTRY_API_KEY`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
