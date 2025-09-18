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

## How It Works

1. The bot runs every 15 minutes via GitHub Actions
2. It connects to EventRegistry API to find new articles about Bitcoin mining
3. It filters out articles that have already been posted
4. For each new article, it creates a tweet thread:
   - First tweet: Catchy headline and summary
   - Second tweet: Link to the full article
5. It updates the tracking file to avoid posting duplicates

## API Keys and Secrets

The bot requires the following API keys set as GitHub repository secrets:
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `EVENTREGISTRY_API_KEY`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
