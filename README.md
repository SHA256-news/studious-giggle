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
- **Graceful degradation**: If the second tweet (with link) fails, the first tweet is still considered successful
- **Clear logging**: Distinguishes between "no new articles" and "rate limited" scenarios
- **Smart reporting**: Provides detailed information about why posting succeeded or failed

## Troubleshooting

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
