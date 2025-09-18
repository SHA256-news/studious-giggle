# Twitter API Rate Limits and Authentication

## Overview

This document outlines the Twitter API rate limits and authentication requirements for the Bitcoin Mining News Bot.

## Rate Limits

### Current Twitter API Limits
- **Posting Tweets**: 17 requests per 24 hours
- **Reading/Fetching**: Higher limits (not typically an issue for this bot)

### Bot Posting Strategy
Given the 17 requests per 24 hours limit, the bot implements the following strategy:

1. **Scheduled Runs**: Bot runs every 90 minutes (16 times per day maximum)
2. **Conservative Posting**: Only posts 1 article per successful run
3. **Rate Limit Handling**: Implements progressive cooldown periods
4. **Daily Reset**: Rate limits reset every 24 hours

### Cooldown Periods

When rate limits are hit, the bot implements escalating cooldown periods:

1. **First Rate Limit Hit**: 2-hour cooldown
2. **Subsequent Hits**: 4-hour cooldown  
3. **Repeated Violations**: 8-hour cooldown
4. **Emergency Backup**: 24-hour cooldown for persistent issues

This ensures the bot stays well within the 17 requests per 24 hours limit.

## Authentication Requirements

### Required Environment Variables
The bot requires the following Twitter API credentials:

- `TWITTER_API_KEY`: Your app's API key
- `TWITTER_API_SECRET`: Your app's API secret key  
- `TWITTER_ACCESS_TOKEN`: User access token
- `TWITTER_ACCESS_TOKEN_SECRET`: User access token secret

### Twitter API Access Level
This bot requires **OAuth 1.0a** with **Read and Write** permissions to:
- Create tweets
- Post threaded content (replies)

### EventRegistry API
Additionally requires:
- `EVENTREGISTRY_API_KEY`: For fetching Bitcoin mining news articles

## Best Practices

### Rate Limit Management
1. **Monitor Usage**: Keep track of API calls per 24-hour period
2. **Graceful Degradation**: Continue operating even when rate limited
3. **User Communication**: Clear logging about rate limit status
4. **Backup Strategy**: Extended cooldowns prevent hitting limits repeatedly

### Error Handling
1. **Retry Logic**: Exponential backoff for temporary failures
2. **Rate Limit Detection**: Proper handling of 429 responses
3. **Fallback Behavior**: Skip posting rather than fail completely
4. **Logging**: Detailed logs for troubleshooting

## Monitoring

### Key Metrics to Track
- Posts per 24-hour period
- Rate limit hits per day
- Successful vs failed posting attempts
- Cooldown activation frequency

### Warning Signs
- More than 15 posts in 24 hours (approaching limit)
- Frequent rate limit cooldowns
- Multiple consecutive posting failures

## Troubleshooting

### Common Issues
1. **"Rate limit exceeded"**: Normal behavior, wait for cooldown
2. **"Authentication failed"**: Check API credentials
3. **"No new articles posted"**: May be due to rate limiting or no new content

### Recovery Procedures
1. **Rate Limited**: Wait for automatic cooldown to expire
2. **Auth Issues**: Verify all 4 Twitter API credentials
3. **Persistent Failures**: Check Twitter API status and limits

## Implementation Notes

The bot automatically adjusts its behavior based on rate limit responses from the Twitter API. Manual intervention is typically not required, as the bot is designed to operate within limits and recover automatically.

For emergency manual intervention, the rate limit cooldown can be cleared by deleting the `rate_limit_cooldown.json` file, but this should only be done if you're certain the 24-hour rate limit window has reset.